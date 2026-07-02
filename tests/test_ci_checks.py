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

import pytest

from docscan.ci_checks import (
    COPYRIGHT_LINE,
    LICENSE_HEADER_SNIPPET,
    SPDX_LINE,
    check_commit,
    check_license_headers,
    check_secrets,
    check_toml,
)


def test_check_toml_valid(tmp_path: pathlib.Path, mocker: Any) -> None:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text('[project]\nlicense = { text = "AGPL-3.0-or-later" }\nname = "test"')
    mocker.patch("docscan.ci_checks.pathlib.Path.read_text", return_value=toml_path.read_text())
    mocker.patch("docscan.ci_checks.pathlib.Path", return_value=toml_path)
    check_toml()


def test_check_toml_invalid(tmp_path: pathlib.Path, mocker: Any) -> None:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text("[[[invalid]]]")
    mocker.patch("docscan.ci_checks.pathlib.Path", return_value=toml_path)
    with pytest.raises(SystemExit):
        check_toml()


def test_check_secrets_passes(mocker: Any) -> None:
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.rglob",
        return_value=[pathlib.Path("docscan/inference.py")],
    )
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.read_text", return_value='n_gpu_layers=0\nprint("ok")'
    )
    check_secrets()


def test_check_secrets_finds_pattern(mocker: Any) -> None:
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.rglob",
        return_value=[pathlib.Path("docscan/bad.py")],
    )
    mocker.patch("docscan.ci_checks.pathlib.Path.read_text", return_value="sk-12345")
    with pytest.raises(SystemExit):
        check_secrets()


def test_check_secrets_missing_cpu_only(mocker: Any) -> None:
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.rglob",
        return_value=[pathlib.Path("docscan/other.py")],
    )
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.read_text",
        side_effect=lambda *a, **_: "no gpu layers here",
    )
    with pytest.raises(SystemExit):
        check_secrets()


def test_check_secrets_network_call(mocker: Any) -> None:
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.rglob",
        return_value=[pathlib.Path("docscan/has_network.py")],
    )
    # read_text calls: 1) rglob loop, 2) inference.py, 3) network loop
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.read_text",
        side_effect=[
            "n_gpu_layers=0",
            "n_gpu_layers=0",
            'requests.get("http://example.com")',
        ],
    )
    with pytest.raises(SystemExit):
        check_secrets()


def test_check_commit_passes(mocker: Any) -> None:
    mocker.patch(
        "docscan.ci_checks.subprocess.check_output",
        return_value="feat(cli): add new feature\n",
    )
    exists_mock = mocker.patch("docscan.ci_checks.pathlib.Path.exists", return_value=True)
    mocker.patch(
        "docscan.ci_checks.pathlib.Path.read_text",
        side_effect=[
            "GNU AFFERO GENERAL PUBLIC LICENSE\nVersion 3\n",
            'license = { text = "AGPL-3.0-or-later" }\n',
        ],
    )
    check_commit()
    assert exists_mock.call_count == 5


def test_check_commit_bad_format(mocker: Any) -> None:
    mocker.patch(
        "docscan.ci_checks.subprocess.check_output",
        return_value="bad commit message\n",
    )
    with pytest.raises(SystemExit):
        check_commit()


def test_check_commit_no_git(mocker: Any) -> None:
    import subprocess

    mocker.patch(
        "docscan.ci_checks.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "git"),
    )
    with pytest.raises(SystemExit):
        check_commit()


def test_check_license_headers_passes(tmp_path: pathlib.Path, mocker: Any) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    f = src / "good.py"
    f.write_text(f"{COPYRIGHT_LINE}\n{SPDX_LINE}\n{LICENSE_HEADER_SNIPPET}\n\nprint('ok')")
    mocker.patch("docscan.ci_checks.pathlib.Path.rglob", return_value=[f])
    mocker.patch("docscan.ci_checks.pathlib.Path.glob", return_value=[])
    check_license_headers()


def test_check_license_headers_missing_spdx(tmp_path: pathlib.Path, mocker: Any) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    f = src / "bad.py"
    f.write_text(f"{COPYRIGHT_LINE}\n{LICENSE_HEADER_SNIPPET}\n\nprint('ok')")
    mocker.patch("docscan.ci_checks.pathlib.Path.rglob", return_value=[f])
    mocker.patch("docscan.ci_checks.pathlib.Path.glob", return_value=[])
    with pytest.raises(SystemExit):
        check_license_headers()


def test_check_license_headers_missing_copyright(tmp_path: pathlib.Path, mocker: Any) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    f = src / "bad.py"
    f.write_text(f"{SPDX_LINE}\n{LICENSE_HEADER_SNIPPET}\n\nprint('ok')")
    mocker.patch("docscan.ci_checks.pathlib.Path.rglob", return_value=[f])
    mocker.patch("docscan.ci_checks.pathlib.Path.glob", return_value=[])
    with pytest.raises(SystemExit):
        check_license_headers()


def test_check_license_headers_missing_boilerplate(tmp_path: pathlib.Path, mocker: Any) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    f = src / "bad.py"
    f.write_text(f"{COPYRIGHT_LINE}\n{SPDX_LINE}\n\nprint('ok')")
    mocker.patch("docscan.ci_checks.pathlib.Path.rglob", return_value=[f])
    mocker.patch("docscan.ci_checks.pathlib.Path.glob", return_value=[])
    with pytest.raises(SystemExit):
        check_license_headers()


def test_check_license_headers_skips_files(tmp_path: pathlib.Path, mocker: Any) -> None:
    src = tmp_path / "docscan"
    src.mkdir()
    f = src / "ci_checks.py"  # in skip list
    f.write_text("no header here")
    mocker.patch("docscan.ci_checks.pathlib.Path.rglob", return_value=[f])
    mocker.patch("docscan.ci_checks.pathlib.Path.glob", return_value=[])
    check_license_headers()


def test_check_license_headers_catches_root_file(tmp_path: pathlib.Path, mocker: Any) -> None:
    root_file = tmp_path / "app.py"
    root_file.write_text("print('no license header')")
    mocker.patch("docscan.ci_checks.pathlib.Path.rglob", return_value=[])
    mocker.patch("docscan.ci_checks.pathlib.Path.glob", return_value=[root_file])
    with pytest.raises(SystemExit):
        check_license_headers()
