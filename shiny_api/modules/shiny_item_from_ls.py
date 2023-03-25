from datetime import datetime
import logging
import pytz
from rich import print as pprint
from sqlmodel import Session, select
from shiny_api.classes.ls_item import Item as LsItem
from shiny_api.classes.shiny_item import Item as ShinyItem
from shiny_api.classes.shiny_client import create_db_and_tables, drop_db_and_tables, engine


def import_item(ls_item: LsItem):
    with Session(engine) as session:
        shiny_item = ShinyItem(
            ls_item_id=ls_item.item_id,
            average_cost=ls_item.avg_cost,
            archived=ls_item.archived,
            updated_from_ls_at=datetime.now()
            
        )
        #session.add(shiny_item)
        
        results = session.exec(select(ShinyItem).where(ShinyItem.ls_item_id == ls_item.item_id))
        shiny_result_item = results.one_or_none()
        if shiny_result_item:
            session.add(shiny_result_item)
            
        else:
            session.add(shiny_item)

        session.commit()

def date_last_updated_from_ls(time_zone: str = "EST"):
    with Session(engine) as session:
        tz_time_zone = pytz.timezone(time_zone)
        last_item_query = select(ShinyItem.updated_from_ls_at).order_by(ShinyItem.updated_from_ls_at.desc()).limit(1)
        item_updated_date = session.exec(last_item_query).one_or_none()
        return pytz.eastern.localize(item_updated_date)
        #return  tz_time_zone.normalize(item_updated_date)


def list_items():
    with Session(engine) as session:
        items = session.query(ShinyItem).all()
        pprint(items)
        print (len(items))


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    #drop_db_and_tables()
    create_db_and_tables()
    items = LsItem.get_all_items(date_filter=date_last_updated_from_ls())
    for item in items:
        import_item(item)
        pprint(f"{item} {item.time_stamp}")
    #list_items()
    
    print()
    pprint(date_last_updated_from_ls())