"""Copy only public F-Droid assets, never repository tooling or secrets."""
import json
import re
import shutil
import sys
from pathlib import Path

PACKAGES = {app["package"] for app in
            json.loads((Path(__file__).parent / "apps.json").read_text()).values()}
PUBLIC_NAMES = {
    ".nojekyll", "index.html", "index.css", "index.png", "index.xml",
    "index.jar", "index-v1.jar", "index-v1.json", "index-v2.json",
    "entry.jar", "entry.json", "icons", "diff",
} | PACKAGES


def public_paths(source):
    return sorted(path for path in source.iterdir()
                  if path.name in PUBLIC_NAMES or any(
                      re.fullmatch(re.escape(pkg) + r"_\d+\.apk", path.name)
                      for pkg in PACKAGES))


def copy_repo(source, target, replace=False):
    paths = public_paths(source)
    if any(path.is_symlink() or any(p.is_symlink() for p in path.rglob("*"))
           for path in paths):
        raise ValueError("Symlinks are not allowed in the public repository")
    target.mkdir(parents=True, exist_ok=True)
    if replace:
        for path in public_paths(target):
            if path.is_dir() and not path.is_symlink():
                shutil.rmtree(path)
            else:
                path.unlink()
    for path in paths:
        dest = target / path.name
        if path.is_dir():
            shutil.copytree(path, dest)
        else:
            shutil.copyfile(path, dest)


if __name__ == "__main__":
    copy_repo(Path(sys.argv[1]), Path(sys.argv[2]), "--replace" in sys.argv[3:])
