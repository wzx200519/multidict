#!/usr/bin/env python3

import json
import re
import sys
import urllib.error
import urllib.request

PACKAGE_NAME = "multidict"
PYPI_JSON_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
VERSION_FILE = "multidict/__init__.py"

RE_VERSION = re.compile(r'''__version__\s*=\s*["']([^"']+)["']''')


def get_local_version() -> str:
    with open(VERSION_FILE, encoding="utf-8") as fh:
        for line in fh:
            match = RE_VERSION.search(line)
            if match:
                return match.group(1)
    raise SystemExit(
        f"Could not find __version__ in {VERSION_FILE}"
    )


def check_pypi(version: str) -> bool:
    req = urllib.request.Request(PYPI_JSON_URL)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            print(f"Package '{PACKAGE_NAME}' not found on PyPI. Proceeding.")
            return False
        raise SystemExit(f"HTTP {exc.code}: could not query PyPI") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Network error querying PyPI: {exc}") from exc

    releases = data.get("releases", {})
    if version in releases:
        print(
            f"Version {version} already exists on PyPI. "
            "Skipping release."
        )
        return True
    print(f"Version {version} does not exist on PyPI. Proceeding.")
    return False


def main() -> None:
    version = get_local_version()
    exists = check_pypi(version)
    if exists:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()