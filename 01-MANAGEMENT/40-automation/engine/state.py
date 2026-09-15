from datetime import datetime, timedelta

def get_rule_state(conn, rule_name):
    with conn.cursor() as cur:
        cur.execute("SELECT is_active, last_fired_at, last_value "
                    "FROM automation_state WHERE rule_name = %s", (rule_name,))
        row = cur.fetchone()
        if row is None:
            return {"is_active": False, "last_fired_at": None, "last_value": None}
        return {"is_active": row[0], "last_fired_at": row[1], "last_value": row[2]}

def set_rule_state(conn, rule_name, is_active, value, fired=False):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO automation_state
              (rule_name, is_active, last_fired_at, last_value, updated_at)
            VALUES (%s, %s, CASE WHEN %s THEN now() ELSE NULL END, %s, now())
            ON CONFLICT (rule_name) DO UPDATE
              SET is_active = EXCLUDED.is_active,
                  last_fired_at = CASE WHEN EXCLUDED.is_active
                                       THEN now() ELSE automation_state.last_fired_at END,
                  last_value = EXCLUDED.last_value,
                  updated_at = now()
        """, (rule_name, is_active, fired, value))

def is_in_cooldown(state_row, cooldown_seconds):
    if cooldown_seconds <= 0 or state_row["last_fired_at"] is None:
        return False
    age = datetime.now(state_row["last_fired_at"].tzinfo) - state_row["last_fired_at"]
    return age < timedelta(seconds=cooldown_seconds)
