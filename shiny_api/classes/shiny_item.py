"""Shiny Item class."""
from datetime import datetime
from typing import Optional
from pydantic import ConstrainedDecimal
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint, Column, Integer


class ShinyMoney(ConstrainedDecimal):
    """Shiny Money class."""
    max_digits = 11
    decimal_places = 2


class Item(SQLModel, table=True):
    """Model for Shiny Item table."""
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    ls_item_id: int = Field(sa_column=Column("ls_item_id", Integer, unique=True))
    average_cost: ShinyMoney = Field(nullable=True)
    archived: bool = Field()
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_from_ls_at: datetime = Field()
    description: str = Field()
    taxed: bool = Field()
    item_type: str = Field()
    serialized: bool = Field()
    upc: str = Field(nullable=True)
    custom_sku: str = Field(nullable=True)
    manufacturer_sku: str = Field()
    item_matrix_id: int = Field()
    manufacturer_id: int = Field()
    vendor_id: int = Field()
    # item_attributes_id: Optional[int] = Field(default=None, foreign_key="item_attributes.id")))
    item_attributes: str = Field()
    prices: str = Field()
    sizes: str = Field()


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
    item = Item()
    print()
