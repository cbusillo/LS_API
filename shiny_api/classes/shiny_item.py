"""Shiny Item class."""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint, Column, Integer


class Item(SQLModel, table=True):
    """Model for Shiny Item table."""
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    ls_item_id: int = Field(sa_column=Column("ls_item_id", Integer, unique=True), default=0)
    average_cost: Decimal = Field(default=0)
    archived: bool = Field(default=False)
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_from_ls_at: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(default="")
    taxed: bool = Field(default=True)
    item_type: str = Field(default="")
    serialized: bool = Field(default=False)
    upc: int = Field(default=0)
    custom_sku: str = Field(default="")
    manufacturer_sku: str = Field(default="")
    item_matrix_id: int = Field(default=0)
    manufacturer_id: int = Field(default=0)
    vendor_id: int = Field(default=0)
    # item_attributes_id: Optional[int] = Field(default=None, foreign_key="item_attributes.id")))
    item_attributes: str = Field(default="")
    prices: str = Field(default="")
    sizes: str = Field(default="")


class ItemAttributes(SQLModel, table=True):
    """Model for Shiny Item Attributes table."""
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    item_id: int = Field()
    attribute_id: int = Field()
    value: str = Field()
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    UniqueConstraint("item_id", "attribute_id", name="uq_item_id_attribute_id")


if __name__ == "__main__":
    pass
