@echo off
setlocal

echo Deactivating any active Conda environments...
call conda deactivate 2>nul

echo Removing Conda environment...
rmdir /s /q "%cd%\installer_files\env"
if %errorlevel% neq 0 echo Failed to remove Conda environment. & goto :error

echo Removing Miniconda installation...
rmdir /s /q "%cd%\installer_files\conda"
if %errorlevel% neq 0 echo Failed to remove Miniconda installation. & goto :error

echo Removing installer files...
rmdir /s /q "%cd%\installer_files"
if %errorlevel% neq 0 echo Failed to remove installer files. & goto :error

echo Cleanup completed successfully.
goto :end

:error
echo An error occurred during the cleanup process.

:end
pause