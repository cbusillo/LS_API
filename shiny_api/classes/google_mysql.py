"""connect to Google's MySQL DB"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from shiny_api.modules.load_config import DB_ACCESS as config
from shiny_api.classes.api_serial import Serial

print(f"Importing {os.path.basename(__file__)}...")


class Database:
    """Create Database class for Google mysql"""

    engine = None
    session = None

    def __init__(self) -> None:
        """Init db connection"""
        ssl_certs = {"ssl_ca": "config/server-ca.pem", "ssl_cert": "config/client-cert.pem", "ssl_key": "config/client-key.pem"}
        connect_string = f'mysql+pymysql://{config["user"]}:{config["password"]}@{config["host"]}/{config["database"]}'
        if Database.engine is None:
            Database.engine = create_engine(connect_string, echo=False, connect_args=ssl_certs)
            Database.session = Session(Database.engine)

            print("Connection established")

    def get_all(self, obj: object):
        """Get all serial numbers from table"""
        return self.session.query(obj).all()

    def exists(self, obj: object, search_string) -> bool:
        """Return True or False if serial exists"""
        response = self.session.query(obj).filter_by(serial_number=search_string).all()
        print(response)
        return bool(response)

    def add_serial(self, serial):
        """Add serial number if not exist"""
        if not self.exists(Serial, serial):
            print(f"Adding serial {serial} to db.")
            self.session.add(Serial(serial_number=serial))
            self.session.commit()
        else:
            print(f"Serial number {serial} already in db.")
