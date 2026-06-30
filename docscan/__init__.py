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

"""docscan-cli: Offline-first, CPU-only document-to-structured-JSON tool.

Uses pdfplumber (PDF), tesseract (image OCR), and llama-cpp-python
(CPU inference with Mistral-7B-Instruct-v0.2 Q4_K_M) to extract
structured data from unstructured documents with zero network calls.
"""

from __future__ import annotations

__version__ = "0.1.0"
