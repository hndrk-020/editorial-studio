@echo off
setlocal
set "SOURCE=%~dp0.agents\skills\editorial-studio"
set "DEST=%USERPROFILE%\.agents\skills\editorial-studio"
if not exist "%SOURCE%\SKILL.md" (
  echo Could not find the Editorial Studio skill in this package.
  pause
  exit /b 1
)
if not exist "%USERPROFILE%\.agents\skills" mkdir "%USERPROFILE%\.agents\skills"
if exist "%DEST%\SKILL.md" (
  echo An Editorial Studio skill is already installed at:
  echo %DEST%
  choice /C YN /M "Replace the existing local skill"
  if errorlevel 2 exit /b 0
)
xcopy "%SOURCE%" "%DEST%" /E /I /Y >nul
if errorlevel 1 (
  echo Skill copy failed. Open the folder in Codex instead.
  pause
  exit /b 1
)
echo.
echo Skill installed in: %DEST%
echo Open or restart Codex and invoke $editorial-studio.
echo.
pause
exit /b 0
