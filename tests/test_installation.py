"""Installation checks use isolated sources/profiles and never the user's skill."""
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import venv
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import check_installation as diagnostic


def snapshot(root):
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in root.rglob("*") if p.is_file()}


class InstallationDiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="Editorial install ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Extracted source with spaces"
        self.skill = self.root / ".agents/skills/editorial-studio"
        shutil.copytree(ROOT / ".agents/skills/editorial-studio", self.skill)

    def test_skill_only_passes_without_app_and_full_check_explains_missing_app(self):
        (self.root / "projects").mkdir()
        (self.root / "projects/private.txt").write_bytes(b"PRIVATE TEST FIXTURE")
        before = snapshot(self.root)
        self.assertTrue(all(c["ok"] for c in diagnostic.inspect_installation(self.root, skill_only=True)))
        checks = diagnostic.inspect_installation(self.root)
        app = next(c for c in checks if c["check"] == "PDF application")
        self.assertFalse(app["ok"])
        self.assertIn("skill alone does not include", app["detail"])
        self.assertEqual(before, snapshot(self.root))

    def test_missing_reference_is_actionable_and_cannot_pass(self):
        (self.skill / "references/editorial_planning.md").unlink()
        checks = diagnostic.inspect_installation(self.root, skill_only=True)
        failure = next(c for c in checks if c["check"] == "Skill references")
        self.assertFalse(failure["ok"])
        self.assertIn("references/editorial_planning.md", failure["detail"])

    def test_missing_dependency_and_wrong_version_are_distinct_failures(self):
        (self.root / "requirements.lock").write_text("Pillow==13.0.0\nreportlab==4.5.1\n")
        with patch.object(diagnostic.importlib.metadata, "version",
                          side_effect=[importlib.metadata.PackageNotFoundError("Pillow"), "0.0.0"]):
            checks = diagnostic.inspect_installation(self.root)
        failures = {c["check"]: c for c in checks if not c["ok"]}
        self.assertIn("not installed", failures["Pillow"]["detail"])
        self.assertIn("0.0.0; requires 4.5.1", failures["reportlab"]["detail"])

    def test_old_python_is_rejected(self):
        with patch.object(diagnostic.sys, "version_info", (3, 10, 0)):
            checks = diagnostic.inspect_installation(self.root)
        self.assertFalse(next(c["ok"] for c in checks if c["check"] == "Python"))

    def test_fresh_process_json_check_needs_no_dependencies_or_user_data(self):
        script = self.root / "scripts/check_installation.py"
        script.parent.mkdir()
        shutil.copyfile(ROOT / "scripts/check_installation.py", script)
        before = snapshot(self.root)
        command = [sys.executable, "-B", "-S", str(script), "--json"]
        result = subprocess.run(command + ["--skill-only"], capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertFalse(json.loads(result.stdout)["ok"])
        self.assertEqual(before, snapshot(self.root))


class LauncherCheckTests(unittest.TestCase):
    def test_existing_incomplete_environment_is_preserved_for_check_and_start(self):
        with tempfile.TemporaryDirectory(prefix="Editorial broken app ") as temporary:
            root = Path(temporary)
            (root / ".venv").mkdir()
            (root / ".venv/local-marker.txt").write_text("EXISTING ENVIRONMENT TEST MARKER")
            for name in ("run_windows.cmd", "run_mac_linux.sh"):
                shutil.copyfile(ROOT / name, root / name)
            before = snapshot(root)
            command = (["cmd.exe", "/d", "/c", "run_windows.cmd"] if os.name == "nt"
                       else ["bash", "run_mac_linux.sh"])
            for args in (["--check"], []):
                result = subprocess.run(command + args, cwd=root, input="\n", capture_output=True,
                                        text=True, timeout=10)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("not replaced", result.stdout + result.stderr)
                self.assertEqual(before, snapshot(root))

    @unittest.skipIf(os.name == "nt", "Unix symlink permissions and launcher behavior")
    def test_dangling_environment_interpreter_does_not_trigger_recreation(self):
        with tempfile.TemporaryDirectory(prefix="Editorial dangling app ") as temporary:
            root = Path(temporary)
            (root / ".venv/bin").mkdir(parents=True)
            interpreter = root / ".venv/bin/python"
            interpreter.symlink_to(root / "missing-python")
            shutil.copyfile(ROOT / "run_mac_linux.sh", root / "run_mac_linux.sh")
            for args in (["--check"], []):
                result = subprocess.run(["bash", "run_mac_linux.sh", *args], cwd=root,
                                        capture_output=True, text=True, timeout=10)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertTrue(interpreter.is_symlink())
                self.assertFalse((root / ".venv/pyvenv.cfg").exists())

    @unittest.skipUnless(os.name == "nt", "Windows launcher discovery")
    def test_unusable_py_launcher_falls_back_to_supported_path_python(self):
        with tempfile.TemporaryDirectory(prefix="Editorial fallback ") as temporary:
            root = Path(temporary)
            for name in (*diagnostic.APPLICATION_FILES, "run_windows.cmd", "scripts/check_installation.py"):
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            shutil.copytree(ROOT / ".agents", root / ".agents")
            fake_bin = root / "Unusable py launcher"
            fake_bin.mkdir()
            # A real executable that rejects Python's arguments, without running a shell or downloading anything.
            shutil.copyfile(Path(os.environ["SystemRoot"]) / "System32/where.exe", fake_bin / "py.exe")
            env = dict(os.environ, PATH=os.pathsep.join((str(fake_bin), str(Path(sys.executable).parent),
                                                        str(Path(os.environ["SystemRoot"]) / "System32"))))
            result = subprocess.run(["cmd.exe", "/d", "/c", "run_windows.cmd", "--check"], cwd=root,
                                    env=env, capture_output=True, text=True, timeout=10)
            self.assertIn("PASS Python:", result.stdout, result.stdout + result.stderr)
            self.assertIn(sys.executable, result.stdout)
            self.assertFalse((root / ".venv").exists())

    def test_read_only_check_in_fresh_environment_reports_missing_runtime(self):
        with tempfile.TemporaryDirectory(prefix="Editorial fresh app ") as temporary:
            root = Path(temporary) / "Application with spaces"
            for name in (*diagnostic.APPLICATION_FILES, "run_windows.cmd", "run_mac_linux.sh",
                         "scripts/check_installation.py"):
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, destination)
            shutil.copytree(ROOT / ".agents", root / ".agents")
            venv.EnvBuilder(with_pip=False).create(root / ".venv")
            before = snapshot(root)
            command = (["cmd.exe", "/d", "/c", "run_windows.cmd", "--check"] if os.name == "nt"
                       else ["bash", "run_mac_linux.sh", "--check"])
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("not installed", result.stdout)
            self.assertEqual(before, snapshot(root))


