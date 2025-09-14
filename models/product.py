from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique product ID.",
        json_schema_extra={"example": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"},
    )
    name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Product name.",
        json_schema_extra={"example": "Widget"},
    )
    description: Optional[str] = Field(
        None,
        max_length=500,
        description="Short description.",
        json_schema_extra={"example": "A compact widget for demos."},
    )
    price: float = Field(
        ...,
        ge=0.0,
        description="Unit price in USD (non-negative).",
        json_schema_extra={"example": 9.99},
    )
    in_stock: int = Field(
        ...,
        ge=0,
        description="Units available in inventory (non-negative).",
        json_schema_extra={"example": 100},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "name": "Widget",
                    "description": "A compact widget for demos.",
                    "price": 9.99,
                    "in_stock": 100,
                }
            ]
        }
    }


class ProductCreate(ProductBase):
    """Creation payload; ID is generated server-side but allowed in payload (like Address)."""
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "11111111-1111-4111-8111-111111111111",
                    "name": "Pro Widget",
                    "description": "Upgraded widget with more features.",
                    "price": 19.99,
                    "in_stock": 25,
                }
            ]
        }
    }


class ProductUpdate(BaseModel):
    """Partial update payload (PATCH); only supply fields you want to change."""
    name: Optional[str] = Field(None, min_length=1, max_length=100, json_schema_extra={"example": "Widget X"})
    description: Optional[str] = Field(None, max_length=500, json_schema_extra={"example": "New description"})
    price: Optional[float] = Field(None, ge=0.0, json_schema_extra={"example": 14.49})
    in_stock: Optional[int] = Field(None, ge=0, json_schema_extra={"example": 42})

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"price": 14.49},
                {"name": "Widget X", "description": "New description"},
                {"in_stock": 42},
            ]
        }
    }


class ProductRead(ProductBase):
    """Server representation returned to clients (includes timestamps)."""
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-09-13T15:04:05Z"},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-09-13T15:30:00Z"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
                    "name": "Widget",
                    "description": "A compact widget for demos.",
                    "price": 9.99,
                    "in_stock": 100,
                    "created_at": "2025-09-13T15:04:05Z",
                    "updated_at": "2025-09-13T15:30:00Z",
                }
            ]
        }
    }
