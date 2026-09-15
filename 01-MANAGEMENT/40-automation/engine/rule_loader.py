import os
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class Rule:
    name: str
    description: str
    severity: str
    enabled: bool
    trigger: dict
    condition: dict = field(default_factory=dict)
    actions: list = field(default_factory=list)
    cooldown_seconds: int = 0

def load_rules(rules_dir: str = "rules") -> list:
    loaded = []
    for yaml_file in sorted(Path(rules_dir).glob("*.yaml")):
        raw = os.path.expandvars(yaml_file.read_text(encoding="utf-8"))
        data = yaml.safe_load(raw)
        if not data.get("enabled", True):
            continue
        loaded.append(Rule(
            name=data["name"],
            description=data.get("description", ""),
            severity=data.get("severity", "info"),
            enabled=True,
            trigger=data["trigger"],
            condition=data.get("condition", {}),
            actions=data.get("actions", []),
            cooldown_seconds=int(data.get("cooldown_seconds", 0)),
        ))
    return loaded
