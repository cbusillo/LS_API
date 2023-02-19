"""connect to Google's MySQL DB"""
import os
from sqlalchemy import Column
from sqlalchemy.types import Integer, String, DateTime
from sqlalchemy.sql import functions
from sqlalchemy.ext.declarative import declarative_base

print(f"Importing {os.path.basename(__file__)}...")


class Serial(declarative_base()):
    """Class to describe db table serial_scanner"""

    __tablename__ = "serial_scanner"
    id = Column(Integer, primary_key=True)
    serial_number = Column(String(20), unique=True, nullable=False)
    create_time = Column(
        DateTime(timezone=True), server_default=functions.now()
    )  # changed from func.now() at pylints complaint.  Not sure if this works
    file_location = Column((String(255)))

    def __repr__(self):
        """Return basic string"""
        return f"<Serial {self.serial_number} {self.create_time} {self.file_location}"
