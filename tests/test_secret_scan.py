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

from docscan.secret_scan import BAD_PATTERNS, scan_for_secrets


def test_scan_for_secrets_passes(tmp_path: pathlib.Path) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    inf = src / "inference.py"
    inf.write_text("# n_gpu_layers=0")
    other = src / "main.py"
    other.write_text("print('hello')")
    assert scan_for_secrets(str(src)) == 0


def test_scan_detects_secret_pattern(tmp_path: pathlib.Path) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    inf = src / "inference.py"
    inf.write_text("# n_gpu_layers=0")
    other = src / "main.py"
    other.write_text('api_key = "sk-1234"')
    assert scan_for_secrets(str(src)) == 1


def test_scan_missing_n_gpu_layers(tmp_path: pathlib.Path) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    inf = src / "inference.py"
    inf.write_text("# no n_gpu_layers here")
    other = src / "other.py"
    other.write_text("print('hello')")
    assert scan_for_secrets(str(src)) == 1


def test_bad_patterns_not_empty() -> None:
    assert len(BAD_PATTERNS) > 0
    assert "sk-" in BAD_PATTERNS
