import sys
sys.path.insert(0, ".")
from engine.rule_loader import load_rules
for r in load_rules("rules"):
    print(f"{r.name:25} sev={r.severity:8} trigger={r.trigger['type']:5} cooldown={r.cooldown_seconds}")
