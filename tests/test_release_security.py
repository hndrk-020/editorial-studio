"""Private dummy files must never become release members."""
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from package_release import release_files


class ReleaseSecurityTests(unittest.TestCase):
    def test_inventory_excludes_unlisted_private_files_and_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)/'source';root.mkdir()
            for original in release_files(ROOT):
                destination=root/original.relative_to(ROOT)
                destination.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(original,destination)
            for name in ('.env.production','private-photo.jpg','personal-manifest.json'):
                (root/name).write_text('DUMMY PRIVATE TEST MARKER')
            command=[sys.executable,str(root/'scripts/package_release.py')]
            subprocess.run(command,cwd=root,check=True,capture_output=True,timeout=15)
            archive=next((root/'dist').glob('*.zip'));first=archive.read_bytes()
            with zipfile.ZipFile(archive) as package:
                self.assertNotIn('editorial-studio/.env.production',package.namelist())
                for name in ('private-photo.jpg','personal-manifest.json'):
                    self.assertNotIn('editorial-studio/'+name,package.namelist())
            subprocess.run(command,cwd=root,check=True,capture_output=True,timeout=15)
            self.assertEqual(first,archive.read_bytes())

    def test_private_paths_and_traversal_cannot_be_allowlisted(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for forbidden in ('.','','.env.production','projects/guide/manifest.json','../private.txt','/private.txt','C:/private.txt'):
                (root/'release-files.json').write_text(json.dumps([forbidden]))
                with self.subTest(forbidden=forbidden),self.assertRaises(ValueError):release_files(root)

    def test_linked_inputs_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'real.txt').write_text('DUMMY TEST')
            try:(root/'linked.txt').symlink_to(root/'real.txt')
            except OSError:self.skipTest('Creating symlinks is unavailable on this platform')
            (root/'release-files.json').write_text('["linked.txt"]')
            with self.assertRaises(ValueError):release_files(root)
