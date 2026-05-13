@echo off
cd /d "%~dp0"

if not exist "runtime\monitor.pid" (
  echo Background monitor is not running.
  pause
  exit /b 1
)

set /p MONITOR_PID=<"runtime\monitor.pid"
if "%MONITOR_PID%"=="" (
  echo monitor.pid is empty.
  pause
  exit /b 1
)

tasklist /FI "PID eq %MONITOR_PID%" | find "%MONITOR_PID%" >nul
if errorlevel 1 (
  echo monitor.pid exists, but process %MONITOR_PID% is not running.
  pause
  exit /b 1
)

echo Background monitor is running.
echo PID: %MONITOR_PID%
if exist "runtime\monitor.log" (
  echo.
  echo Last log lines:
  powershell -NoProfile -Command "Get-Content -Path 'runtime\\monitor.log' -Tail 10"
)
pause
