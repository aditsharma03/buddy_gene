import json
import os
from typing import List

USERS_FILE = "users.json"


def read_users() -> List[dict]:
    """
    Read users from users.json
    """
    if not os.path.exists(USERS_FILE):
        return []

    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def write_users(users: List[dict]) -> None:
    """
    Write users to users.json
    """
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)
