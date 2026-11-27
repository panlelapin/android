import unittest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import patch
import importer
from importer import candidate, check_manifest


class ImportRules(unittest.TestCase):
    app = {"package": "com.github.panlelapin.blackbg", "asset": "BlackBG-{version}-arm64-v8a.apk", "cert": "a"*64}
    release = {"tag_name": "v1.1", "draft": False, "prerelease": False,
               "assets": [{"name": "BlackBG-1.1-arm64-v8a.apk", "digest": "sha256:"+"b"*64, "size": 5000}]}
    header = "package: name='com.github.panlelapin.blackbg' versionCode='2' versionName='1.1'"
    certs = "Signer #1 certificate SHA-256 digest: "+"a"*64

    def test_waits_for_signed_asset_and_skips_drafts(self):
        self.assertIsNone(candidate(self.app, dict(self.release, draft=True)))
        self.assertIsNone(candidate(self.app, dict(self.release, assets=[])))
        self.assertEqual(candidate(self.app, self.release)[0], "1.1")

    def test_only_advancing_signed_version(self):
        self.assertEqual(check_manifest(self.app, "1.1", self.header, self.certs, 1), 2)
        for header, certs, previous in (
            (self.header, self.certs, 2),
            (self.header.replace("blackbg", "wfqa"), self.certs, 1),
            (self.header.replace("1.1", "1.2"), self.certs, 1),
            (self.header, self.certs.replace("aaa", "bbb"), 1),
            (self.header, self.certs+"\nSigner #2 certificate SHA-256 digest: "+"f"*64, 1),
        ):
            with self.assertRaises(ValueError):
                check_manifest(self.app, "1.1", header, certs, previous)


class RepositoryMigration(unittest.TestCase):
    package = "com.github.panlelapin.blackbg"
    address = "https://panlelapin.github.io/fdroidrepo/"

    def seed(self, root, address):
        index = {"repo": {"address": address, "timestamp": 123},
                 "packages": {self.package: {"versions": {}}}}
        (root / "index-v2.json").write_text(json.dumps(index))
        (root / f"{self.package}_1.apk").write_bytes(b"unchanged APK")
        (root / "icons").mkdir()
        (root / "icons/icon.png").write_bytes(b"icon")
        # Legacy layout lets the old importer run, but it must no longer be used.
        legacy = root / "fdroid/repo"
        legacy.mkdir(parents=True)
        (legacy / "index-v2.json").write_text(json.dumps(index))
        (legacy / f"{self.package}_1.apk").write_bytes(b"legacy APK")
        (root / "catalog").mkdir()
        (root / "catalog/private.p12").write_bytes(b"private")
        (root / ".github").mkdir()
        (root / "README.md").write_text("Development documentation")
        (root / "config.yml").write_text("private configuration")
        # This Pages-only marker must not be scanned as a repository download.
        (root / ".nojekyll").touch()

    def collect(self, root, work, force=False):
        with patch.object(importer, "ROOT", root), \
             patch.object(importer, "run", return_value="[[]]"), \
             patch.dict(os.environ, {"ANDROID_HOME": str(root)}):
            importer.collect(work, force)

    def test_address_change_stages_root_assets_without_new_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.seed(root, "https://panlelapin.github.io/android/fdroid/repo")
            work = root / "work"
            work.mkdir()
            self.collect(root, work)
            self.assertTrue((work / "repo").is_dir(), "Address migration must rebuild the index")
            self.assertEqual((work / f"repo/{self.package}_1.apk").read_bytes(), b"unchanged APK")
            self.assertEqual({p.name for p in (work / "repo").iterdir()},
                             {"index-v2.json", f"{self.package}_1.apk", "icons"})
            self.assertEqual(json.loads((work / "expected.json").read_text()),
                             {app["package"]: [] for app in importer.APPS.values()})
            self.assertTrue((work / "tmp/repo_123.json").is_file())

    def test_current_address_does_not_rebuild_without_new_releases(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.seed(root, self.address)
            work = root / "work"
            work.mkdir()
            self.collect(root, work)
            self.assertFalse((work / "repo").exists())
            self.assertFalse((work / "expected.json").exists())

    def test_forced_rebuild_stages_root_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.seed(root, self.address)
            work = root / "work"
            work.mkdir()
            self.collect(root, work, force=True)
            self.assertEqual((work / f"repo/{self.package}_1.apk").read_bytes(), b"unchanged APK")

    def test_public_copy_excludes_tooling_and_replaces_only_public_files(self):
        self.assertTrue(callable(getattr(importer, "copy_repo", None)),
                        "A shared public-only copy helper is required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.seed(root, self.address)
            dest = root / "destination"
            dest.mkdir()
            (dest / "README.md").write_text("Keep development files")
            (dest / f"{self.package}_99.apk").write_bytes(b"obsolete")
            importer.copy_repo(root, dest, replace=True)
            self.assertEqual({p.name for p in dest.iterdir()},
                             {"README.md", "index-v2.json", f"{self.package}_1.apk", "icons"})
            self.assertEqual((dest / "README.md").read_text(), "Keep development files")

    def test_public_copy_rejects_symlinks(self):
        self.assertTrue(callable(getattr(importer, "copy_repo", None)),
                        "A shared public-only copy helper is required")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.seed(root, self.address)
            (root / "icons/secret").symlink_to(root / "config.yml")
            with self.assertRaises(ValueError):
                importer.copy_repo(root, root / "destination")
