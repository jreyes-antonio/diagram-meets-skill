#!/usr/bin/env python3
"""Report the installed skill version and optionally compare it with upstream."""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

VERSION_FILE = Path(__file__).resolve().parents[1] / "VERSION"
REMOTE_VERSION_URL = (
    "https://raw.githubusercontent.com/jreyes-antonio/"
    "diagram-meets-skill/main/transcript-to-flowchart/VERSION"
)
UPDATE_COMMAND = (
    "npx skills@latest update transcript-to-flowchart --global --yes"
)
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def read_version(path: Path) -> str:
    version = path.read_text(encoding="utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"invalid semantic version in {path}: {version!r}")
    return version


def version_tuple(version: str) -> tuple[int, int, int]:
    match = SEMVER_RE.fullmatch(version)
    if not match:
        raise ValueError(f"invalid semantic version: {version!r}")
    return tuple(int(part) for part in match.groups())


def fetch_latest(timeout: float) -> str:
    remote_url = f"{REMOTE_VERSION_URL}?ts={int(time.time())}"
    curl = shutil.which("curl")
    if curl:
        completed = subprocess.run(
            [
                curl,
                "--fail",
                "--silent",
                "--show-error",
                "--max-time",
                str(max(1, math.ceil(timeout))),
                remote_url,
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout + 2,
        )
        if completed.returncode == 0:
            version = completed.stdout.strip()
            if not SEMVER_RE.fullmatch(version):
                raise ValueError(f"upstream returned an invalid version: {version!r}")
            return version
        raise OSError(completed.stderr.strip() or f"curl exited with {completed.returncode}")

    request = urllib.request.Request(
        remote_url,
        headers={"User-Agent": "transcript-to-flowchart-version-check"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        version = response.read(100).decode("utf-8").strip()
    if not SEMVER_RE.fullmatch(version):
        raise ValueError(f"upstream returned an invalid version: {version!r}")
    return version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Compare with the version published on GitHub")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument("--timeout", type=float, default=5.0, help="Network timeout in seconds")
    args = parser.parse_args()

    installed = read_version(VERSION_FILE)
    result = {
        "skill": "transcript-to-flowchart",
        "installed": installed,
        "latest": None,
        "status": "installed",
        "update_command": UPDATE_COMMAND,
    }
    if args.check:
        try:
            latest = fetch_latest(args.timeout)
            result["latest"] = latest
            if version_tuple(installed) < version_tuple(latest):
                result["status"] = "outdated"
            elif version_tuple(installed) > version_tuple(latest):
                result["status"] = "ahead"
            else:
                result["status"] = "current"
        except (OSError, UnicodeError, ValueError, urllib.error.URLError) as exc:
            result["status"] = "check-unavailable"
            result["error"] = str(exc)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"Skill: {result['skill']}")
    print(f"Versión instalada: {result['installed']}")
    if args.check:
        if result["latest"]:
            print(f"Última versión publicada: {result['latest']}")
        print(f"Estado: {result['status']}")
        if result["status"] == "outdated":
            print(f"Actualizar con: {result['update_command']}")
        elif result["status"] == "check-unavailable":
            print(f"No fue posible consultar la versión remota: {result['error']}")


if __name__ == "__main__":
    main()
