import urllib.request
import urllib.error

def run_http_trigger(trigger_config, rule, conn, state):
    url = trigger_config["url"]
    timeout = trigger_config.get("timeout_seconds", 10)
    threshold = trigger_config.get("consecutive_failures", 1)
    current = state.get(rule.name, {}).get("consecutive_failures", 0)
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ok = 200 <= resp.status < 300
            detail = f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        ok, detail = False, f"HTTP {e.code}"
    except Exception as e:
        ok, detail = False, str(e)
    if ok:
        state.setdefault(rule.name, {})["consecutive_failures"] = 0
        return False, 0, detail
    current += 1
    state.setdefault(rule.name, {})["consecutive_failures"] = current
    return current >= threshold, current, detail
