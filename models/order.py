from __future__ import annotations

from typing import Optional, List
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    product_id: UUID = Field(
        ...,
        description="ID of the product in this line item.",
        json_schema_extra={"example": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="Quantity ordered (must be > 0).",
        json_schema_extra={"example": 2},
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                "quantity": 2,
            }
        }
    }


class OrderBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique order ID.",
        json_schema_extra={"example": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"},
    )
    customer_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the customer placing the order.",
        json_schema_extra={"example": "Alice"},
    )
    items: List[LineItem] = Field(
        default_factory=list,
        description="List of product line items.",
    )
    note: Optional[str] = Field(
        None,
        max_length=280,
        description="Optional note attached to the order.",
        json_schema_extra={"example": "Leave at front desk."},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "customer_name": "Alice",
                    "items": [
                        {
                            "product_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                            "quantity": 2,
                        }
                    ],
                    "note": "Leave at front desk.",
                }
            ]
        }
    }


class OrderCreate(OrderBase):
    """Creation payload; ID is generated server-side but allowed in payload (like Address)."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "11111111-2222-4333-8444-555555555555",
                    "customer_name": "Bob",
                    "items": [
                        {"product_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "quantity": 1}
                    ],
                    "note": None,
                }
            ]
        }
    }


class OrderUpdate(BaseModel):
    """Partial update (PATCH)."""
    customer_name: Optional[str] = Field(
        None, min_length=1, max_length=100, json_schema_extra={"example": "Alice Johnson"}
    )
    items: Optional[List[LineItem]] = Field(
        None,
        description="If provided, replaces the entire items list.",
        json_schema_extra={
            "example": [
                {"product_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "quantity": 3}
            ]
        },
    )
    note: Optional[str] = Field(None, max_length=280, json_schema_extra={"example": "Ring the bell twice."})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"customer_name": "Alice Johnson"},
                {"items": [{"product_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa", "quantity": 3}]},
                {"note": "Ring the bell twice."},
            ]
        }
    }


class OrderRead(OrderBase):
    """Server representation returned to clients (includes timestamps and computed total)."""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-09-13T15:05:00Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-09-13T15:35:00Z"},
    )
    total_amount: float = Field(
        default=0.0,
        ge=0.0,
        description="Computed total for the order in USD.",
        json_schema_extra={"example": 19.98},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb",
                    "customer_name": "Alice",
                    "items": [
                        {
                            "product_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                            "quantity": 2,
                        }
                    ],
                    "note": "Leave at front desk.",
                    "created_at": "2025-09-13T15:05:00Z",
                    "updated_at": "2025-09-13T15:35:00Z",
                    "total_amount": 19.98,
                }
            ]
        }
    }
