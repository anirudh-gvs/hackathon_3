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

from docscan.schemas import (
    SCHEMA_DESCRIPTIONS,
    SCHEMA_MAP,
    Entity,
    GenericSchema,
    LineItem,
    MedicalSchema,
    Medication,
    ReceiptSchema,
    SchemaName,
)


def test_receipt_schema_partial() -> None:
    r = ReceiptSchema(vendor="Walmart", total=18.86, line_items=[])
    assert r.vendor == "Walmart"
    assert r.total == 18.86


def test_medical_schema_empty_lists() -> None:
    m = MedicalSchema()
    assert m.medications == []
    assert m.diagnosis == []


def test_generic_schema_required_summary() -> None:
    g = GenericSchema(summary="Board meeting notes", key_facts=["Budget $2.4M"])
    assert "Budget" in g.key_facts[0]


def test_receipt_full() -> None:
    r = ReceiptSchema(
        vendor="Costco",
        date="2024-01-15",
        total=150.75,
        tax=12.50,
        payment_method="Visa",
        line_items=[
            LineItem(description="Item A", quantity=2, unit_price=10.0, total=20.0),
            LineItem(description="Item B", quantity=1, unit_price=30.0, total=30.0),
        ],
    )
    assert r.vendor == "Costco"
    assert len(r.line_items) == 2
    assert r.line_items[0].description == "Item A"


def test_medical_full() -> None:
    m = MedicalSchema(
        patient_name="John Doe",
        date="2024-03-01",
        diagnosis=["Hypertension", "Type 2 Diabetes"],
        medications=[Medication(name="Metformin", dosage="500mg", frequency="twice daily")],
        doctor="Dr. Smith",
        notes="Follow up in 3 months",
    )
    assert m.patient_name == "John Doe"
    assert len(m.medications) == 1
    assert m.medications[0].name == "Metformin"


def test_generic_full() -> None:
    g = GenericSchema(
        title="Meeting Notes",
        summary="Discussed Q1 results",
        key_facts=["Revenue up 20%"],
        entities=[Entity(text="Acme Corp", label="ORG"), Entity(text="Alice", label="PERSON")],
        dates=["2024-01-10"],
    )
    assert g.title == "Meeting Notes"
    assert len(g.entities) == 2
    assert g.entities[0].label == "ORG"


def test_line_item_defaults() -> None:
    li = LineItem(description="Test")
    assert li.quantity is None
    assert li.unit_price is None
    assert li.total is None


def test_schema_name_enum_values() -> None:
    assert SchemaName.receipt.value == "receipt"
    assert SchemaName.medical.value == "medical"
    assert SchemaName.generic.value == "generic"


def test_schema_name_members() -> None:
    assert set(SchemaName) == {SchemaName.receipt, SchemaName.medical, SchemaName.generic}


def test_schema_map_keys() -> None:
    assert set(SCHEMA_MAP) == {SchemaName.receipt, SchemaName.medical, SchemaName.generic}


def test_schema_map_values() -> None:
    assert SCHEMA_MAP[SchemaName.receipt] == ReceiptSchema
    assert SCHEMA_MAP[SchemaName.medical] == MedicalSchema
    assert SCHEMA_MAP[SchemaName.generic] == GenericSchema


def test_schema_descriptions() -> None:
    assert set(SCHEMA_DESCRIPTIONS) == {SchemaName.receipt, SchemaName.medical, SchemaName.generic}
    assert "receipt" in SCHEMA_DESCRIPTIONS[SchemaName.receipt]
    assert "medical" in SCHEMA_DESCRIPTIONS[SchemaName.medical]
