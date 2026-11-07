@echo off
setlocal
cd /d "%~dp0"
title Editorial Studio
if /I "%~1"=="--check" goto check_only
if not "%~1"=="" goto usage
if exist ".venv\Scripts\python.exe" goto install_deps
if exist ".venv" goto old_environment
where py >nul 2>nul
if errorlevel 1 goto fallback_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 goto fallback_python
py -3 -m venv .venv
if errorlevel 1 goto failed
goto install_deps
:fallback_python
where python >nul 2>nul
if errorlevel 1 goto missing_python
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 goto missing_python
python -m venv .venv
if errorlevel 1 goto failed
:install_deps
".venv\Scripts\python.exe" -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 goto old_environment
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto failed
".venv\Scripts\python.exe" -B scripts\check_installation.py
if errorlevel 1 goto failed
".venv\Scripts\python.exe" studio.py serve
if errorlevel 1 goto failed
exit /b 0
:check_only
if exist ".venv\Scripts\python.exe" goto check_venv
if exist ".venv" goto invalid_environment_check
where py >nul 2>nul
if errorlevel 1 goto check_python
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if not errorlevel 1 goto check_py
:check_python
where python >nul 2>nul
if errorlevel 1 goto missing_python_check
python -c "import sys; sys.exit(0 if sys.version_info >= (3, 11) else 1)" >nul 2>nul
if errorlevel 1 goto missing_python_check
python -B scripts\check_installation.py
exit /b %errorlevel%
:check_venv
".venv\Scripts\python.exe" -B scripts\check_installation.py
exit /b %errorlevel%
:check_py
py -3 -B scripts\check_installation.py
exit /b %errorlevel%
:missing_python_check
echo Install Python 3.11 or newer from https://www.python.org/downloads/
exit /b 1
:invalid_environment_check
echo The existing .venv is incomplete or broken. It was not replaced.
echo Follow docs\LOCAL_INSTALLATION.md to rebuild only the environment.
exit /b 1
:old_environment
echo The existing .venv is incomplete, broken or cannot run Python 3.11 or newer. It was not replaced.
echo Install a supported Python, then follow docs\LOCAL_INSTALLATION.md to rebuild only the environment.
goto failed
:usage
echo Usage: run_windows.cmd [--check]
exit /b 2
:missing_python
echo Install Python 3.11 or newer from https://www.python.org/downloads/
:failed
echo Editorial Studio could not start. Read the error message above.
pause
exit /b 1
