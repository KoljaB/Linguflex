@echo off
set PYTHON_EXE=python.exe

cd /d %~dp0

set LOGFILE=%~dp0log_install_shell.txt

echo Creating VENV
echo Creating VENV >> %LOGFILE%
%PYTHON_EXE% -m venv test_env >> %LOGFILE% 2>&1

:: Activate the virtual environment
echo Activating VENV
echo Activating VENV >> %LOGFILE%
call test_env\Scripts\activate.bat >> %LOGFILE% 2>&1

echo Upgrading PIP
echo Upgrading PIP >> %LOGFILE%
test_env\Scripts\python -m pip install --upgrade pip >> %LOGFILE% 2>&1

echo Starting windows installation script
echo Starting windows installation script >> %LOGFILE%

python install_win.py

cmd