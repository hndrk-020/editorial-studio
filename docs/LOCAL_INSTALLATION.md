# From installation to your first PDF

Editorial Studio has two parts. **The skill teaches your AI tool the editorial workflow. The local application provides this project's dashboard and PDF renderer.** Installing the skill alone does not install Python or the application.

You need your own access to a supported AI tool; its subscriptions and usage limits are separate. The source is publicly readable at [hndrk-020/editorial-studio](https://github.com/hndrk-020/editorial-studio). No repository invitation, GitHub token or administrator access is required to copy the skill.

## 1. Install the skill and verify discovery

Choose **one** of these routes. Keep an existing working installation until you have deliberately chosen to update it.

### Inside Codex

Paste this into Codex:

```text
$skill-installer install https://github.com/hndrk-020/editorial-studio/tree/main/.agents/skills/editorial-studio
```

The bundled installer normally targets `$CODEX_HOME/skills`, defaulting to `~/.codex/skills`. It refuses to overwrite an existing destination. If it reports one, retain that copy or back it up outside active skill directories before a deliberate update. For a private fork, authenticate local Git or use a supported GitHub token; browser login alone may not authenticate Git.

Start a new turn; restart Codex if discovery has not refreshed. Invoke `$editorial-studio` and send:

```text
$editorial-studio Confirm you can load the skill and its editorial planning and brand system references. Tell me the loaded SKILL.md path. Do not start a publication yet.
```

Confirm the reported path is the installation you intended. A successful file copy is not proof that the AI tool loaded that copy.

### Windows source installer

1. Open the [repository](https://github.com/hndrk-020/editorial-studio), select **Code → Download ZIP**, then use **Extract All**. This downloads the current branch; an older release ZIP may lack recent fixes. A 404 means you should check the URL and branch.
2. Open the extracted `editorial-studio-main` folder. Confirm `install_codex_skill_windows.cmd` and `.agents/skills/editorial-studio/SKILL.md` exist. Do not run from inside a ZIP preview.
3. Double-click `install_codex_skill_windows.cmd`. It copies the nine skill files to `%USERPROFILE%\.agents\skills\editorial-studio`. Python, Git and Node are not needed for this operation.
4. If **any destination folder already exists**, the installer asks before updating. Back up local edits before selecting Y. An update overlays matching files and retains extra files; it is not an atomic replacement. An incomplete source is rejected before copying.
5. Wait for **Skill installed in** and press a key. Then use the Codex discovery prompt above.

For a check that changes no files, open PowerShell in the extracted folder:

```powershell
.\install_codex_skill_windows.cmd --check
```

This compares the nine distributed files with the source, including every reference. It returns a nonzero exit code for missing or changed files; intentional local edits can cause this result. It does not remove extra files or verify Codex discovery.

### Other AI tools

The [showcase](https://magazine.10myth.com) includes setup prompts for Claude Code, Grok **Build**, Cursor and Gemini CLI. Their documented skill locations differ. These are not instructions for consumer Grok chat. Keep all references with `SKILL.md`, use that tool's skill refresh/discovery command, and request the exact loaded path. These routes have not been runtime-tested here.

## 2. Set up the local PDF application

Complete this step for this project's dashboard or renderer. It is separate from skill installation.

1. Keep the **full extracted repository** in a stable folder you control. A skill-only directory cannot run the dashboard. Existing users should keep their current checkout, `projects/`, `output/` and local settings; do not replace that whole folder with a fresh ZIP.
2. Install [Python 3.11 or newer](https://www.python.org/downloads/). On Windows, enable its launcher/PATH option. Close and reopen the terminal after installation.
3. Start the platform launcher from the repository.

   Windows: double-click `run_windows.cmd`.

   macOS/Linux:

   ```bash
   chmod +x run_mac_linux.sh
   ./run_mac_linux.sh
   ```

   The launcher checks the Python version, creates `.venv` if absent, installs the hash-locked dependencies, checks the application files, and starts the dashboard. Initial dependency installation needs internet. Normal starts let pip check those locked dependencies again. It does not install or replace your AI tool.
4. Open **http://127.0.0.1:8765** if the browser does not open automatically. Keep the terminal running. **Ctrl+C** stops the server. Keep this single-user app on localhost; do not expose it through a public tunnel.
5. For future readiness checks, run one of these from the repository. `--check` does **not** install dependencies, create a virtual environment or start a server:

   ```powershell
   .\run_windows.cmd --check
   ```

   ```bash
   ./run_mac_linux.sh --check
   ```

The diagnostic reports the Python executable/version, application files, linked skill references and installed dependency versions. A `FIX` result identifies missing prerequisites. Checks do not prove a finished PDF or AI-tool discovery.

To check a specific installed skill with an available Python, without requiring the PDF runtime:

```powershell
.\.venv\Scripts\python.exe -B scripts\check_installation.py --skill "$env:USERPROFILE\.agents\skills\editorial-studio" --skill-only
```

Replace the path with the one your AI tool actually loaded. The diagnostic never reads your publications or settings.

## 3. Make your first publication

Open the full repository as your AI tool's workspace so the app is available. A useful starting request is:

```text
$editorial-studio Create an English two-page introduction for my startup, for prospective customers. Use my real product photographs. Start with the purpose, audience and style; ask for an inspiration URL or no example, then show two creative directions. Verify the local PDF application before production.
```

This starts discovery; it does not guarantee a particular layout from the baseline renderer. Its magazine supports up to 12 feature pages, and its A4 portrait onepager supports up to 3 features. Custom layouts need a separate approved development phase.

Choose a direction, review the exact local images and crops, and retain source/rights evidence for the intended distribution. Downloaded images start unapproved. No final PDF is ready until preflight, PDF structure checks and visual review pass. The app runs locally; material you give an AI tool is handled under that provider's settings and terms.

## Existing installations and updates

The Windows installer uses `~/.agents/skills`; the bundled Codex installer normally uses `~/.codex/skills`. A project-local `.agents/skills` copy can also take precedence. Check these locations and ask Codex which `SKILL.md` it loads. Keep one intended user-wide copy; do not delete working copies to fix an unexplained picker issue.

Back up the entire existing skill outside active skill directories before updating. Preserve local edits and update the whole skill, including references. The Windows installer overlays files and keeps obsolete extras; the bundled installer refuses an existing destination.

Application updates and skill updates are separate. Preserve `projects/`, `output/`, approved assets and local settings. If an existing `.venv` is broken or uses old Python, stop the dashboard, move **only `.venv`** to a backup directory, then run the launcher with a supported Python. Do not move/delete publication folders. Rebuilding an environment needs internet for dependencies.

## Troubleshooting

| What you see | What to do |
|---|---|
| Missing skill/reference file | Extract the complete source ZIP. Do not copy just the installer or `SKILL.md`. |
| Skill absent or wrong loaded path | Refresh the AI tool, request the loaded path, and check for competing project/user copies. |
| `studio.py` missing | You have the skill only, or are in the wrong directory. Use the full repository for the PDF app. |
| Python opens Microsoft Store, or `py` is missing | Install Python 3.11+ from python.org with PATH/launcher enabled, then reopen the terminal. |
| Dependency missing/version differs | Run the platform launcher normally to install into its `.venv`; use that environment's Python. Do not change an unrelated project's environment. |
| Locked wheel unavailable | Read pip's error. Use a Python/platform with compatible wheels; retain hashes and avoid unreviewed source builds. CI covers Python 3.11/3.13 on Windows/Linux; macOS is not runtime-verified here. |
| Port 8765 in use | Close the previous server, or use `.venv`'s Python with `studio.py serve --port 8766`. |
| Export blocked | Resolve preflight's missing content, exact-image approval or rights evidence. Do not bypass those gates. |

Keep personal content outside source control: `projects/` and `output/` are Git-ignored. Installation never requires uploading personal guides/photos, and does not publish them or change repository visibility.

## Verification scope

The Windows source installer has been exercised in an isolated profile path containing spaces, and a fresh Codex process loaded the project-local skill and its references. This uses an existing machine and AI-tool login. It is **not** a clean-OS or unassisted first-time-user test. The public GitHub ZIP download/extraction route and the other four AI runtimes remain separately unverified in this local test. Do not infer all-platform compatibility from file checks.

Source: [Windows installer](https://github.com/hndrk-020/editorial-studio/blob/main/install_codex_skill_windows.cmd), [repository README](https://github.com/hndrk-020/editorial-studio/blob/main/README.md), and the bundled Codex Skill Installer behavior. Current Codex discovery is documented in [OpenAI skills](https://developers.openai.com/plugins/concepts/skills).
