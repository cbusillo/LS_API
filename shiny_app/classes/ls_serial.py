from typing import Any, Generator, Optional, Self
from dataclasses import dataclass, field
from shiny_app.classes.ls_client import BaseLSEntity


@dataclass
class Item(BaseLSEntity):
    """Item class from LS"""

    default_params = {"load_relations": '["ItemAttributes","ItemPrices"]'}

    @dataclass
    class ItemMatrix(BaseLSEntity):
        """Get full list of size attributes from LS table.
        Use these to import into individual items without a separate API call."""

        size_attributes = []
