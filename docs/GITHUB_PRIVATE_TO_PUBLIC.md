# GitHub release guide: private first, public only after review

Editorial Studio consists of **three separately installed elements**: a skill (`.agents/skills/editorial-studio`), a local dashboard (Python app), and a portable **skill-only plugin** (`plugins/editorial-studio`). Installing one does not automatically install the other two.

## 1. Create your private repository

On Windows, install Git for Windows and GitHub CLI (`gh`) if needed. Open a terminal in the extracted `Editorial_Studio_GitHub_Ready_v03` directory.

```powershell
gh auth login
python scripts/validate_repository.py
python -m unittest discover -s tests -v
git init
git branch -M main
git add .
git status --short
git commit -m "feat: editorial studio private beta 0.3"
gh repo create editorial-studio --private --source=. --remote=origin --push
```

`gh repo create` creates the repository under your authenticated GitHub account if no owner is specified. It also creates the `origin` remote and pushes the initial commit. Verify on GitHub that visibility is **Private** and that the committed files contain neither `projects/` nor `output/`. Do not run `gh repo create` twice.

The GitHub connector currently accessible in ChatGPT can work with files in existing repositories, but this chat does not have a confirmed permission/tool to create a new repository. The commands above are therefore a local user action, **not a completed GitHub push**.

## 2. Give colleagues access privately

On GitHub, open repository **Settings → Collaborators and teams**, add named collaborators, and assign the minimum necessary permissions. Prefer a protected `main` branch with pull requests and required CI.

In Codex, authorized collaborators can install the skill using the built-in installer, after GitHub authentication if the repository is private:

```text
$skill-installer install https://github.com/OWNER/editorial-studio/tree/main/.agents/skills/editorial-studio
```

Replace `OWNER` with the actual GitHub username or organization. Restart Codex if necessary. This installs the **skill**, not the dashboard.

To run the app, a collaborator downloads/clones the repository and starts `run_windows.cmd` or `run_mac_linux.sh`. Private repository Git access is required.

## 3. Add a private plugin marketplace

The repo includes `plugins/editorial-studio/plugin.json` and `.agents/plugins/marketplace.json`. In Codex CLI, you can add this repository as a marketplace:

```bash
codex plugin marketplace add OWNER/editorial-studio
```

Then open the ChatGPT desktop Plugin Directory or Codex `/plugins` and install **Editorial Studio** from the `Editorial Studio (Private Beta)` source. Availability depends on client and account configuration. This is a *skills-only* plugin: it teaches the editorial workflow but does not remotely control the local Python dashboard.

This route is distinct from the public, universal Plugins Directory, which requires submission and review.

## 4. Create a reproducible beta ZIP

```bash
python scripts/package_release.py
```

The command validates source layout, checks the plugin skill against the canonical Codex skill, then writes a ZIP and SHA-256 checksum into `dist/`. Release assets should be downloaded from GitHub Releases, not executed directly from random URLs. For the private beta, publish a **draft/pre-release** after local Windows smoke tests. An unsigned ZIP is a beta artifact, not a native one-click installer.

## 5. Prerequisites for converting to public

Before clicking **Settings → Danger Zone → Change repository visibility → Public**:

- Audit the **entire Git history**, Actions logs and existing releases for secrets, private imagery, confidential text and personally identifying details. `.gitignore` cannot remove data from earlier commits. If sensitive material entered history, recreate a clean public repository rather than merely deleting the current file.
- Add a chosen open-source `LICENSE` (for example Apache-2.0 or MIT), COPYRIGHT/THIRD_PARTY_NOTICES for included fonts and media, CONTRIBUTING, CODE_OF_CONDUCT if desired, and a security contact.
- Finish an external security review for the image downloader and localhost HTTP routes. Add a locked dependency graph, SBOM, dependency scanners and documented update path.
- Test signed or checksum-verified release artifacts on **clean Windows 11** and macOS, not only in developer environments.
- Perform at least five real editorial design reviews across diverse project types: photo essay, property magazine, company onepager, event guide, and product editorial.
- Verify all public demo images are genuinely licensed for redistribution, and that press/media-kit terms cover PDFs and software packaging.

GitHub warns that switching to public exposes code, forks, workflow history and logs. Consider creating a **separate clean public repository** if the private repo accumulated experimental or sensitive history.

## 6. Actual one-click and one-paste distribution paths

| Distribution | Beta now | Public later |
|---|---|---|
| Codex skill | Copy/paste `$skill-installer` GitHub URL | Public GitHub skill URL, optionally installable via supported skill sites |
| ChatGPT/Codex plugin | Private repo marketplace, Plugin Directory | Official public plugin submission/review |
| Local Windows dashboard | Download ZIP → unzip → double-click `.cmd` | Signed installer (.msi/.exe) from GitHub Releases |
| macOS/Linux dashboard | Clone/unzip → shell script | Signed packaged app or OS-native install path |

Do **not** promise that a skill-install link will also start Python, download unapproved photos, or run background agents.

## References

- Codex skills: https://learn.chatgpt.com/docs/build-skills
- Portable plugins and marketplace: https://developers.openai.com/plugins/build/plugins
- GitHub CLI create: https://cli.github.com/manual/gh_repo_create
- Repo visibility: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/setting-repository-visibility
