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

"""Tests for the Flask app module."""

from __future__ import annotations

import io
import json
import tempfile
from pathlib import Path

import pytest

from app import allowed_file, app, get_file_type, infer_doc_type


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    app.config["UPLOAD_FOLDER"] = Path(tempfile.mkdtemp())
    with app.test_client() as client:
        yield client


def test_index_returns_html(client):
    """Test the index route returns HTML."""
    rv = client.get("/")
    assert rv.status_code == 200
    assert b"Offline DocScan" in rv.data


def test_allowed_file_valid():
    """Test allowed file extensions."""
    assert allowed_file("test.pdf") is True
    assert allowed_file("test.png") is True
    assert allowed_file("test.jpg") is True
    assert allowed_file("test.txt") is True
    assert allowed_file("test.bmp") is True


def test_allowed_file_invalid():
    """Test invalid file extensions."""
    assert allowed_file("test.exe") is False
    assert allowed_file("test.mp3") is False
    assert allowed_file("test") is False


def test_get_file_type():
    """Test file type detection."""
    assert get_file_type("test.pdf") == "PDF"
    assert get_file_type("test.png") == "Image"
    assert get_file_type("test.jpg") == "Image"
    assert get_file_type("test.txt") == "Text"
    assert get_file_type("test.unknown") == "Unknown"


def test_infer_doc_type_generic_document():
    """Test generic schema returns Document when no title."""
    result = infer_doc_type("generic", {})
    assert result == "Document"


def test_infer_doc_type_generic_invoice():
    """Test generic schema detects Invoice from title."""
    result = infer_doc_type("generic", {"title": "Invoice #123"})
    assert result == "Invoice"


def test_infer_doc_type_generic_receipt():
    """Test generic schema detects Receipt from title."""
    result = infer_doc_type("generic", {"title": "Receipt from Store"})
    assert result == "Receipt"


def test_infer_doc_type_generic_report():
    """Test generic schema detects Report from title."""
    result = infer_doc_type("generic", {"title": "Annual Report 2024"})
    assert result == "Report"


def test_infer_doc_type_medical():
    """Test medical schema."""
    result = infer_doc_type("medical", {})
    assert result == "Medical Report"


def test_infer_doc_type_receipt():
    """Test receipt schema returns Receipt."""
    result = infer_doc_type("receipt", {"vendor": "Store"})
    assert result == "Receipt"


def test_infer_doc_type_receipt_invoice():
    """Test receipt schema detects Invoice from vendor."""
    result = infer_doc_type("receipt", {"vendor": "INVOICE Corp"})
    assert result == "Invoice"


def test_infer_doc_type_receipt_bill():
    """Test receipt schema detects Bill from title."""
    result = infer_doc_type("receipt", {"title": "Bill of Sale"})
    assert result == "Invoice"


def test_api_scan_no_file(client):
    """Test /api/scan with no file returns 400."""
    rv = client.post("/api/scan")
    assert rv.status_code == 400
    assert b"No file provided" in rv.data


def test_api_scan_empty_filename(client):
    """Test /api/scan with empty filename returns 400."""
    rv = client.post("/api/scan", data={"file": (io.BytesIO(b""), "")})
    assert rv.status_code == 400


def test_api_scan_invalid_extension(client):
    """Test /api/scan with invalid file extension returns 400."""
    rv = client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"test"), "test.exe"),
        },
    )
    assert rv.status_code == 400


def test_api_scan_invalid_schema(client):
    """Test /api/scan with invalid schema returns 400."""
    rv = client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"test"), "test.txt"),
            "schema": "invalid_schema",
        },
    )
    assert rv.status_code == 400


def test_api_scan_quick_mode(client):
    """Test /api/scan with quick mode returns successfully."""
    rv = client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"Hello world test document"), "test.txt"),
            "schema": "generic",
            "mode": "quick",
        },
    )
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["success"] is True
    assert "result" in data
    assert data["mode"] == "quick"


def test_api_scan_receipt_quick(client):
    """Test /api/scan with receipt schema in quick mode."""
    rv = client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"INVOICE\nABC Corp\nTotal $100.00"), "invoice.txt"),
            "schema": "receipt",
            "mode": "quick",
        },
    )
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["record"]["doc_type"] == "Invoice"


def test_api_history_empty(client):
    """Test /api/history returns empty list initially."""
    rv = client.get("/api/history")
    assert rv.status_code == 200
    assert isinstance(json.loads(rv.data), list)


def test_api_history_after_scan(client):
    """Test /api/history returns records after a scan."""
    client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"test document"), "test.txt"),
            "schema": "generic",
            "mode": "quick",
        },
    )
    rv = client.get("/api/history")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


def test_api_stats(client):
    """Test /api/stats returns valid statistics."""
    rv = client.get("/api/stats")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert "total_documents" in data
    assert "success_rate" in data
    assert "by_doc_type" in data
    assert "by_schema" in data


def test_api_delete_history(client):
    """Test deleting a history record."""
    # First create a record
    client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"test"), "test.txt"),
            "schema": "generic",
            "mode": "quick",
        },
    )
    rv = client.get("/api/history")
    records = json.loads(rv.data)
    if records:
        record_id = records[0]["id"]
        rv = client.delete(f"/api/history/{record_id}")
        assert rv.status_code == 200
        assert json.loads(rv.data)["success"] is True


def test_api_scan_with_mode_formdata(client):
    """Test /api/scan processes mode from form data."""
    rv = client.post(
        "/api/scan",
        data={
            "file": (io.BytesIO(b"Patient Name: John\nDiagnosis: Fever"), "medical.txt"),
            "schema": "medical",
            "mode": "quick",
        },
    )
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert "result" in data
    assert data["record"]["doc_type"] == "Medical Report"
