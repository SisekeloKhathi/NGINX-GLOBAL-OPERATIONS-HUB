from .sql_trigger import run_sql_trigger
from .http_trigger import run_http_trigger

TRIGGERS = {"sql": run_sql_trigger, "http": run_http_trigger}

def run_trigger(trigger_config, rule, conn, state):
    handler = TRIGGERS.get(trigger_config.get("type"))
    if not handler:
        return False, None, "unknown trigger"
    return handler(trigger_config, rule, conn, state)
