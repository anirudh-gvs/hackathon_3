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
schemas.py — Pydantic output schemas for structured extraction.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class SchemaName(StrEnum):
    receipt = "receipt"
    medical = "medical"
    generic = "generic"


class LineItem(BaseModel):
    description: str
    quantity: float | None = None
    unit_price: float | None = None
    total: float | None = None


class ReceiptSchema(BaseModel):
    vendor: str | None = Field(None, description="Store or vendor name")
    date: str | None = Field(None, description="Transaction date (ISO 8601 if possible)")
    total: float | None = Field(None, description="Total amount paid")
    tax: float | None = Field(None, description="Tax amount")
    payment_method: str | None = Field(None, description="Cash, card, UPI, etc.")
    line_items: list[LineItem] = Field(default_factory=list)


class Medication(BaseModel):
    name: str
    dosage: str | None = None
    frequency: str | None = None


class MedicalSchema(BaseModel):
    patient_name: str | None = None
    date: str | None = None
    diagnosis: list[str] | None = Field(default_factory=list)
    medications: list[Medication] = Field(default_factory=list)
    doctor: str | None = None
    notes: str | None = None


class Entity(BaseModel):
    text: str
    label: str


class GenericSchema(BaseModel):
    title: str | None = None
    summary: str
    key_facts: list[str] = Field(default_factory=list)
    entities: list[Entity] = Field(default_factory=list)
    dates: list[str] = Field(default_factory=list)


SCHEMA_MAP = {
    SchemaName.receipt: ReceiptSchema,
    SchemaName.medical: MedicalSchema,
    SchemaName.generic: GenericSchema,
}

SCHEMA_DESCRIPTIONS = {
    SchemaName.receipt: "retail receipt, invoice, or bill",
    SchemaName.medical: "medical report, prescription, or clinical note",
    SchemaName.generic: "any other document — extracts summary, entities, key facts",
}
