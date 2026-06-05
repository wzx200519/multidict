#!/usr/bin/env python3
import os
import re
import sys
import requests
from packaging.version import parse


def get_version_from_tag():
    tag = os.environ.get("GITHUB_REF_NAME", "")
    if not tag.startswith("v"):
        print("::error::Tag must start with 'v'")
        sys.exit(1)
    version = tag[1:]
    try:
        parse(version)
        return version
    except Exception as e:
        print(f"::error::Invalid version format: {e}")
        sys.exit(1)


def version_exists_on_pypi(package_name, version):
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json", timeout=10)
        if response.status_code == 404:
            return False
        response.raise_for_status()
        data = response.json()
        releases = data.get("releases", {})
        return version in releases
    except requests.RequestException as e:
        print(f"::warning::Failed to check PyPI: {e}")
        return False


def main():
    package_name = "multidict"
    version = get_version_from_tag()
    
    exists = version_exists_on_pypi(package_name, version)
    
    with open(os.environ.get("GITHUB_OUTPUT", "/dev/null"), "a") as f:
        f.write(f"version_exists={str(exists).lower()}\n")
    
    if exists:
        print(f"::error::Version {version} already exists on PyPI!")
        sys.exit(1)
    else:
        print(f"::notice::Version {version} is available on PyPI")


if __name__ == "__main__":
    main()
