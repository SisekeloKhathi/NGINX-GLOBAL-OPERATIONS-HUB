import json
import urllib.request
import urllib.error

def _render(template, rule, observed_value, threshold):
    return (str(template)
            .replace("{{ observed_value }}", str(observed_value))
            .replace("{{ threshold }}", str(threshold))
            .replace("{{ rule_name }}", rule.name)
            .replace("{{ severity }}", rule.severity))

def action_webhook(action_config, rule, observed_value, threshold, conn):
    url = action_config.get("url", "")
    if not url:
        return "skipped", "no WEBHOOK_URL"
    body = action_config.get("body", {"text": rule.description})
    body = {k: _render(v, rule, observed_value, threshold) for k, v in body.items()}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return "success", f"HTTP {resp.status}"
    except urllib.error.HTTPError as e:
        return "failed", f"HTTP {e.code}"
    except Exception as e:
        return "failed", str(e)
