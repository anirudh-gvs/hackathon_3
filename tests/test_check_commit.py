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
from typing import Any

from docscan.check_commit import (
    check_commit_message,
    check_license,
    check_required_files,
    run_checks,
)


def test_check_commit_message_valid() -> None:
    assert check_commit_message("feat(cli): add new feature")
    assert check_commit_message("fix: resolve crash")
    assert check_commit_message("docs(readme): update installation")


def test_check_commit_message_invalid() -> None:
    assert not check_commit_message("bad commit")
    assert not check_commit_message("")
    assert not check_commit_message("feat:ab")  # too short


def test_check_required_files_all_exist(tmp_path: pathlib.Path) -> None:
    for f in ["README.md", "CONTRIBUTING.md", "CHANGELOG.md", "LICENSE", "docs/spec.md"]:
        p = tmp_path / f
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("")
    missing = check_required_files(str(tmp_path))
    assert missing == []


def test_check_required_files_missing(tmp_path: pathlib.Path) -> None:
    missing = check_required_files(str(tmp_path))
    assert "README.md" in missing
    assert len(missing) == 5


def test_check_license_valid(tmp_path: pathlib.Path) -> None:
    lic = tmp_path / "LICENSE"
    lic.write_text("GNU AFFERO GENERAL PUBLIC LICENSE Version 3")
    toml = tmp_path / "pyproject.toml"
    toml.write_text('license = "AGPL-3.0-or-later"')
    assert check_license(str(tmp_path))


def test_check_license_invalid(tmp_path: pathlib.Path) -> None:
    lic = tmp_path / "LICENSE"
    lic.write_text("MIT License")
    assert not check_license(str(tmp_path))


def test_check_license_missing(tmp_path: pathlib.Path) -> None:
    assert not check_license(str(tmp_path))


def test_run_checks_passes(mocker: Any) -> None:
    mocker.patch(
        "docscan.check_commit.subprocess.check_output",
        return_value="feat(test): improve coverage\n",
    )
    mocker.patch("docscan.check_commit.pathlib.Path.exists", return_value=True)
    mocker.patch(
        "docscan.check_commit.pathlib.Path.read_text",
        side_effect=[
            "GNU AFFERO GENERAL PUBLIC LICENSE\nVersion 3\n",
            'license = "AGPL-3.0-or-later"\n',
        ],
    )
    assert run_checks() == 0


def test_run_checks_bad_commit(mocker: Any) -> None:
    mocker.patch(
        "docscan.check_commit.subprocess.check_output",
        return_value="bad message\n",
    )
    assert run_checks() == 1


def test_run_checks_no_git(mocker: Any) -> None:
    import subprocess

    mocker.patch(
        "docscan.check_commit.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "git"),
    )
    assert run_checks() == 1


def test_run_checks_missing_files(mocker: Any) -> None:
    mocker.patch(
        "docscan.check_commit.subprocess.check_output",
        return_value="feat(test): add tests\n",
    )
    mocker.patch("docscan.check_commit.pathlib.Path.exists", return_value=False)
    assert run_checks() == 1


def test_run_checks_bad_license(mocker: Any) -> None:
    mocker.patch(
        "docscan.check_commit.subprocess.check_output",
        return_value="feat(test): add tests\n",
    )
    mocker.patch("docscan.check_commit.pathlib.Path.exists", return_value=True)
    mocker.patch(
        "docscan.check_commit.pathlib.Path.read_text",
        return_value="MIT License",
    )
    assert run_checks() == 1
