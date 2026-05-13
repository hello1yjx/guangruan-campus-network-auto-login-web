from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_config(path: str | Path) -> dict[str, Any]:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Copy config.example.json to config.json and fill in your own settings first."
        )

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    required_keys = ["login_url", "username", "password", "selectors"]
    missing = [key for key in required_keys if not config.get(key)]
    if missing:
        raise ValueError(f"Missing required config fields: {', '.join(missing)}")

    return config
