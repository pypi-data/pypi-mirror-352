import yaml
import json
from typing import Any, Dict

class ConfigLoader:
    @staticmethod
    def load_yaml(path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return yaml.safe_load(f)

    @staticmethod
    def load_json(path: str) -> Dict[str, Any]:
        with open(path, 'r') as f:
            return json.load(f) 