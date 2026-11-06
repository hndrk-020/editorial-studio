@echo off
setlocal
cd /d "%~dp0"
title Editorial Studio
if exist ".venv\Scripts\python.exe" goto install_deps
where py >nul 2>nul
if errorlevel 1 goto fallback_python
py -3 -m venv .venv
if errorlevel 1 goto failed
goto install_deps
:fallback_python
where python >nul 2>nul
if errorlevel 1 goto missing_python
python -m venv .venv
if errorlevel 1 goto failed
:install_deps
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" studio.py serve
if errorlevel 1 goto failed
exit /b 0
:missing_python
echo Install Python 3.11 or newer from https://www.python.org/downloads/
:failed
echo Editorial Studio could not start. Read the error message above.
pause
exit /b 1
