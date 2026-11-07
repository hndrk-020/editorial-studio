"""Read-only installation diagnostics; no downloads, app imports or user-data access."""
from __future__ import annotations

import sys
if __name__ == "__main__":
    sys.dont_write_bytecode = True

import argparse
import importlib.metadata
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
APPLICATION_FILES = (
    "studio.py", "engine.py", "creative.py", "photo_researcher.py",
    "image_transport.py", "finalized_edition.py", "local_files.py",
    "static/index.html", "static/studio.css", "static/studio.js",
    "requirements.txt", "requirements.lock",
)


def inspect_installation(root=ROOT, skill=None, skill_only=False):
    """Return checks without loading the app, its settings or any publications."""
    root = Path(root)
    skill = Path(skill) if skill is not None else root / ".agents/skills/editorial-studio"
    checks = []

    def record(name, ok, detail):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})

    entry = skill / "SKILL.md"
    try:
        body = entry.read_text(encoding="utf-8")
        record("Skill instructions", body.startswith("---\n") and
               re.search(r"^name:\s*editorial-studio\s*$", body, re.M), str(entry))
        references = set(re.findall(r"references/[A-Za-z0-9_.-]+\.md", body))
        missing = sorted(name for name in references if not (skill / name).is_file())
        record("Skill references", bool(references) and not missing,
               "Missing: " + ", ".join(missing) if missing else f"{len(references)} linked references found")
        record("Skill metadata", (skill / "agents/openai.yaml").is_file(), "agents/openai.yaml")
    except (OSError, UnicodeError) as error:
        record("Skill instructions", False, f"Cannot read {entry}: {error}. Extract/install the complete skill folder.")

    if not skill_only:
        record("Python", sys.version_info >= (3, 11),
               f"{sys.version.split()[0]} at {sys.executable}; Python 3.11+ is required")
        missing = [name for name in APPLICATION_FILES if not (root / name).is_file()]
        record("PDF application", not missing,
               "Missing: " + ", ".join(missing) + ". Keep the full extracted repository; the skill alone does not include the application."
               if missing else "Full local application files found")
        try:
            lock = (root / "requirements.lock").read_text(encoding="utf-8")
            requirements = re.findall(r"^([A-Za-z0-9_.-]+)==([^\s\\]+)", lock, re.M)
            record("Dependency lock", bool(requirements), "requirements.lock")
            for name, expected in requirements:
                try:
                    actual = importlib.metadata.version(name)
                except importlib.metadata.PackageNotFoundError:
                    actual = "not installed"
                record(name, actual == expected,
                       f"{actual}; requires {expected}" +
                       (". Run the platform launcher to install the locked dependencies into .venv." if actual != expected else ""))
        except (OSError, UnicodeError) as error:
            record("Dependency lock", False, str(error))
    return checks


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill", type=Path, help="Check a specific installed skill folder")
    parser.add_argument("--skill-only", action="store_true", help="Check skill files without requiring the PDF runtime")
    parser.add_argument("--json", action="store_true", help="Print machine-readable results")
    args = parser.parse_args(argv)
    checks = inspect_installation(skill=args.skill, skill_only=args.skill_only)
    passed = all(check["ok"] for check in checks)
    if args.json:
        print(json.dumps({"ok": passed, "checks": checks}, indent=2))
    else:
        for check in checks:
            print(f"{'PASS' if check['ok'] else 'FIX '} {check['check']}: {check['detail']}")
        print("\nNo files, settings or publications were changed. No downloads were attempted.")
        print("File checks do not verify AI-tool discovery or a finished PDF. Ask your AI tool to report the loaded SKILL.md path; inspect an export separately.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
