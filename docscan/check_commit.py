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
import subprocess  # nosec B404
import sys

REQUIRED_FILES = ["README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "docs/spec.md"]
COMMIT_PATTERN = r"^(feat|fix|docs|style|refactor|test|chore|ci|perf|build|revert)(\(.+\))?: .{3,}"


def check_commit_message(msg: str) -> bool:
    """Validate a single commit message against Conventional Commits format."""
    return bool(re.match(COMMIT_PATTERN, msg))


def check_required_files(base: str = ".") -> list[str]:
    """Check that all required files exist. Returns list of missing files."""
    missing = []
    for f in REQUIRED_FILES:
        if not pathlib.Path(base, f).exists():
            missing.append(f)
    return missing


def check_license(base: str = ".") -> bool:
    """Validate LICENSE file is AGPL-3.0 and pyproject.toml has correct SPDX identifier."""
    try:
        lic = pathlib.Path(base, "LICENSE").read_text(encoding="utf-8")
        if "GNU AFFERO GENERAL PUBLIC LICENSE" not in lic or "Version 3" not in lic:
            return False
    except FileNotFoundError:
        return False
    try:
        toml = pathlib.Path(base, "pyproject.toml").read_text(encoding="utf-8")
        if 'license = { text = "AGPL-3.0-or-later" }' not in toml:
            return False
    except FileNotFoundError:
        return False
    return True


def run_checks() -> int:
    """Run all commit checks. Returns 0 on success, 1 on failure."""
    try:
        msg = subprocess.check_output(  # nosec B603 B607
            ["git", "log", "-1", "--pretty=%s"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except subprocess.CalledProcessError:
        print("FAIL: could not read git log")
        return 1
    print(f"Last commit: {msg}")

    if not check_commit_message(msg):
        print(f"FAIL: Not Conventional Commits format: {msg}")
        return 1
    print("Commit message valid")

    missing = check_required_files()
    if missing:
        for f in missing:
            print(f"FAIL: {f} missing")
        return 1
    for f in REQUIRED_FILES:
        print(f"OK: {f}")

    if not check_license():
        print("FAIL: LICENSE is not AGPL-3.0")
        return 1

    print("commit-quality passed")
    return 0


def main() -> None:
    sys.exit(run_checks())


if __name__ == "__main__":
    main()
