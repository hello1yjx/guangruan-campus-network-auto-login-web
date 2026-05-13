from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from campus_net_auto_login.config import load_config
from campus_net_auto_login.connectivity import (
    is_campus_login_reachable,
    is_online,
    is_proxy_enabled,
)
from campus_net_auto_login.login import CampusNetworkLogin


RUNTIME_DIR = Path("runtime")
MONITOR_PID_PATH = RUNTIME_DIR / "monitor.pid"


def run_once(config: dict) -> bool:
    client = CampusNetworkLogin(config)
    return client.run()


def read_monitor_pid() -> int | None:
    if not MONITOR_PID_PATH.exists():
        return None

    try:
        return int(MONITOR_PID_PATH.read_text(encoding="utf-8").strip())
    except (OSError, ValueError):
        return None


def is_pid_running(pid: int) -> bool:
    if pid <= 0:
        return False

    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def is_monitor_running() -> bool:
    existing_pid = read_monitor_pid()
    if existing_pid is None:
        return False
    return is_pid_running(existing_pid)


def write_monitor_pid() -> None:
    RUNTIME_DIR.mkdir(exist_ok=True)
    MONITOR_PID_PATH.write_text(str(os.getpid()), encoding="utf-8")


def clear_monitor_pid() -> None:
    current_pid = read_monitor_pid()
    if current_pid == os.getpid() and MONITOR_PID_PATH.exists():
        MONITOR_PID_PATH.unlink()


def should_skip_login_for_proxy(config: dict, proxy_skip_logged: bool) -> tuple[bool, bool]:
    if is_proxy_enabled(config):
        if not proxy_skip_logged:
            print("Proxy detected. Skipping campus login for now.")
        return True, True

    if proxy_skip_logged:
        print("Proxy disabled. Resuming campus login monitoring.")
    return False, False


def should_skip_login_for_environment(config: dict, campus_skip_logged: bool) -> tuple[bool, bool]:
    monitor_config = config.get("monitor", {})
    if not bool(monitor_config.get("only_login_when_campus_page_reachable", True)):
        return False, False

    if not is_campus_login_reachable(config):
        if not campus_skip_logged:
            print("Campus login page is not reachable. Skipping campus login.")
        return True, True

    if campus_skip_logged:
        print("Campus login page is reachable again. Resuming campus login monitoring.")
    return False, False


def run_startup_login(config: dict) -> None:
    monitor_config = config.get("monitor", {})
    startup_delay_seconds = int(monitor_config.get("startup_initial_delay_seconds", 10))

    if startup_delay_seconds > 0:
        print(f"Startup mode: waiting {startup_delay_seconds} seconds before the first login attempt.")
        time.sleep(startup_delay_seconds)

    skip, _ = should_skip_login_for_proxy(config, False)
    if skip:
        return

    skip, _ = should_skip_login_for_environment(config, False)
    if skip:
        return

    if is_online(config):
        print("Startup mode: network is already available. Skipping the first login attempt.")
        return

    print("Startup mode: starting the first automatic login attempt.")
    success = run_once(config)
    if success:
        print("Startup mode: first automatic login succeeded.")
    else:
        print("Startup mode: first automatic login failed. Monitor mode will continue retrying later.")


def run_monitor(config: dict, startup_mode: bool = False) -> int:
    monitor_config = config.get("monitor", {})
    interval_seconds = int(monitor_config.get("check_interval_seconds", 60))
    offline_threshold = int(monitor_config.get("offline_threshold", 2))
    post_login_wait_seconds = int(monitor_config.get("post_login_wait_seconds", 10))
    consecutive_failures = 0
    proxy_skip_logged = False
    campus_skip_logged = False

    if is_monitor_running():
        print("Monitor is already running. This launch will exit.")
        return 0

    write_monitor_pid()
    print("Monitor mode started. Press Ctrl+C to stop.")

    try:
        if startup_mode:
            run_startup_login(config)

        while True:
            skip, proxy_skip_logged = should_skip_login_for_proxy(config, proxy_skip_logged)
            if skip:
                consecutive_failures = 0
                time.sleep(interval_seconds)
                continue

            skip, campus_skip_logged = should_skip_login_for_environment(config, campus_skip_logged)
            if skip:
                consecutive_failures = 0
                time.sleep(interval_seconds)
                continue

            if is_online(config):
                if consecutive_failures != 0:
                    print("Network is back online.")
                consecutive_failures = 0
            else:
                consecutive_failures += 1
                print(f"Network looks offline. Failure count: {consecutive_failures}.")

                if consecutive_failures >= offline_threshold:
                    print("Trying automatic re-login.")
                    success = run_once(config)
                    if success:
                        print("Automatic re-login succeeded.")
                        consecutive_failures = 0
                        time.sleep(post_login_wait_seconds)
                        continue
                    print("Automatic re-login failed. Will retry on the next cycle.")

            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("Monitor mode stopped.")
        return 0
    finally:
        clear_monitor_pid()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Campus network auto login script")
    parser.add_argument(
        "--monitor",
        action="store_true",
        help="Keep monitoring the network and reconnect automatically when needed.",
    )
    parser.add_argument(
        "--startup-monitor",
        action="store_true",
        help="Startup mode: try one login first, then keep monitoring.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = load_config("config.json")

    if args.startup_monitor:
        return run_monitor(config, startup_mode=True)

    if args.monitor:
        return run_monitor(config)

    success = run_once(config)
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
