"""Import official releases. No publishing credential or index key is needed."""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from public_repo import copy_repo

ROOT = Path(__file__).resolve().parents[1]
ADDRESS = "https://panlelapin.github.io/fdroidrepo/"
APPS = json.loads((ROOT / "catalog/apps.json").read_text())


def candidate(app, release):
    tag = release["tag_name"]
    if release["draft"] or release["prerelease"] or not re.fullmatch(r"v\d+(?:\.\d+){1,2}", tag):
        return None
    name = app["asset"].format(version=tag[1:])
    asset = next((a for a in release["assets"] if a["name"] == name), None)
    if asset is None:
        return None  # Signing may still be running.
    if not re.fullmatch(r"sha256:[0-9a-f]{64}", asset.get("digest") or ""):
        raise ValueError(f"Missing GitHub asset digest: {tag}/{name}")
    return tag[1:], asset


def check_manifest(app, version, badging, certs, previous):
    header = re.match(r"^package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging)
    if not header or header[1] != app["package"] or header[3] not in (version, version+".0"):
        raise ValueError(f"Wrong package or version for {app['package']} v{version}")
    if re.findall(r"^Signer #\d+ certificate SHA-256 digest: ([a-f0-9]+)$", certs, re.M) != [app["cert"]]:
        raise ValueError(f"Unexpected APK signer: {app['package']}")
    code = int(header[2])
    if code <= previous:
        raise ValueError(f"{app['package']}: versionCode {code} must exceed {previous}")
    return code


def run(*args):
    return subprocess.check_output(args, text=True)


def collect(work, force=False):
    repo = work / "repo"
    index = json.loads((ROOT / "index-v2.json").read_bytes())
    expected = {pkg: dict(info["versions"]) for pkg, info in index["packages"].items()}
    added = {}
    tools = Path(os.environ["ANDROID_HOME"]) / "build-tools/36.0.0"
    for source, app in APPS.items():
        pkg = app["package"]
        versions = expected.setdefault(pkg, {})
        highest = max((v["manifest"]["versionCode"] for v in versions.values()), default=0)
        pages = json.loads(run("gh", "api", "--paginate", "--slurp", f"repos/{source}/releases?per_page=100"))
        for release in sorted((r for page in pages for r in page), key=lambda r: r["published_at"] or ""):
            result = candidate(app, release)
            if not result:
                continue
            version, asset = result
            digest = asset["digest"].split(":")[1]
            if digest in versions:
                continue
            if not 0 < asset["size"] <= 250 * 1024**2:
                raise ValueError("Unexpected APK size")
            url = f"https://github.com/{source}/releases/download/v{version}/{asset['name']}"
            with tempfile.NamedTemporaryFile(dir=work) as tmp:
                with urllib.request.urlopen(url, timeout=60) as response:
                    size = 0
                    while block := response.read(1024**2):
                        size += len(block)
                        if size > asset["size"]:
                            raise ValueError("Asset larger than declared")
                        tmp.write(block)
                tmp.flush()
                tmp.seek(0)
                if size != asset["size"] or hashlib.file_digest(tmp, "sha256").hexdigest() != digest:
                    raise ValueError("Incorrect APK digest")
                code = check_manifest(app, version, run(tools/"aapt", "dump", "badging", tmp.name),
                                      run(tools/"apksigner", "verify", "--print-certs", tmp.name), highest)
                if not repo.exists():
                    copy_repo(ROOT, repo)
                dest = repo / f"{pkg}_{code}.apk"
                if dest.exists():
                    raise FileExistsError(dest)
                shutil.copyfile(tmp.name, dest)
            highest = code
            versions[digest] = {"manifest": {"versionCode": code}}
            added[dest.name] = digest
            print(f"Validated {pkg} v{version} ({code})")
    dirty = bool(added) or force or index["repo"]["address"] != ADDRESS
    if dirty:
        if not repo.exists():
            copy_repo(ROOT, repo)
        (work/"expected.json").write_text(json.dumps({pkg:sorted(versions) for pkg,versions in expected.items()}))
        # Preserve a delta from the last published index.
        (work/"tmp").mkdir(exist_ok=True)
        shutil.copyfile(repo/"index-v2.json", work/"tmp"/f"repo_{index['repo']['timestamp']}.json")
    if output := os.environ.get("GITHUB_OUTPUT"):
        with open(output, "a") as f:
            print(f"changed={str(dirty).lower()}", file=f)
    print("Index ready for signing" if dirty else "Catalog is already up to date")


if __name__ == "__main__":
    target = Path(sys.argv[1]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    collect(target, "--force" in sys.argv[2:])
