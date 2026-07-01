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

from docscan.storage import get_results, init_db, save_result


def test_save_and_retrieve(tmp_path: pathlib.Path) -> None:
    db_path = tmp_path / "test.db"
    init_db(str(db_path))
    save_result(
        str(db_path),
        "test_file.pdf",
        {"summary": "test", "source_type": "generic", "file": "test_file.pdf"},
    )
    results = get_results(str(db_path))
    assert len(results) == 1
    assert results[0]["source_file"] == "test_file.pdf"


def test_get_results_empty_db(tmp_path: pathlib.Path) -> None:
    db_path = tmp_path / "empty.db"
    init_db(str(db_path))
    results = get_results(str(db_path))
    assert results == []


def test_multiple_saves(tmp_path: pathlib.Path) -> None:
    db_path = tmp_path / "multi.db"
    init_db(str(db_path))
    for i in range(3):
        save_result(
            str(db_path),
            f"file{i}.pdf",
            {"summary": f"test{i}", "source_type": "generic"},
        )
    results = get_results(str(db_path))
    assert len(results) == 3
