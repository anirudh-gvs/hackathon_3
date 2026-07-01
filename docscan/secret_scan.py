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
import sys

BAD_PATTERNS = ["sk-", "glpat-", 'api_key = "', 'password = "']


def scan_for_secrets(source_dir: str = "docscan") -> int:
    """Scan source files for secret patterns and CPU-only enforcement.
    Returns 0 on success, 1 on failure.
    """
    skip = {"secret_scan.py", "check_commit.py", "ci_checks.py"}
    files = [f for f in pathlib.Path(source_dir).rglob("*.py") if f.name not in skip]
    found = False
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in BAD_PATTERNS:
            if pat in text:
                print(f"WARNING: secret pattern {pat!r} found in {f}")
                found = True
    inf_path = pathlib.Path(source_dir) / "inference.py"
    inf = inf_path.read_text(encoding="utf-8", errors="ignore")
    if "n_gpu_layers=0" not in inf:
        print("FAIL: n_gpu_layers=0 missing in inference.py")
        return 1
    print("CPU-only confirmed: n_gpu_layers=0 found")
    if found:
        print("FAIL: secrets detected in code")
        return 1
    print("secret-scanning passed")
    return 0


def main() -> None:
    sys.exit(scan_for_secrets())


if __name__ == "__main__":
    main()
