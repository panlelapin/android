import unittest
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
