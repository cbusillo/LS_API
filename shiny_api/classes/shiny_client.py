"""Create interface to Shiny DB"""
from sqlmodel import SQLModel, create_engine


SQLITE_FILENAME = 'shiny.sqlite3'
sqlite_url = f"sqlite:///{SQLITE_FILENAME}"

engine = create_engine(sqlite_url)


def drop_db_and_tables():
    """Drop all tables in the database"""
    SQLModel.metadata.drop_all(engine)


def create_db_and_tables():
    """Create all tables in the database from SQLModel"""
    SQLModel.metadata.create_all(engine)
