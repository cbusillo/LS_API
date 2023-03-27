"""Import items from LightSpeed to Shiny."""
from datetime import datetime
import logging
import pytz
from rich import print as pprint
from sqlmodel import Session, select
from shiny_api.classes.ls_item import Item as LsItem
from shiny_api.classes.shiny_item import Item as ShinyItem
from shiny_api.classes.shiny_client import create_db_and_tables, drop_db_and_tables, engine


def import_item(ls_item: LsItem):
    """Relate LS item to Shiny item"""
    with Session(engine) as session:
        results = session.exec(select(ShinyItem).where(ShinyItem.ls_item_id == ls_item.item_id))
        shiny_item = results.one_or_none()
        if shiny_item is None:
            shiny_item = ShinyItem()

        shiny_item.ls_item_id = ls_item.item_id
        shiny_item.average_cost = ls_item.avg_cost or ls_item.default_cost
        shiny_item.archived = ls_item.archived
        shiny_item.updated_from_ls_at = datetime.now()
        shiny_item.description = ls_item.description
        shiny_item.taxed = ls_item.tax
        shiny_item.item_type = ls_item.item_type
        shiny_item.serialized = ls_item.serialized
        shiny_item.upc = ls_item.upc
        shiny_item.custom_sku = ls_item.custom_sku
        shiny_item.manufacturer_sku = ls_item.manufacturer_sku
        shiny_item.item_matrix_id = ls_item.item_matrix_id
        shiny_item.manufacturer_id = ls_item.manufacturer_id
        shiny_item.vendor_id = ls_item.default_vendor_id
        shiny_item.item_attributes = str(ls_item.item_attributes)
        shiny_item.prices = str(ls_item.prices)
        shiny_item.sizes = str(ls_item.sizes)

        session.add(shiny_item)
        session.commit()
        pprint(f"Shiny {shiny_item} {shiny_item.updated_from_ls_at.astimezone(pytz.timezone('America/New_York'))}")


def date_last_updated_from_ls(time_zone: str = "America/New_York"):
    """Convert LS date string to datetime"""
    local_tz = pytz.timezone(time_zone)
    with Session(engine) as session:
        last_item_query = select(ShinyItem.updated_from_ls_at).order_by(ShinyItem.updated_from_ls_at).limit(1)
        item_updated_date = session.exec(last_item_query).one_or_none()
        if item_updated_date is None:
            return datetime(2000, 1, 1, 0, 0, 0, 0, tzinfo=local_tz)
        item_updated_date = local_tz.localize(item_updated_date, is_dst=None).astimezone(pytz.utc)
        return item_updated_date


def list_items(item_id: int = 0):
    """List items from Shiny db"""
    with Session(engine) as session:
        if item_id:
            items = session.query(ShinyItem).where(ShinyItem.ls_item_id == item_id).one_or_none()
        else:
            items = session.query(ShinyItem).all()
        for item in items:
            pprint(f"Shiny {item} {item.time_stamp.astimezone(pytz.timezone('America/New_York'))}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    DELETE_DB = False
    if DELETE_DB:
        drop_db_and_tables()
    create_db_and_tables()
    test_items = LsItem.get_all_items(date_filter=date_last_updated_from_ls())
    for test_item in test_items:
        import_item(test_item)
        pprint(f"LightSpeed {test_item} {test_item.time_stamp.astimezone(pytz.timezone('America/New_York'))}")

    print()
    # pprint(f"Shiny: {date_last_updated_from_ls()}")
