@echo off
setlocal
cd /d "%~dp0"
set "PROJECT_DIR=%CD%"

del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\CampusNetworkAutoLogin.lnk" 2>nul
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\CampusNetworkAutoLogin.vbs" 2>nul

powershell -NoProfile -ExecutionPolicy Bypass ^
  -Command "$projectDir = [System.IO.Path]::GetFullPath($env:PROJECT_DIR); $startup = [Environment]::GetFolderPath('Startup'); $shell = New-Object -ComObject WScript.Shell; $shortcut = $shell.CreateShortcut((Join-Path $startup 'CampusNetworkAutoLogin.lnk')); $shortcut.TargetPath = Join-Path $env:SystemRoot 'System32\wscript.exe'; $shortcut.Arguments = ('\"{0}\"' -f (Join-Path $projectDir 'run_monitor_startup.vbs')); $shortcut.WorkingDirectory = $projectDir; $shortcut.IconLocation = (Join-Path $env:SystemRoot 'System32\shell32.dll') + ',25'; $shortcut.Save()"

if errorlevel 1 (
  echo Failed to install startup shortcut.
  pause
  exit /b 1
)

echo Startup shortcut installed.
pause
