#!/usr/bin/env python3

import json
import sys
import urllib.request
import urllib.error


def get_tag_version(tag_ref: str) -> str:
    if tag_ref.startswith("v"):
        return tag_ref[1:]
    return tag_ref


def get_local_version() -> str:
    version_ns: dict = {}
    with open("multidict/__init__.py") as f:
        exec(f.read(), version_ns)
    return version_ns["__version__"]


def is_version_on_pypi(package: str, version: str) -> bool:
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        with urllib.request.urlopen(url, timeout=30) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise
    releases = data.get("releases", {})
    return version in releases


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: check-version.py <tag-ref>", file=sys.stderr)
        sys.exit(1)

    tag_ref = sys.argv[1]
    tag_version = get_tag_version(tag_ref)
    local_version = get_local_version()

    if tag_version != local_version:
        print(
            f"ERROR: Tag version ({tag_version}) does not match "
            f"local version ({local_version})",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Version to release: {tag_version}")

    if is_version_on_pypi("multidict", tag_version):
        print(
            f"ERROR: Version {tag_version} already exists on PyPI!",
            file=sys.stderr,
        )
        sys.exit(1)

    print(f"Version {tag_version} is not yet on PyPI — safe to proceed.")


if __name__ == "__main__":
    main()
