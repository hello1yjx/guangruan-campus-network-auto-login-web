# Campus Network Auto Login Web

This project uses Python, Playwright, and Tesseract OCR to automate a campus network web login flow.

## Features

- open the campus login page automatically
- fill in username and password
- recognize the captcha image and try to submit the form
- retry when the network is down
- support background monitoring
- support startup mode
- skip login when a proxy is enabled
- skip login when the campus login page is not reachable

## Files

- `main.py`: entry point
- `config.example.json`: public example config
- `campus_net_auto_login/login.py`: login workflow
- `campus_net_auto_login/connectivity.py`: connectivity checks
- `campus_net_auto_login/captcha_ocr.py`: captcha OCR
- `run_login.bat`: one-time login
- `run_monitor_background.vbs`: background monitor
- `run_monitor_startup.vbs`: startup monitor
- `status_monitor.bat`: check background status
- `stop_monitor.bat`: stop background monitor
- `install_startup.bat`: install Windows startup shortcut
- `uninstall_startup.bat`: remove Windows startup shortcut

## Setup

1. Install Python dependencies:

```powershell
D:\python\python.exe -m pip install -r requirements.txt
```

2. Install Tesseract OCR.

Common Windows path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

3. Copy `config.example.json` to `config.json` and fill in your own:

- campus login URL
- username
- password
- browser path if needed
- selectors if your login page differs

## Run

One-time login:

```powershell
D:\python\python.exe main.py
```

Continuous monitor:

```powershell
D:\python\python.exe main.py --monitor
```

Startup mode:

```powershell
D:\python\python.exe main.py --startup-monitor
```

## Scripts

- `run_login.bat`: login once
- `run_monitor_background.vbs`: start the monitor in the background
- `run_monitor_startup.vbs`: try one login first, then keep monitoring
- `status_monitor.bat`: show whether the background monitor is running
- `stop_monitor.bat`: stop the background monitor
- `install_startup.bat`: add startup shortcut to Windows Startup
- `uninstall_startup.bat`: remove startup shortcut

## Config

Do not publish your real `config.json`.

Recommended to publish:

- `config.example.json`

Do not publish:

- `config.json`
- `runtime/`
- real username and password
- real campus login URL
- `wlanacip`
- `wlanuserip`

## Monitor Settings

- `check_interval_seconds`: how often to check the network
- `offline_threshold`: how many failed checks before relogin starts
- `post_login_wait_seconds`: wait time after a successful relogin
- `startup_initial_delay_seconds`: wait time before the first startup login attempt
- `request_timeout_seconds`: timeout for connectivity checks
- `connectivity_check_url`: URL used to test whether the network is online
- `skip_login_when_proxy_enabled`: skip login while a proxy is enabled
- `only_login_when_campus_page_reachable`: only try login when the campus login page is reachable

## Notes

- Different schools and network areas may use different login URLs and parameters.
- Captcha OCR may still need tuning depending on the actual portal.
- If the page structure differs, update the selectors in your config.
