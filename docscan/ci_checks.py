# Copyright (C) 2024 DocScan Team
# SPDX-License-Identifier: AGPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
import tomllib


def check_toml() -> None:
    """Validate pyproject.toml syntax and license field."""
    text = pathlib.Path("pyproject.toml").read_text(encoding="utf-8")
    try:
        tomllib.loads(text)
        print("OK: pyproject.toml is valid TOML")
    except Exception as exc:
        print(f"FAIL: pyproject.toml invalid: {exc}")
        sys.exit(1)
    if 'license = "AGPL-3.0-or-later"' not in text:
        print(
            'FAIL: pyproject.toml license field must be SPDX string: license = "AGPL-3.0-or-later"'
        )
        sys.exit(1)
    print("OK: pyproject.toml has correct AGPL-3.0-or-later SPDX identifier")


def check_secrets() -> None:
    """Check for hardcoded secrets, CPU-only enforcement, and no network calls."""
    skip = {"secret_scan.py", "check_commit.py", "ci_checks.py"}
    files = [f for f in pathlib.Path("docscan").rglob("*.py") if f.name not in skip]
    found = False
    bad = ["sk-", "glpat-", "PRIVATE_KEY", "api_secret"]
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in bad:
            if pat in text:
                print(f"WARNING: pattern {pat!r} in {f.name}")
                found = True
    inf = pathlib.Path("docscan/inference.py").read_text(encoding="utf-8", errors="ignore")
    if "n_gpu_layers=0" not in inf:
        print("FAIL: n_gpu_layers=0 missing in inference.py")
        sys.exit(1)
    print("OK: CPU-only enforcement confirmed (n_gpu_layers=0 present)")
    net_pats = ["requests.get", "requests.post", "urllib.request.urlopen"]
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in net_pats:
            if pat in text:
                print(f"FAIL: network call {pat!r} in {f.name}")
                found = True
    if found:
        sys.exit(1)
    print("secret-scanning passed")


def check_commit() -> None:
    """Validate commit message format and required repo files."""
    try:
        msg = subprocess.check_output(
            ["git", "log", "-1", "--pretty=%s"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        print("FAIL: could not read git log")
        sys.exit(1)
    print(f"Last commit: {msg}")
    pattern = r"^(feat|fix|docs|style|refactor|test|chore|ci|perf|build|revert)" r"(\(.+\))?: .{3,}"
    if not re.match(pattern, msg):
        print(f"FAIL: Not Conventional Commits format: {msg}")
        sys.exit(1)
    print("OK: commit message valid")
    required = [
        "README.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "LICENSE",
        "docs/spec.md",
    ]
    for fname in required:
        if pathlib.Path(fname).exists():
            print(f"OK: {fname}")
        else:
            print(f"FAIL: {fname} missing")
            sys.exit(1)
    lic = pathlib.Path("LICENSE").read_text(encoding="utf-8")
    if "GNU AFFERO GENERAL PUBLIC LICENSE" not in lic or "Version 3" not in lic:
        print("FAIL: LICENSE is not AGPL-3.0")
        sys.exit(1)
    toml = pathlib.Path("pyproject.toml").read_text(encoding="utf-8")
    if 'license = "AGPL-3.0-or-later"' not in toml:
        print('FAIL: pyproject.toml license must be SPDX string: license = "AGPL-3.0-or-later"')
        sys.exit(1)
    print("commit-quality passed")


SPDX_LINE = "SPDX-License-Identifier: AGPL-3.0-or-later"
COPYRIGHT_LINE = "Copyright (C) 2024 DocScan Team"
LICENSE_HEADER_SNIPPET = "This program is free software: you can redistribute it and/or modify"


def check_license_headers() -> None:
    """Verify all Python files have the required AGPLv3 header and SPDX identifier."""
    skip = {"secret_scan.py", "check_commit.py", "ci_checks.py"}
    files = (
        list(pathlib.Path("docscan").rglob("*.py"))
        + list(pathlib.Path("tests").rglob("*.py"))
        + [p for p in pathlib.Path(".").glob("*.py") if p.is_file()]
    )
    failed = False
    for f in files:
        if f.name in skip:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        if SPDX_LINE not in text:
            print(f"FAIL: missing SPDX identifier in {f}")
            failed = True
        if COPYRIGHT_LINE not in text:
            print(f"FAIL: missing copyright notice in {f}")
            failed = True
        if LICENSE_HEADER_SNIPPET not in text:
            print(f"FAIL: missing license boilerplate in {f}")
            failed = True
    if failed:
        print("FAIL: one or more files are missing required license headers")
        sys.exit(1)
    print("OK: all Python files have required license headers")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    commands = {
        "toml": check_toml,
        "secrets": check_secrets,
        "commit": check_commit,
        "license-headers": check_license_headers,
    }
    if cmd not in commands:
        print("Usage: ci_checks.py [toml|secrets|commit|license-headers]")
        sys.exit(1)
    commands[cmd]()
