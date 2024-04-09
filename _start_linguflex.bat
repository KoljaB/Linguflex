@echo off
cd /d %~dp0
:: Activate the virtual environment
:: echo Activating VENV
:: echo Activating VENV >> %LOGFILE%
call test_env\Scripts\activate.bat

:: Start Linguflex 2.0
python -m lingu.core.run

:: Keep the command prompt open
cmd
