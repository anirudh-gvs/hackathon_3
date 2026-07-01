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
inference.py — Run local LLM inference via llama-cpp-python.
CPU-only. No network calls after model is loaded.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from docscan.schemas import (
    SCHEMA_DESCRIPTIONS,
    SCHEMA_MAP,
    GenericSchema,
    MedicalSchema,
    Medication,
    ReceiptSchema,
    SchemaName,
)

_MODEL_INSTANCE: Any = None
DEFAULT_MODEL_PATH = Path("models/phi3-mini-q4.gguf")


def _describe_fields(schema_cls: type) -> str:
    """Generate a simple field description from a Pydantic schema class."""
    lines = []
    for name, field in schema_cls.model_fields.items():  # type: ignore[attr-defined]
        field_type = field.annotation
        if hasattr(field_type, "__origin__"):
            origin = field_type.__origin__
            args = field_type.__args__
            if origin is list:
                inner = args[0].__name__ if hasattr(args[0], "__name__") else str(args[0])
                field_type_str = f"list[{inner}]"
            elif origin is dict:
                field_type_str = "dict"
            else:
                field_type_str = str(field_type)
        else:
            field_type_str = (
                field_type.__name__ if hasattr(field_type, "__name__") else str(field_type)
            )
        required = field.is_required()
        lines.append(f'  "{name}": {field_type_str}' + ("" if required else " (optional)"))
    return "\n".join(lines)


def load_model(model_path: Path = DEFAULT_MODEL_PATH, n_ctx: int = 4096) -> Any:
    """Load the GGUF model into memory. Cached after first call."""
    global _MODEL_INSTANCE
    if _MODEL_INSTANCE is None:
        from llama_cpp import Llama

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at {model_path}. Run: bash scripts/download_model.sh"
            )
        _MODEL_INSTANCE = Llama(
            model_path=str(model_path),
            n_ctx=n_ctx,
            n_threads=4,
            n_gpu_layers=0,
            verbose=False,
        )
    return _MODEL_INSTANCE


def build_prompt(text: str, schema_name: SchemaName) -> str:
    """Build the extraction prompt for the given schema."""
    schema_cls = SCHEMA_MAP[schema_name]
    doc_type = SCHEMA_DESCRIPTIONS[schema_name]
    fields = _describe_fields(schema_cls)

    return f"""<|user|>
Extract structured data from this document.

Document type: {doc_type}

Return ONLY valid JSON with these fields (no explanation, no markdown, no extra text):
{fields}

If a field cannot be determined, use null for optional fields or empty arrays.

DOCUMENT:
{text[:3000]}
<|end|>
<|assistant|>
{{"""


