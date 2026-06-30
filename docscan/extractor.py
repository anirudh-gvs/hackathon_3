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

"""
extractor.py — Extract raw text from PDF, image, or plain text files.
Offline only. No network calls.
"""

from __future__ import annotations

import re
from pathlib import Path

import pdfplumber
import pytesseract
from PIL import Image


def extract_text(path: Path) -> str:
    """
    Dispatch to the correct extractor based on file extension.
    Returns raw extracted text string.
    Raises ValueError for unsupported file types.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix in {".png", ".jpg", ".jpeg", ".tiff", ".bmp"}:
        return _extract_image(path)
    elif suffix == ".txt":
        return path.read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _extract_pdf(path: Path) -> str:
    """Extract text from all pages of a PDF using pdfplumber."""
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                pages.append(text.strip())
    if not pages:
        raise ValueError("PDF appears to be scanned or empty. Try converting to image first.")
    return "\n\n".join(pages)


def _extract_image(path: Path) -> str:
    """OCR an image using Tesseract. Preprocesses to grayscale for accuracy."""
    img = Image.open(path).convert("L")
    text = pytesseract.image_to_string(img)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text:
        raise ValueError("OCR returned no text. Check image quality.")
    return text
