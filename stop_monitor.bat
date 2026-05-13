@echo off
cd /d "%~dp0"

if not exist "runtime\monitor.pid" (
  echo monitor.pid not found.
  echo The background monitor may not be running.
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
  echo Process %MONITOR_PID% is not running.
  if exist "runtime\monitor.pid" del /f /q "runtime\monitor.pid" >nul 2>nul
  pause
  exit /b 1
)

taskkill /PID %MONITOR_PID% /F
if exist "runtime\monitor.pid" del /f /q "runtime\monitor.pid" >nul 2>nul
echo Background monitor stopped.
pause
