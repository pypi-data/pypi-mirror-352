import json
import os

CONFIG_DIR = os.path.expanduser("~/.escli")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")


def save_config(domain: str, token: str):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump({"domain": domain, "token": token}, f)


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH) as f:
        return json.load(f)
