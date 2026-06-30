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

"""Tests for text extraction — no model required."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from docscan.extractor import extract_text

FIXTURES = Path("tests/fixtures")


def test_extract_txt_receipt() -> None:
    text = extract_text(FIXTURES / "sample_receipt.txt")
    assert "WALMART" in text
    assert len(text) > 50


def test_extract_txt_medical() -> None:
    text = extract_text(FIXTURES / "sample_medical.txt")
    assert "Metformin" in text


def test_extract_txt_generic() -> None:
    text = extract_text(FIXTURES / "sample_generic.txt")
    assert "Acme Corp" in text


def test_unsupported_extension() -> None:
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(Path("fake.xyz"))


def test_extract_pdf(mocker: Any) -> None:
    mock_pdf = mocker.patch("docscan.extractor.pdfplumber")
    mock_page = mocker.MagicMock()
    mock_page.extract_text.return_value = "PDF text content"
    mock_pdf.open.return_value.__enter__.return_value.pages = [mock_page]
    result = extract_text(Path("test.pdf"))
    assert "PDF text content" in result


def test_extract_pdf_empty_raises(mocker: Any) -> None:
    mock_pdf = mocker.patch("docscan.extractor.pdfplumber")
    mock_pdf.open.return_value.__enter__.return_value.pages = []
    with pytest.raises(ValueError, match="PDF appears to be scanned"):
        extract_text(Path("empty.pdf"))


def test_extract_image(mocker: Any) -> None:
    mock_img = mocker.patch("docscan.extractor.Image")
    mock_img.open.return_value.convert.return_value = mock_img.open.return_value
    mock_tess = mocker.patch("docscan.extractor.pytesseract")
    mock_tess.image_to_string.return_value = "image text content"
    result = extract_text(Path("test.png"))
    assert "image text content" in result


def test_extract_image_empty_raises(mocker: Any) -> None:
    mock_img = mocker.patch("docscan.extractor.Image")
    mock_img.open.return_value.convert.return_value = mock_img.open.return_value
    mock_tess = mocker.patch("docscan.extractor.pytesseract")
    mock_tess.image_to_string.return_value = ""
    with pytest.raises(ValueError, match="OCR returned no text"):
        extract_text(Path("test.png"))
