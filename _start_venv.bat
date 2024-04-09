@echo off
cd /d %~dp0
:: Activate the virtual environment
:: echo Activating VENV
:: echo Activating VENV >> %LOGFILE%
call test_env\Scripts\activate.bat

:: Keep the command prompt open
cmd