@unittest.skipUnless(os.name == "nt", "Windows batch installer is tested on Windows CI")
class WindowsInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="Editorial Windows ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "Extracted source with spaces"
        self.source = self.root / ".agents/skills/editorial-studio"
        shutil.copytree(ROOT / ".agents/skills/editorial-studio", self.source)
        shutil.copyfile(ROOT / "install_codex_skill_windows.cmd", self.root / "install_codex_skill_windows.cmd")
        self.profile = Path(self.temp.name) / "Fresh User Profile"
        self.profile.mkdir()
        self.destination = self.profile / ".agents/skills/editorial-studio"

    def run_installer(self, *args, answer="\n"):
        env = dict(os.environ, USERPROFILE=str(self.profile))
        return subprocess.run(["cmd.exe", "/d", "/c", "install_codex_skill_windows.cmd", *args],
                              cwd=self.root, env=env, input=answer, capture_output=True,
                              text=True, timeout=10)

    def test_installs_complete_skill_in_fresh_profile_with_spaces_and_checks_it(self):
        result = self.run_installer()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(snapshot(self.source), snapshot(self.destination))
        before = snapshot(self.profile)
        result = self.run_installer("--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(before, snapshot(self.profile))

    def test_check_rejects_missing_or_changed_files_without_writing(self):
        self.assertEqual(self.run_installer("--check").returncode, 1)
        self.assertFalse(self.destination.exists())
        shutil.copytree(self.source, self.destination)
        (self.destination / "SKILL.md").write_text("INTENTIONAL LOCAL EDIT")
        before = snapshot(self.profile)
        self.assertEqual(self.run_installer("--check").returncode, 1)
        self.assertEqual(before, snapshot(self.profile))

    def test_incomplete_source_is_rejected_before_creating_destination(self):
        (self.source / "references/brand_system.md").unlink()
        result = self.run_installer()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertFalse(self.destination.exists())

    def test_existing_incomplete_folder_is_preserved_when_update_declined(self):
        self.destination.mkdir(parents=True)
        (self.destination / "local-notes.txt").write_text("EXISTING TEST USER EDIT")
        before = snapshot(self.profile)
        result = self.run_installer(answer="N\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("already exists", result.stdout)
        self.assertEqual(before, snapshot(self.profile))

    def test_explicit_update_retains_extra_files(self):
        shutil.copytree(self.source, self.destination)
        (self.destination / "SKILL.md").write_text("OLD TEST VERSION")
        (self.destination / "local-notes.txt").write_text("EXISTING TEST USER EDIT")
        result = self.run_installer(answer="Y\n")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.source / "SKILL.md").read_bytes(), (self.destination / "SKILL.md").read_bytes())
        self.assertEqual((self.destination / "local-notes.txt").read_text(), "EXISTING TEST USER EDIT")


if __name__ == "__main__":
    unittest.main()
