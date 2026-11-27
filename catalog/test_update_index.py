"""Integration coverage for fdroidserver's nonstandard repository URL adapter."""
import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


@unittest.skipUnless(importlib.util.find_spec("fdroidserver"), "Install fdroidserver==2.4.5 for integration tests")
class RootUrlGeneration(unittest.TestCase):
    def test_custom_url_reaches_the_generated_index_before_signing(self):
        self.assertIsNotNone(importlib.util.find_spec("update_index"),
                             "A root-URL adapter is required for fdroidserver")
        from update_index import configure_repo
        from fdroidserver import common, index

        address = "https://panlelapin.github.io/fdroidrepo/"
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as tmp, \
             patch.object(common, "config", None), \
             patch.object(common, "options", SimpleNamespace(pretty=False, nosign=True)):
            try:
                os.chdir(tmp)
                config_file = Path("config.yml")
                config_file.write_text(json.dumps({
                    "repo_url": address + "repo",
                    "sdk_path": tmp, "java_paths": {},
                    "apksigner": "/usr/bin/true",
                }))
                config_file.chmod(0o600)
                config = configure_repo(address)
                # The actual fdroidserver loader must reuse the initialized config.
                self.assertEqual(common.read_config()["repo_url"], address)
                self.assertEqual(json.loads(config_file.read_text())["repo_url"], address + "repo")
                Path("repo/icons").mkdir(parents=True)
                Path("repo/icons/icon.png").write_bytes(b"public icon")
                Path("tmp").mkdir()
                index.make_v2({}, [], "repo", {
                    "address": config["repo_url"], "name": "Pan le lapin",
                    "description": "Android apps by panlelapin", "icon": "icon.png",
                    "timestamp": datetime(2026, 11, 27, tzinfo=timezone.utc),
                    "version": 20002,
                }, {}, {}, False)
                generated = json.loads(Path("repo/index-v2.json").read_text())
                self.assertEqual(generated["repo"]["address"], address)
                self.assertEqual(generated["repo"]["description"],
                                 {"en-US": "Android apps by panlelapin"})
                self.assertTrue(Path("repo/entry.json").is_file())
            finally:
                os.chdir(original_cwd)
