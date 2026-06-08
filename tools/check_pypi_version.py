#!/usr/bin/env python3
import argparse
import ast
import configparser
import urllib.error
import urllib.request
from pathlib import Path


def get_package_metadata(project_root: Path) -> tuple[str, str]:
    setup_cfg = project_root / "setup.cfg"
    parser = configparser.ConfigParser()
    parser.read(setup_cfg, encoding="utf-8")

    name = parser["metadata"]["name"].strip()
    version_value = parser["metadata"]["version"].strip()
    if version_value.startswith("attr:"):
        version = read_attr_value(
            project_root,
            version_value.removeprefix("attr:").strip(),
        )
    else:
        version = version_value
    return name, version


def read_attr_value(project_root: Path, dotted_path: str) -> str:
    module_name, attribute_name = dotted_path.rsplit(".", 1)
    module_path = project_root.joinpath(*module_name.split("."))
    if module_path.is_dir():
        module_path = module_path / "__init__.py"
    else:
        module_path = module_path.with_suffix(".py")

    module_ast = ast.parse(module_path.read_text(encoding="utf-8"))
    for node in module_ast.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == attribute_name:
                value = ast.literal_eval(node.value)
                if not isinstance(value, str):
                    raise ValueError(
                        f"{attribute_name} in {module_path} must be a string",
                    )
                return value

    raise ValueError(f"Unable to find {attribute_name} in {module_path}")


def get_tag_version(tag: str) -> str:
    if not tag.startswith("v"):
        raise ValueError(f"Release tag must start with 'v', got {tag!r}")
    tag_version = tag.removeprefix("v")
    if not tag_version:
        raise ValueError("Release tag must include a version after 'v'")
    return tag_version


def ensure_tag_matches_version(tag: str, package_version: str) -> None:
    tag_version = get_tag_version(tag)
    if tag_version != package_version:
        raise ValueError(
            f"Release tag version {tag_version!r} does not match package version "
            f"{package_version!r}",
        )


def version_exists_on_pypi(package_name: str, package_version: str) -> bool:
    url = f"https://pypi.org/pypi/{package_name}/{package_version}/json"
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "multidict-release-check"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return False
        raise


def write_outputs(output_path: Path, outputs: dict[str, str]) -> None:
    with output_path.open("a", encoding="utf-8") as output_file:
        for key, value in outputs.items():
            print(f"{key}={value}", file=output_file)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--project-root",
        default=Path(__file__).resolve().parents[1],
        type=Path,
    )
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--tag")
    args = parser.parse_args()

    package_name, package_version = get_package_metadata(args.project_root)
    if args.tag is not None:
        ensure_tag_matches_version(args.tag, package_version)

    exists = version_exists_on_pypi(package_name, package_version)
    outputs = {
        "package_name": package_name,
        "package_version": package_version,
        "pypi_version_exists": str(exists).lower(),
    }

    if args.github_output is not None:
        write_outputs(args.github_output, outputs)

    print(f"{package_name} {package_version} exists_on_pypi={str(exists).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
