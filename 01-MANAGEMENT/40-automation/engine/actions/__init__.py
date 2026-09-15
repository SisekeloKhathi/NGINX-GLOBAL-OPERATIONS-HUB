from .log_event import action_log_event
from .webhook import action_webhook

ACTIONS = {"log_event": action_log_event, "webhook": action_webhook}

def run_action(action_config, rule, observed_value, threshold, conn):
    handler = ACTIONS.get(action_config.get("type"))
    if not handler:
        return "skipped", "unknown action"
    return handler(action_config, rule, observed_value, threshold, conn)
