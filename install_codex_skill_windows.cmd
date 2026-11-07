@echo off
setlocal DisableDelayedExpansion
set "SOURCE=%~dp0.agents\skills\editorial-studio"
set "DEST=%USERPROFILE%\.agents\skills\editorial-studio"
set "SKILL_FILES=SKILL.md agents\openai.yaml references\brand_system.md references\creative_brief.md references\editorial_planning.md references\image_research.md references\qa_release.md references\security_privacy.md references\style_directions.md"
if not defined USERPROFILE goto missing_profile
if not "%~1"=="" if /I not "%~1"=="--check" goto usage
for %%F in (%SKILL_FILES%) do if not exist "%SOURCE%\%%F" goto incomplete_source
if /I "%~1"=="--check" goto check_only
if exist "%DEST%" goto existing
goto copy_skill
:existing
echo An Editorial Studio folder already exists at:
echo "%DEST%"
echo This overlays matching files and retains extra files. Back up local edits first.
choice /C YN /M "Update this folder"
if errorlevel 2 goto cancelled
if not errorlevel 1 goto cancelled
:copy_skill
if not exist "%USERPROFILE%\.agents\skills" (
  mkdir "%USERPROFILE%\.agents\skills"
  if errorlevel 1 goto copy_failed
)
xcopy "%SOURCE%" "%DEST%" /E /I /Y >nul
if errorlevel 1 goto copy_failed
echo.
echo Skill installed in: "%DEST%"
echo Start a new Codex turn and invoke $editorial-studio. Restart if needed.
echo Ask Codex which SKILL.md it loads; another installed copy may take precedence.
echo The PDF application is separate. See docs\LOCAL_INSTALLATION.md.
echo.
pause
exit /b 0
:check_only
for %%F in (%SKILL_FILES%) do (
  if not exist "%DEST%\%%F" goto check_failed
  fc /b "%SOURCE%\%%F" "%DEST%\%%F" >nul 2>nul
  if errorlevel 1 goto check_failed
)
echo PASS: The nine distributed skill files match at "%DEST%".
echo Extra destination files are retained. Ask Codex to report the loaded SKILL.md path.
exit /b 0
:check_failed
echo The installed skill is missing files or differs from this source: "%DEST%"
echo No files were changed. Review local edits before updating.
exit /b 1
:cancelled
echo Cancelled. The existing skill was not changed.
exit /b 0
:incomplete_source
echo The source skill is incomplete. Extract the full repository before installing.
exit /b 1
:missing_profile
echo USERPROFILE is not set. Open this repository in Codex instead.
exit /b 1
:copy_failed
echo Skill copy failed. Review the destination before retrying.
pause
exit /b 1
:usage
echo Usage: install_codex_skill_windows.cmd [--check]
exit /b 2
