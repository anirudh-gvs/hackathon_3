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

from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from docscan.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "DocScan CLI" in result.stdout


def test_scan_file_not_found() -> None:
    result = runner.invoke(app, ["scan", "nonexistent.pdf"])
    assert result.exit_code == 1
    assert "File not found" in result.stdout


def test_scan_txt_inference_fails(tmp_path: Path, mocker: Any) -> None:
    mocker.patch("docscan.cli.run_inference", side_effect=ValueError("model crashed"))
    txt = tmp_path / "test.txt"
    txt.write_text("Hello world")
    result = runner.invoke(app, ["scan", str(txt), "-s", "generic"])
    assert result.exit_code == 1
    assert "Inference failed" in result.stdout


def test_scan_verbose(tmp_path: Path, mocker: Any) -> None:
    mock_result = {"summary": "test", "key_facts": []}
    mocker.patch("docscan.cli.extract_text", return_value="Hello world content here")
    mocker.patch("docscan.cli.run_inference", return_value=mock_result)
    txt = tmp_path / "test.txt"
    txt.write_text("dummy")
    result = runner.invoke(app, ["scan", str(txt), "-s", "generic", "--verbose"])
    assert result.exit_code == 0
    assert "Extracted Text" in result.stdout
    assert "Hello world" in result.stdout


def test_scan_output_file(tmp_path: Path, mocker: Any) -> None:
    mock_result = {"summary": "output test", "key_facts": []}
    mocker.patch("docscan.cli.extract_text", return_value="Some text")
    mocker.patch("docscan.cli.run_inference", return_value=mock_result)
    txt = tmp_path / "input.txt"
    txt.write_text("dummy")
    out = tmp_path / "out.json"
    result = runner.invoke(app, ["scan", str(txt), "-s", "generic", "-o", str(out)])
    assert result.exit_code == 0
    assert "Saved to" in result.stdout
    assert out.read_text(encoding="utf-8") == '{\n  "summary": "output test",\n  "key_facts": []\n}'


def test_scan_stdout(tmp_path: Path, mocker: Any) -> None:
    mock_result = {"summary": "stdout test", "key_facts": ["fact1"]}
    mocker.patch("docscan.cli.extract_text", return_value="Some text")
    mocker.patch("docscan.cli.run_inference", return_value=mock_result)
    txt = tmp_path / "input.txt"
    txt.write_text("dummy")
    result = runner.invoke(app, ["scan", str(txt), "-s", "generic"])
    assert result.exit_code == 0
    assert "stdout test" in result.stdout
    assert "Inference complete" in result.stdout


def test_scan_extraction_failure(tmp_path: Path, mocker: Any) -> None:
    mocker.patch("docscan.cli.extract_text", side_effect=ValueError("bad file"))
    txt = tmp_path / "bad.txt"
    txt.write_text("dummy")
    result = runner.invoke(app, ["scan", str(txt), "-s", "generic"])
    assert result.exit_code == 1
    assert "Extraction failed" in result.stdout


def test_scan_model_not_found(tmp_path: Path, mocker: Any) -> None:
    mocker.patch("docscan.cli.extract_text", return_value="Some text")
    mocker.patch(
        "docscan.cli.run_inference",
        side_effect=FileNotFoundError("model file not found"),
    )
    txt = tmp_path / "input.txt"
    txt.write_text("dummy")
    result = runner.invoke(app, ["scan", str(txt), "-s", "generic"])
    assert result.exit_code == 1
    assert "Model not found" in result.stdout


def test_main_entry(mocker: Any) -> None:
    mock_app = mocker.patch("docscan.cli.app")
    import docscan.cli as cli

    cli.app()
    mock_app.assert_called_once()
