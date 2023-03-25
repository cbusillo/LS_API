from typing import Optional
from pydantic import condecimal
from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint, Column, Integer
from datetime import datetime


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True, nullable=False)
    ls_item_id: int = Field(sa_column=Column("ls_item_id",Integer, unique=True))
    average_cost: condecimal(max_digits=7, decimal_places=2) = Field(nullable=True)
    archived: bool = Field()
    created_at: datetime = Field(default=datetime.now())
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_from_ls_at: datetime = Field()


if __name__ == "__main__":
    item = Item()
    print()
