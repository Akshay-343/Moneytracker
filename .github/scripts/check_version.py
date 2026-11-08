"""Checks that a pull request bumps the version the way its branch name says.

Usage: python check_version.py <branch> <base_init_py> <is_breaking: true|false>
Run from the repository root; reads the PR's versions from the working tree.
"""
import json
import re
import sys
from pathlib import Path

NO_BUMP = ("chore/", "docs/", "dependabot/")
BUMPS = {"feature/": "minor", "bugfix/": "patch", "hotfix/": "patch"}


def parse(text: str) -> tuple[int, int, int]:
    m = re.search(r'__version__ = "(\d+)\.(\d+)\.(\d+)"', text)
    if not m:
        sys.exit("Could not find __version__ in backend/app/__init__.py")
    return tuple(int(x) for x in m.groups())


def fmt(v: tuple[int, int, int]) -> str:
    return ".".join(map(str, v))


def fail(msg: str) -> None:
    print(f"::error::{msg}")
    sys.exit(1)


def main() -> None:
    branch, base_file, breaking = sys.argv[1], sys.argv[2], sys.argv[3] == "true"
    base = parse(Path(base_file).read_text())
    new = parse(Path("backend/app/__init__.py").read_text())
    frontend = json.loads(Path("frontend/package.json").read_text())["version"]

    if frontend != fmt(new):
        fail(f"Version mismatch: backend is {fmt(new)}, frontend/package.json is {frontend}")

    if breaking:
        kind = "major"
    elif branch.startswith(NO_BUMP):
        kind = None
    else:
        kind = next((k for prefix, k in BUMPS.items() if branch.startswith(prefix)), "unknown")

    if kind == "unknown":
        fail(f"Branch '{branch}' must start with feature/, bugfix/, hotfix/, chore/ or docs/")

    if kind is None:
        if new != base:
            fail(f"{branch} branches must not change the version (main is {fmt(base)}, this PR has {fmt(new)})")
        print(f"No version bump needed for {branch}; version stays {fmt(base)}")
        return

    major, minor, patch = base
    expected = {"major": (major + 1, 0, 0), "minor": (major, minor + 1, 0), "patch": (major, minor, patch + 1)}[kind]
    if new != expected:
        fail(f"This is a {kind} change: bump the version from {fmt(base)} to {fmt(expected)} (found {fmt(new)}). "
             f"Set it in backend/app/__init__.py and run `npm version {fmt(expected)} --no-git-tag-version` in frontend/")

    if f"## [{fmt(new)}]" not in Path("CHANGELOG.md").read_text(encoding="utf-8"):
        fail(f"Add a '## [{fmt(new)}] - YYYY-MM-DD' section to CHANGELOG.md")

    print(f"Version bump OK: {fmt(base)} -> {fmt(new)} ({kind})")


if __name__ == "__main__":
    main()