def run_inference(
    text: str,
    schema_name: SchemaName,
    model_path: Path = DEFAULT_MODEL_PATH,
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> dict[str, Any]:
    """
    Run local LLM inference and return validated structured data as a dict.
    Raises ValueError if the model output cannot be parsed or validated.
    """
    llm = load_model(model_path)
    prompt = build_prompt(text, schema_name)

    response = llm(
        prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        stop=["<|end|>", "<|user|>"],
    )

    raw = response["choices"][0]["text"].strip()
    if not raw.startswith("{"):
        raw = "{" + raw

    try:
        parsed = _parse_json(raw)
    except ValueError:
        parsed = _extract_partial(raw, schema_name)

    schema_cls = SCHEMA_MAP[schema_name]
    validated = schema_cls.model_validate(parsed)  # type: ignore[attr-defined]
    return validated.model_dump()  # type: ignore[no-any-return]


def quick_extract(text: str, schema_name: SchemaName) -> dict[str, Any]:
    """Keyword-based instant extraction - no AI model needed."""
    text_lower = text.lower()
    lines = text.strip().split("\n")
    first_line = lines[0] if lines else ""

    if schema_name == SchemaName.receipt:
        total = None
        tax = None
        vendor = first_line.strip() if first_line else None
        amounts = re.findall(r"[\$]?(\d+\.\d{2})", text)
        if amounts:
            for a in reversed(amounts):
                val = float(a)
                if val > 1:
                    if total is None:
                        total = val
                    elif tax is None and val < total * 0.5:
                        tax = val
        return ReceiptSchema(
            vendor=vendor[:50] if vendor else None,
            date="",
            total=total,
            tax=tax,
            payment_method="card"
            if "card" in text_lower
            else "cash"
            if "cash" in text_lower
            else None,
            line_items=[],
        ).model_dump()

    elif schema_name == SchemaName.medical:
        diagnosis = []
        medications = []
        patient_name = None
        for line in lines:
            lower_line = line.lower().strip()
            if "patient" in lower_line and ":" in lower_line:
                patient_name = line.split(":", 1)[1].strip()[:50]
            elif "diagnosis" in lower_line and ":" in lower_line:
                diag = line.split(":", 1)[1].strip()
                if diag:
                    diagnosis.append(diag[:100])
            elif "medication" in lower_line and ":" in lower_line:
                med_name = line.split(":", 1)[1].strip()[:50]
                if med_name:
                    medications.append(Medication(name=med_name))
        if not diagnosis:
            for word in [
                "fever",
                "cold",
                "cough",
                "infection",
                "pain",
                "diabetes",
                "hypertension",
                "asthma",
            ]:
                if word in text_lower:
                    diagnosis.append(word.title()[:100])
                    break
        return MedicalSchema(
            patient_name=patient_name,
            date="",
            diagnosis=diagnosis if diagnosis else None,
            medications=medications,
            doctor=None,
            notes=text[:200],
        ).model_dump()

    else:  # generic
        title = first_line.strip()[:80] if first_line else None
        sentences = re.split(r"[.!?\n]+", text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        key_facts = sentences[:5]
        return GenericSchema(
            title=title, summary=text[:200], key_facts=key_facts, entities=[], dates=[]
        ).model_dump()


def _fallback_extract(text: str, schema_name: SchemaName) -> dict[str, Any]:
    """Fallback extraction that returns a minimal valid dict without loading a model."""
    schema_cls = SCHEMA_MAP[schema_name]
    if schema_name == SchemaName.generic:
        return schema_cls(summary="").model_dump()  # type: ignore[no-any-return]
    return schema_cls().model_dump()  # type: ignore[no-any-return]


def _extract_json_balanced(text: str) -> str | None:
    """Extract the first balanced JSON object, handling braces inside strings."""
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    in_string = False
    escaped = False
    for i in range(start, len(text)):
        ch = text[i]
        if escaped:
            escaped = False
            continue
        if ch == "\\" and in_string:
            escaped = True
            continue
        if ch == '"' and not escaped:
            in_string = not in_string
            continue
        if not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None


def _repair_json(text: str) -> str:
    """Attempt to repair common JSON issues from LLM output."""
    text = text.strip()
    if text.endswith("..."):
        text = text[:-3].rstrip()
    if not text.endswith("}"):
        text += "}"
    text = re.sub(r",\s*}", "}", text)
    text = re.sub(r",\s*]", "]", text)
    text = re.sub(r':\s*"([^"]*)$', r': "\1"', text, flags=re.MULTILINE)
    return text


def _extract_partial(text: str, schema_name: SchemaName) -> dict[str, Any]:
    """Extract a safe partial dict from truncated model output."""
    result: dict[str, Any] = {}
    schema_cls = SCHEMA_MAP[schema_name]

    title_match = re.search(r'"title"\s*:\s*"([^"]*)"', text)
    if title_match:
        result["title"] = title_match.group(1)

    summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', text)
    if summary_match:
        result["summary"] = summary_match.group(1)

    if not result:
        return _fallback_extract(text, schema_name)

    try:
        return schema_cls.model_validate(result).model_dump()  # type: ignore[attr-defined, no-any-return]
    except Exception:
        return _fallback_extract(text, schema_name)


def _parse_json(text: str) -> dict[str, Any]:
    """Try to extract a JSON object from model output."""
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?", "", text)
    text = re.sub(r"\n?\s*```$", "", text)

    candidate = _extract_json_balanced(text)
    if not candidate:
        raise ValueError(f"No JSON object found in model output:\n{text[:300]}")

    try:
        return json.loads(candidate)  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        pass

    repaired = _repair_json(candidate)
    try:
        return json.loads(repaired)  # type: ignore[no-any-return]
    except json.JSONDecodeError:
        pass

    raise ValueError(f"Failed to parse JSON:\n{text[:500]}")
