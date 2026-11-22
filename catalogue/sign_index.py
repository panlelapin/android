"""Regenerate the public repo in staging; never put signing material in Git."""
import base64
import hashlib
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
from pathlib import Path
from importer import ADDRESS, APPS, ROOT

FINGERPRINT = "363DEB527CD0C41ABBC30359005EE6F2A5A6869716D32CF42CEED66DCC3A7A7A"
os.umask(0o077)
work = Path(sys.argv[1]).resolve()
os.chdir(work)
password = os.environ.pop("INDEX_PASSWORD")
key = work/"index.p12"
config = work/"config.yml"
try:
    key.write_bytes(base64.b64decode(os.environ.pop("INDEX_P12"), validate=True))
    # JSON is a subset of YAML; passwords are quoted safely.
    config.write_text(json.dumps(dict(
        sdk_path=os.environ["ANDROID_HOME"], repo_keyalias="blackbg-repo", keystore=str(key),
        keystorepass=password, keypass=password, repo_url=ADDRESS, repo_icon="icon.png",
        repo_name="Pan le lapin", repo_description="Applications Android de panlelapin",
        archive_older=0, make_current_version_link=False
    )))
    shutil.copyfile("repo/icons/icon.png", "icon.png")
    shutil.copytree(ROOT/"catalogue/metadata", "metadata")
    subprocess.run(["fdroid", "update"], check=True)
finally:
    key.unlink(missing_ok=True)
    config.unlink(missing_ok=True)

repo = work/"repo"
index = json.loads((repo/"index-v2.json").read_bytes())
expected = json.loads((work/"expected.json").read_bytes())
if index["repo"]["address"] != ADDRESS or set(index["packages"]) != set(expected):
    raise ValueError("Wrong catalogue URL or package set")
pins = {app["package"]:app["cert"] for app in APPS.values()}
for pkg, versions in expected.items():
    found = index["packages"][pkg]["versions"]
    if sorted(found) != versions:
        raise ValueError(f"Missing or unexpected versions for {pkg}")
    for digest, v in found.items():
        apk = repo/f"{pkg}_{v['manifest']['versionCode']}.apk"
        if (v["manifest"]["signer"]["sha256"] != [pins[pkg]] or
                v["file"]["name"] != "/"+apk.name or
                hashlib.file_digest(apk.open("rb"), "sha256").hexdigest() != digest):
            raise ValueError(f"Incorrect indexed APK: {apk.name}")
subprocess.run(["jarsigner","-verify",str(repo/"entry.jar")],check=True,stdout=subprocess.DEVNULL)
cert = subprocess.check_output(["keytool","-printcert","-jarfile",str(repo/"entry.jar"),"-rfc"])
certificates = re.findall(rb"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----", cert, re.S)
if len(certificates) != 1 or hashlib.sha256(ssl.PEM_cert_to_DER_cert(certificates[0].decode())).hexdigest().upper() != FINGERPRINT:
    raise ValueError("Unexpected catalogue signing certificate")
if (repo/"status").is_dir():
    shutil.rmtree(repo/"status")
if any(f.is_symlink() or f.suffix in {".p12",".jks",".keystore"} or f.name=="config.yml" for f in repo.rglob("*")):
    raise ValueError("Unexpected file in public repo")
