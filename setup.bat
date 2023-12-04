@echo off
chcp 65001

>nul 2>&1 "%SYSTEMROOT%\System32\cacls.exe" "%SYSTEMROOT%\System32\config\system"

if %errorlevel% NEQ 0 (
    color 0c
    echo "Please run the script as an administrator."
    pause
    exit /b 1
)

set /p MoBuVersion=Input MotionBuilder Version (ex. 2024): 
SET MobupyPath="C:\Program Files\Autodesk\MotionBuilder %MoBuVersion%\bin\x64\mobupy.exe"

if not exist %MobupyPath% (
    color 0c
    echo "MotionBuilder %MoBuVersion% is not installed."
    pause
    exit /b 1
)
echo "install python packages..."

SET REQUIREMENTS=%~dp0\requirements.txt
%MobupyPath% -m pip install -r %REQUIREMENTS%

pause
