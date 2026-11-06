# Install Editorial Studio locally on Windows

Use this guide with the private [hndrk-020/editorial-studio repository](https://github.com/hndrk-020/editorial-studio). You need repository read access. Choose one installation route.


1. Open Codex and sign in.
   Open GitHub in your browser and sign in as hndrk-020, or an account with read access to the private repository.

2. Download the source.
   Open https://github.com/hndrk-020/editorial-studio
   Select Code > Download ZIP. This downloads the current branch source; avoid an older release ZIP if you want the enhanced workflow.
   A 404 usually means you are signed into the wrong GitHub account or lack access.

3. Extract the ZIP completely.
   Right-click the downloaded ZIP > Extract All.
   Open the extracted editorial-studio-main folder. Confirm install_codex_skill_windows.cmd and .agents\skills\editorial-studio\SKILL.md exist.
   Do not run the installer from inside the ZIP preview.

4. Run the skill installer.
   Double-click install_codex_skill_windows.cmd.
   This copies the complete skill and reference files to:
   %USERPROFILE%\.agents\skills\editorial-studio
   Administrator access, Python, Git and Node are not needed for this copy operation.
   If the destination already has SKILL.md, the installer asks whether to replace it. Back up any local edits before choosing Y.
   Wait for the “Skill installed in” message, then press a key to close the window.
   The script uses xcopy to overlay files; it does not remove obsolete destination files.

5. Verify the files in PowerShell.
   Run:
   Test-Path "$env:USERPROFILE\.agents\skills\editorial-studio\SKILL.md"
   Test-Path "$env:USERPROFILE\.agents\skills\editorial-studio\references\editorial_planning.md"
   Test-Path "$env:USERPROFILE\.agents\skills\editorial-studio\references\brand_system.md"
   All three should return True. These checks verify copied files, not Codex discovery.

6. Refresh Codex and test discovery.
   Start a new turn; restart Codex if the skill is not listed. Type $editorial-studio and select it if the skill picker appears.
   Send:
   $editorial-studio Confirm you can load the skill and its editorial planning and brand system references. Tell me the loaded SKILL.md path. Do not start a publication yet.
   Confirm the reported path is the installation you intended. This verifies loading rather than a file copy alone.

7. Start your first publication.
   Example:
   $editorial-studio Create a Dutch photography-led personal travel guide. Start with the purpose, audience and style, ask for an inspiration URL or no example, then show two creative directions before production.
   Expect the existing direction and exact-image approval gates, followed by editorial planning, design proofs and PDF quality checks.

## Alternative: install from inside Codex
Choose this route instead of the Windows installer, not in addition to it.
Paste into Codex:
$skill-installer install https://github.com/hndrk-020/editorial-studio/tree/main/.agents/skills/editorial-studio
The bundled installer normally targets $CODEX_HOME/skills, defaulting to ~/.codex/skills. Private-repository installation requires usable Git credentials or a supported GitHub token; browser or connector login alone may not authenticate local Git.
If it reports an existing destination, retain the current working installation or back it up before a deliberate update. The bundled installer refuses to overwrite an existing skill directory.
It should be available on the next turn; restart Codex if discovery has not refreshed.

## Existing installations and updates

The repository Windows installer targets `~/.agents/skills`. The bundled Codex Skill Installer defaults to `$CODEX_HOME/skills` (normally `~/.codex/skills`). Keep one intended user-wide copy. Check both locations and ask Codex which `SKILL.md` it loads; a project-local `.agents/skills` copy can also exist.

Back up the entire existing folder outside active skill directories before an update. Preserve local edits and install the whole skill folder, including references. The Windows installer overlays files rather than removing obsolete ones; the bundled installer refuses an existing destination. Do not delete working copies to fix an unexplained picker issue.

## Optional local dashboard and PDF application
Installing the skill provides instructions and references. The dashboard and its Python dependencies are separate.
If you also want the repository application:
- Keep the full extracted repository.
- Install Python 3.11+ with its launcher/PATH option.
- Double-click run_windows.cmd in the extracted repository.
- The launcher creates .venv, installs requirements.txt and starts the localhost application; first start needs internet.
- Open http://127.0.0.1:8765 if the browser does not open automatically. Keep its terminal running; Ctrl+C stops it.
- Skill-only installation does not guarantee that an arbitrary project already has a PDF runtime or the application files.

## Troubleshooting
- Missing SKILL.md: extract the full source ZIP; do not copy only the .cmd file.
- Skill absent: check the actual destination, refresh Codex, then request the loaded path. Check for competing project/user copies.
- Private clone authentication error: authenticate local Git separately, or use the browser ZIP route.
- Dashboard exits: read the terminal error; check Python and dependency installation.
- Preserve private publication data. Keep projects/ and output/ excluded from Git. Installation does not require uploading personal guides or photos.

## Verification scope

Repository metadata and installer behavior were inspected on 6 November 2026. These instructions are not evidence of a clean-machine installation test. Installing a skill does not change repository visibility or publish local projects.

## Sources
Verified repository installer:
https://github.com/hndrk-020/editorial-studio/blob/main/install_codex_skill_windows.cmd
Repository README:
https://github.com/hndrk-020/editorial-studio/blob/main/README.md
Official skill documentation:
https://learn.chatgpt.com/docs/build-skills
Bundled Skill Installer instructions were also checked locally.
