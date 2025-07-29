#!/usr/bin/env python3
"""Script to build and publish Zuma to PyPI."""

import argparse
import subprocess
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, NoReturn, TypeAlias

# Type definitions
ExitCode: TypeAlias = Literal[0, 1]
Command: TypeAlias = list[str]


@dataclass
class PublishConfig:
    """Configuration for publishing."""

    version: str
    dry_run: bool = False
    test_pypi: bool = False
    skip_tests: bool = False


def run_command(cmd: Command, check: bool = True) -> subprocess.CompletedProcess[str]:
    """Run a command and return its output."""
    return subprocess.run(cmd, check=check, text=True, capture_output=True)


def get_version() -> str:
    """Get the current version from pyproject.toml."""
    pyproject = Path("pyproject.toml")
    if not pyproject.exists():
        sys.exit("pyproject.toml not found")

    with open(pyproject, "rb") as f:
        try:
            data = tomllib.load(f)
            return str(data["project"]["version"])
        except (KeyError, tomllib.TOMLDecodeError) as e:
            sys.exit(f"Failed to read version from pyproject.toml: {e}")


def clean_build_files() -> None:
    """Clean up build artifacts."""
    paths = ["build/", "dist/", "*.egg-info"]
    for path in paths:
        cmd = ["rm", "-rf", path]
        run_command(cmd, check=False)


def run_tests() -> None:
    """Run the test suite."""
    print("Running tests...")
    result = run_command(["pytest"])
    if result.returncode != 0:
        print("Tests failed!")
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(1)
    print("Tests passed!")


def build_package() -> None:
    """Build the package."""
    print("Building package...")
    run_command(["python", "-m", "build"])


def publish_package(config: PublishConfig) -> None:
    """Publish the package to PyPI."""
    repository = "--repository-url https://test.pypi.org/legacy/" if config.test_pypi else ""
    cmd = ["twine", "upload"]

    if config.dry_run:
        cmd.append("--dry-run")
    if repository:
        cmd.extend(repository.split())

    cmd.append("dist/*")

    print(f"Publishing version {config.version}...")
    result = run_command(cmd)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)


def main() -> NoReturn:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build and publish Zuma to PyPI")
    parser.add_argument("--dry-run", action="store_true", help="Don't actually upload")
    parser.add_argument("--test", action="store_true", help="Upload to TestPyPI")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    args = parser.parse_args()

    config = PublishConfig(
        version=get_version(), dry_run=args.dry_run, test_pypi=args.test, skip_tests=args.skip_tests
    )

    try:
        clean_build_files()
        if not config.skip_tests:
            run_tests()
        build_package()
        publish_package(config)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
