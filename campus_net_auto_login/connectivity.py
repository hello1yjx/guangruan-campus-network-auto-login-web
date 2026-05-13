from __future__ import annotations

import os
from typing import Any
from urllib.error import URLError
from urllib.request import Request, getproxies, urlopen


PROXY_ENV_KEYS = [
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
]


def _build_request(url: str, user_agent: str) -> Request:
    return Request(url, headers={"User-Agent": user_agent})


def is_online(config: dict[str, Any]) -> bool:
    monitor_config = config.get("monitor", {})
    check_url = monitor_config.get("connectivity_check_url", "https://www.baidu.com")
    timeout = float(monitor_config.get("request_timeout_seconds", 5))
    user_agent = monitor_config.get(
        "user_agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CampusNetAutoLogin/1.0",
    )

    request = _build_request(check_url, user_agent)
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 400
    except (URLError, TimeoutError, ValueError):
        return False


def is_campus_login_reachable(config: dict[str, Any]) -> bool:
    monitor_config = config.get("monitor", {})
    timeout = float(monitor_config.get("request_timeout_seconds", 5))
    user_agent = monitor_config.get(
        "user_agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CampusNetAutoLogin/1.0",
    )
    login_url = str(config.get("login_url", "")).strip()
    if not login_url:
        return False

    request = _build_request(login_url, user_agent)
    try:
        with urlopen(request, timeout=timeout) as response:
            return 200 <= getattr(response, "status", 200) < 500
    except (URLError, TimeoutError, ValueError):
        return False


def is_proxy_enabled(config: dict[str, Any]) -> bool:
    monitor_config = config.get("monitor", {})
    if not bool(monitor_config.get("skip_login_when_proxy_enabled", True)):
        return False

    for key in PROXY_ENV_KEYS:
        value = os.environ.get(key, "").strip()
        if value:
            return True

    system_proxies = getproxies()
    return any(str(value).strip() for value in system_proxies.values())
