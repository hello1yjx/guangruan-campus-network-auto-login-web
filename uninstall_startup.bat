@echo off
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\CampusNetworkAutoLogin.lnk" 2>nul
del /F /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\CampusNetworkAutoLogin.vbs" 2>nul
echo Startup item removed.
pause
