"""connect to Google's MySQL DB"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from modules.load_config import DB_ACCESS as config
from classes.apl_serial import Serial

print(f"Importing {os.path.basename(__file__)}...")


class Database:
    """Create Database class for Google mysql"""

    connect_string = f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}'
    engine = None
    session = None

    def __init__(self) -> None:
        """Init db connection"""
        if Database.engine is None:
            try:
                Database.engine = create_engine(Database.connect_string, echo=False)
                Database.session = Session(Database.engine)

            except Exception as error:
                print(f"Error: Connection not established {format(error)}")
            else:
                print("Connection established")

    def get_all(self, obj: object):
        """Get all serial numbers from table"""
        return self.session.query(obj).all()

    def exists(self, obj: object, search_string) -> bool:
        """Return True or False if serial exists"""
        response = self.session.query(obj).filter_by(serial_number=search_string).all()
        return bool(response)

    def add_serial(self, serial):
        """Add serial number if not exist"""
        if not self.exists(Serial, serial):
            print(f"Adding serial {serial} to db.")
            self.session.add(Serial(serial_number=serial))
            self.session.commit()
        else:
            print(f"Serial number {serial} already in db.")
