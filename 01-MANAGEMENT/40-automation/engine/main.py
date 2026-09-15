import os
import time
from datetime import datetime
import psycopg2
from dotenv import load_dotenv
from engine.rule_loader import load_rules
from engine.triggers import run_trigger
from engine.actions import run_action
from engine.state import get_rule_state, set_rule_state, is_in_cooldown

load_dotenv()

DB = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "database": os.getenv("DB_NAME", "ops_db"),
    "user": os.getenv("DB_USER", "admin"),
    "password": os.getenv("DB_PASSWORD"),
}
CYCLE_SECONDS = int(os.getenv("CYCLE_SECONDS", 60))

def write_event(conn, rule, value, threshold, action_taken, status, detail):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO automation_events
              (rule_name, severity, metric, observed_value, threshold,
               comparator, message, action_taken, action_status, action_detail)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (rule.name, rule.severity, rule.name, value, threshold,
              rule.condition.get("comparator", rule.trigger.get("type")),
              rule.description, action_taken, status, detail))

def cycle(http_state):
    conn = psycopg2.connect(**DB)
    try:
        for rule in load_rules("rules"):
            try:
                is_true, value, detail = run_trigger(rule.trigger, rule, conn, http_state)
            except Exception as e:
                print(f"[ERROR] {rule.name}: {e}")
                continue
            prev = get_rule_state(conn, rule.name)
            should_fire = is_true and not prev["is_active"]
            if should_fire and is_in_cooldown(prev, rule.cooldown_seconds):
                should_fire = False
            ts = datetime.now().strftime("%H:%M:%S")
            if should_fire:
                print(f"[{ts}] FIRE   {rule.name} value={value}")
                for action in rule.actions:
                    status, adetail = run_action(action, rule, value,
                                                 rule.condition.get("threshold"), conn)
                    write_event(conn, rule, value, rule.condition.get("threshold"),
                                action.get("type"), status, adetail)
                set_rule_state(conn, rule.name, is_true, value, fired=True)
            elif is_true:
                print(f"[{ts}] ACTIVE {rule.name} value={value}")
                set_rule_state(conn, rule.name, True, value)
            else:
                print(f"[{ts}] ok     {rule.name}")
                set_rule_state(conn, rule.name, False, value)
            conn.commit()
    finally:
        conn.close()

def main():
    print("Automation engine started")
    http_state = {}
    while True:
        try:
            cycle(http_state)
        except Exception as e:
            print(f"[ERROR] cycle: {e}")
        time.sleep(CYCLE_SECONDS)

if __name__ == "__main__":
    main()
