import json
import logging
from pathlib import Path
from typing import Union

import keyring


def read_from_json(file_path: Union[str, Path]):
    with open(file_path, "r") as f:
        data = json.load(f)
        return data


def get_logger():
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger()
    return logger


def save_credentials(domain: str, token: str):
    keyring.set_password("escli", "domain", domain)
    keyring.set_password("escli", "token", token)


def load_credentials():
    domain = keyring.get_password("escli", "domain")
    token = keyring.get_password("escli", "token")
    return domain, token
