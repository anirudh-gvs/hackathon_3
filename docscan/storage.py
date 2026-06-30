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

"""storage.py — SQLite-backed persistence for extraction results."""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from typing import Any


def init_db(db_path: str) -> None:
    """Create the results table if it doesn't exist."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_file TEXT NOT NULL,
            result_json TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
    conn.commit()
    conn.close()


def save_result(db_path: str, source_file: str, result: dict[str, Any]) -> None:
    """Insert an extraction result into the database."""
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT INTO results (source_file, result_json, created_at) VALUES (?, ?, ?)",
        (source_file, json.dumps(result), datetime.now(UTC).isoformat()),
    )
    conn.commit()
    conn.close()


def get_results(db_path: str) -> list[dict[str, Any]]:
    """Return all stored results as a list of dicts."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM results ORDER BY id").fetchall()
    results = []
    for row in rows:
        d = dict(row)
        d["result"] = json.loads(d.pop("result_json"))
        results.append(d)
    conn.close()
    return results


def delete_result(db_path: str, record_id: int) -> None:
    """Delete a result by its ID."""
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM results WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
