#!/usr/bin/env python3
"""Repack an already-validated FreeBSD .NET 10 runtime for OPNsense 26.7.

Changes only the explicit openssl dependency in the UCL manifest.
Runs on a trusted FreeBSD build host with 'pkg' and an installed staging root.
Never run against the production OPNsense root.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import tempfile

OLD = '''    openssl: {
        origin: "security/openssl",
        version: "3.5.9,1"
    }'''
NEW = '''    openssl35: {
        origin: "security/openssl35",
        version: "3.5.9"
    }'''


def run(*args: str) -> str:
    completed = subprocess.run(
        args, capture_output=True, text=True, check=True
    )
    return completed.stdout


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_pkg", type=Path, help="validated dotnet-runtime10-10.0.15.pkg")
    parser.add_argument("staging_root", type=Path, help="isolated jail root containing installed runtime")
    parser.add_argument("output_dir", type=Path, help="new, empty output directory")
    args = parser.parse_args()

    source = args.source_pkg.resolve(strict=True)
    staging = args.staging_root.resolve(strict=True)
    output = args.output_dir.resolve()
    if source.name != "dotnet-runtime10-10.0.15.pkg":
        parser.error("unexpected source package filename")
    if staging == Path("/"):
        parser.error("refusing to use the host filesystem as staging root")
    if not (staging / "usr/local/lib/dotnet10/dotnet").is_file():
        parser.error("staging root lacks the installed .NET 10 runtime")
    if output.exists() and any(output.iterdir()):
        parser.error("output directory is not empty")
    output.mkdir(parents=True, exist_ok=True)

    original = run("pkg", "info", "--raw", "-F", str(source))
    if original.count(OLD) != 1:
        parser.error("expected exactly one FreeBSD OpenSSL dependency record")
    modified = original.replace(OLD, NEW)
    if modified.replace(NEW, OLD) != original:
        parser.error("unexpected change outside the OpenSSL dependency record")

    with tempfile.TemporaryDirectory(prefix="dotnet10-repack-") as scratch:
        manifest = Path(scratch) / "dotnet-runtime10.opnsense.ucl"
        manifest.write_text(modified, encoding="utf-8")
        subprocess.run(
            ["pkg", "create", "-M", str(manifest), "-r", str(staging), "-o", str(output)],
            check=True,
        )

    result = output / source.name
    if not result.is_file():
        parser.error("pkg create did not produce the expected package")

    repacked = run("pkg", "info", "--raw", "-F", str(result))
    if repacked != modified:
        parser.error("repacked UCL manifest differs from the intended manifest")
    original_files = run("pkg", "info", "-l", "-F", str(source)).splitlines()
    output_files = run("pkg", "info", "-l", "-F", str(result)).splitlines()
    if original_files != output_files:
        parser.error("repacked file listing differs from original")

    print("Validated derived package:", result)
    print(run("pkg", "info", "-d", "-F", str(result)).strip())
    print(run("sha256", str(result)).strip())
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as error:
        print(f"Command failed: {error.cmd} (exit {error.returncode})", file=sys.stderr)
        sys.exit(error.returncode or 1)
