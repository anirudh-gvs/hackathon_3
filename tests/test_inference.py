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

import pytest

from docscan.inference import (
    _extract_json_balanced,
    _extract_partial,
    _fallback_extract,
    _parse_json,
    _repair_json,
    build_prompt,
    load_model,
    quick_extract,
    run_inference,
)
from docscan.schemas import SchemaName


def test_fallback_generic() -> None:
    result = _fallback_extract("Hello world meeting notes", SchemaName.generic)
    assert isinstance(result, dict)
    assert "summary" in result


def test_fallback_returns_dict() -> None:
    result = _fallback_extract("some text", SchemaName.receipt)
    assert isinstance(result, dict)


def test_fallback_medical() -> None:
    result = _fallback_extract("patient data", SchemaName.medical)
    assert isinstance(result, dict)
    assert "medications" in result


def test_parse_json_valid() -> None:
    result = _parse_json('{"summary": "test"}')
    assert result == {"summary": "test"}


def test_parse_json_nested_braces() -> None:
    result = _parse_json('{"key": "val"}')
    assert result == {"key": "val"}


def test_parse_json_no_json_raises() -> None:
    with pytest.raises(ValueError, match="No JSON object found"):
        _parse_json("just plain text")


def test_parse_json_invalid_json_raises() -> None:
    with pytest.raises(ValueError, match="Failed to parse JSON"):
        _parse_json("{invalid}")


def test_build_prompt_contains_schema() -> None:
    prompt = build_prompt("test doc", SchemaName.generic)
    assert "summary" in prompt
    assert "test doc" in prompt


def test_build_prompt_all_schemas() -> None:
    for schema in SchemaName:
        prompt = build_prompt("sample text", schema)
        assert "sample text" in prompt
        assert schema.value in prompt or "Extract" in prompt


def test_load_model_not_found(mocker: Any) -> None:
    import sys

    import docscan.inference as inf_mod

    original = inf_mod._MODEL_INSTANCE
    inf_mod._MODEL_INSTANCE = None
    sys.modules["llama_cpp"] = mocker.MagicMock()
    fake_path = Path("nonexistent_model.gguf")
    with pytest.raises(FileNotFoundError, match="Model not found"):
        load_model(fake_path)
    inf_mod._MODEL_INSTANCE = original
    del sys.modules["llama_cpp"]


def test_run_inference_success(mocker: Any) -> None:
    mock_llm = mocker.MagicMock()
    mock_llm.return_value = {
        "choices": [{"text": '"summary": "works"}'}],
    }
    mocker.patch("docscan.inference.load_model", return_value=mock_llm)
    result = run_inference("some text", SchemaName.generic, Path("fake.gguf"))
    assert isinstance(result, dict)
    assert result["summary"] == "works"


def test_run_inference_invalid_json(mocker: Any) -> None:
    mock_llm = mocker.MagicMock()
    mock_llm.return_value = {
        "choices": [{"text": "not valid json at all"}],
    }
    mocker.patch("docscan.inference.load_model", return_value=mock_llm)
    result = run_inference("some text", SchemaName.generic, Path("fake.gguf"))
    assert isinstance(result, dict)
    assert "summary" in result


def test_repair_json_trailing_dots() -> None:
    result = _repair_json('{"summary": "test"...')
    assert result == '{"summary": "test"}'


def test_repair_json_missing_brace() -> None:
    result = _repair_json('{"summary": "test"')
    assert result == '{"summary": "test"}'


def test_repair_json_trailing_comma() -> None:
    result = _repair_json('{"summary": "test",}')
    assert '"summary": "test"' in result
    assert ",}" not in result


def test_extract_json_balanced_simple() -> None:
    result = _extract_json_balanced('{"a": 1}')
    assert result == '{"a": 1}'


def test_extract_json_balanced_nested() -> None:
    result = _extract_json_balanced('{"a": {"b": 2}}')
    assert result == '{"a": {"b": 2}}'


def test_extract_json_balanced_no_brace() -> None:
    result = _extract_json_balanced("plain text")
    assert result is None


def test_extract_json_balanced_with_prefix() -> None:
    result = _extract_json_balanced('prefix {"a": 1} suffix')
    assert result == '{"a": 1}'


def test_extract_json_balanced_string_with_braces() -> None:
    result = _extract_json_balanced('{"a": "text { with brace"}')
    assert result is not None


def test_extract_partial_title_only() -> None:

    result = _extract_partial('{"title": "My Doc"', SchemaName.generic)
    assert isinstance(result, dict)
    assert result.get("title") is None
    assert "summary" in result


def test_extract_partial_with_summary() -> None:

    result = _extract_partial('{"title": "My Doc", "summary": "A document"', SchemaName.generic)
    assert isinstance(result, dict)
    assert result.get("title") == "My Doc"
    assert result.get("summary") == "A document"


def test_extract_partial_empty_fallback() -> None:

    result = _extract_partial("no json at all", SchemaName.generic)
    assert isinstance(result, dict)
    assert "summary" in result


def test_quick_extract_receipt() -> None:
    result = quick_extract("Store Name\nItem $10.00\nTotal $10.00", SchemaName.receipt)
    assert isinstance(result, dict)
    assert "vendor" in result


def test_quick_extract_medical() -> None:
    result = quick_extract("Patient: John\nDiagnosis: Fever", SchemaName.medical)
    assert isinstance(result, dict)
    assert "diagnosis" in result


def test_quick_extract_generic() -> None:
    result = quick_extract("Hello World\nThis is a document", SchemaName.generic)
    assert isinstance(result, dict)
    assert "summary" in result


def test_quick_extract_medical_diagnosis_fallback() -> None:
    result = quick_extract("Patient has fever and cough", SchemaName.medical)
    assert isinstance(result, dict)
    assert result.get("diagnosis") == ["Fever"]


def test_quick_extract_medical_medication() -> None:
    result = quick_extract("Patient: Alice\nMedication: Amoxicillin", SchemaName.medical)
    assert isinstance(result, dict)
    assert result.get("patient_name") == "Alice"


def test_quick_extract_receipt_with_amounts() -> None:
    """Test quick_extract receipt with dollar amounts."""
    result = quick_extract("Store XYZ\nItem $25.50\nItem $10.00\nTotal $35.50", SchemaName.receipt)
    assert isinstance(result, dict)
    assert result.get("vendor") == "Store XYZ"


def test_quick_extract_receipt_with_card() -> None:
    """Test quick_extract detects payment method."""
    result = quick_extract("Store\nPaid by credit card\nTotal $50.00", SchemaName.receipt)
    assert result.get("payment_method") == "card"


def test_quick_extract_receipt_with_cash() -> None:
    """Test quick_extract detects cash payment."""
    result = quick_extract("Store\nPaid in cash\nTotal $20.00", SchemaName.receipt)
    assert result.get("payment_method") == "cash"


def test_describe_fields_generic() -> None:
    """Test _describe_fields produces field descriptions."""
    from docscan.inference import _describe_fields
    from docscan.schemas import GenericSchema

    result = _describe_fields(GenericSchema)
    assert "summary" in result
    assert "title" in result
    assert "key_facts" in result


def test_describe_fields_receipt() -> None:
    """Test _describe_fields for receipt schema."""
    from docscan.inference import _describe_fields
    from docscan.schemas import ReceiptSchema

    result = _describe_fields(ReceiptSchema)
    assert "vendor" in result
    assert "total" in result
