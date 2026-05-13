# Guangruan Campus Network Auto Login Web

广州软件学院等类似校园网 Web 认证页面的自动登录脚本。  
A Python-based auto login tool for campus network web portals such as the Guangruan-style login page.

## Overview

这个项目使用 `Python + Playwright + Tesseract OCR` 自动完成校园网网页认证。  
It uses `Python + Playwright + Tesseract OCR` to automate campus network web login.

适合这类场景：

- 网页端登录
- 需要输入账号和密码
- 带图片验证码
- 掉线后希望自动重连

Typical use cases:

- web-based campus login
- username and password form
- image captcha
- automatic retry after disconnection

## Features

- 自动打开校园网登录页 / Open the campus login page automatically
- 自动填写账号密码 / Fill in username and password
- OCR 识别验证码并尝试提交 / Recognize captcha with OCR and submit
- 登录失败自动重试 / Retry when login fails
- 支持后台监控模式 / Support background monitor mode
- 支持开机启动后先登录再持续监控 / Support startup mode with initial login attempt
- 检测到代理时跳过认证 / Skip login when a proxy is enabled
- 检测不到校园网环境时跳过认证 / Skip login when the campus portal is not reachable

## Quick Start

1. 安装依赖 / Install dependencies

```powershell
D:\python\python.exe -m pip install -r requirements.txt
```

2. 安装 Tesseract OCR / Install Tesseract OCR

Windows 常见路径 / Common Windows path:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

3. 复制配置模板 / Copy the config template

将 `config.example.json` 复制为 `config.json`，再填写你自己的参数。  
Copy `config.example.json` to `config.json`, then fill in your own values.

你需要至少修改这些内容 / At minimum, update:

- `login_url`
- `username`
- `password`
- `ocr.tesseract_cmd`
- `selectors` if your portal structure is different

## Run

单次登录 / One-time login:

```powershell
D:\python\python.exe main.py
```

持续监控 / Continuous monitor:

```powershell
D:\python\python.exe main.py --monitor
```

开机模式：先尝试一次登录，再继续监控  
Startup mode: try one login first, then continue monitoring

```powershell
D:\python\python.exe main.py --startup-monitor
```

## Common Scripts

- `run_login.bat`: 单次登录 / login once
- `run_monitor.bat`: 前台监控 / monitor in a visible console
- `run_monitor_background.vbs`: 后台静默监控 / start monitor in background
- `run_monitor_startup.vbs`: 开机启动用后台脚本 / startup monitor script
- `status_monitor.bat`: 查看监控状态 / check monitor status
- `stop_monitor.bat`: 停止后台监控 / stop background monitor
- `install_startup.bat`: 安装开机自启 / install Windows startup shortcut
- `uninstall_startup.bat`: 移除开机自启 / remove Windows startup shortcut

## Configuration Notes

常见可调参数 / Common settings:

- `max_attempts`: 最大登录重试次数 / max login retries
- `page_timeout_seconds`: 页面等待超时 / page timeout
- `after_submit_wait_seconds`: 提交后等待秒数 / wait after submit
- `check_interval_seconds`: 监控检查间隔 / monitor interval
- `offline_threshold`: 连续离线多少次后触发重连 / offline threshold before relogin
- `post_login_wait_seconds`: 重连成功后等待秒数 / wait after relogin
- `startup_initial_delay_seconds`: 开机模式首次尝试前等待时间 / startup delay
- `skip_login_when_proxy_enabled`: 开代理时跳过登录 / skip login when proxy is enabled
- `only_login_when_campus_page_reachable`: 仅在校园网页面可达时尝试登录 / only login when portal is reachable

## Privacy And Safety

不要公开提交你的真实配置。  
Do not publish your real personal configuration.

建议公开的文件 / Safe to publish:

- `config.example.json`

不要公开的内容 / Do not publish:

- `config.json`
- `runtime/`
- 真实账号和密码 / real username and password
- 真实登录地址 / real login URL
- `wlanacip`
- `wlanuserip`

## Notes

- 不同学校的认证页结构可能不同，必要时请调整 `selectors`。  
  Different schools may use different portal structures, so `selectors` may need adjustment.
- 验证码识别成功率与页面样式有关，必要时可以继续优化 OCR 预处理。  
  Captcha OCR accuracy depends on the actual portal style and may need tuning.
- 批处理脚本中的 Python 路径目前按本机环境写死，如需分享给别人，建议改成通用路径或让用户自行修改。  
  The batch scripts currently use a machine-specific Python path and may need adjustment on other computers.
