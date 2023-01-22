"""connect to Google's MySQL DB"""
import os
from sqlalchemy import create_engine, Column
from sqlalchemy.orm import Session
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from modules.load_config import DB_ACCESS as config


print(f"Importing {os.path.basename(__file__)}...")


class Serial(declarative_base()):
    """Class to describe db table serial_scanner"""

    __tablename__ = "serial_scanner"
    id = Column(Integer, primary_key=True)
    serial_number = Column(String(20), unique=True, nullable=False)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    file_location = Column((String(255)))

    def __repr__(self):
        """Return basic string"""
        return f"<Serial {self.serial_number} {self.create_time} {self.file_location}"


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
        return self.session.query(obj).all()

    def exists(self, obj: object, search_string) -> bool:
        """Return True or False if serial exists"""
        response = self.session.query(obj).filter_by(serial_number=search_string).all()
        return bool(response)

    def add_serial(self, serial):
        if not self.exists(Serial, serial):
            print(f"Adding serial {serial} to db.")
            self.session.add(Serial(serial_number=serial))
            self.session.commit()
        else:
            print(f"Serial number {serial} already in db.")


db = Database()
db.add_serial("12345")
serials = db.get_all(Serial)
for serial in serials:
    print(serial.serial_number)
print(db.exists(Serial, "12345"))
