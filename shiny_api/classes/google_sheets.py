"""connect to Google's MySQL DB"""
import datetime
import os
from typing import List
import pygsheets
import shiny_api.modules.load_config as config
import shiny_api.classes.sickw_results as sickw_results


print(f"Importing {os.path.basename(__file__)}...")

SCOPES = ("https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive")
HEADERS = ["ID", "Status", "Serial Number", "Description", "Name", "A Number", "Model ID", "Capacity", "Color", "Type", "Year"]


class GoogleSheet:
    """Object to interact with a Google Sheet"""

    google_client: pygsheets.client.Client
    sheet: pygsheets.Spreadsheet
    worksheets: List[pygsheets.Worksheet]
    current_worksheet: pygsheets.Worksheet

    lines = [sickw_results.SickwResults]

    def __init__(self, sheet_name: str) -> str:
        self.google_client = pygsheets.authorize(outh_file=f"{config.CONFIG_SECRET_DIR}/.secret_client.json", scopes=SCOPES)

        sheets = self.google_client.spreadsheet_titles()
        if sheet_name not in sheets:
            self.google_client.create(sheet_name)
        self.sheet = self.google_client.open(sheet_name)
        self.worksheets = self.sheet.worksheets()
        self.current_worksheet = self.sheet.add_worksheet(title=datetime.datetime.now().strftime("%m%d%y-%H%M%S"), rows=2, cols=11)
        self.current_worksheet.frozen_rows = 1
        self.current_worksheet.update_row(1, values=HEADERS)

        # TODO: Remove after testing
        self.del_other_worksheets()

    def add_line(self, line: sickw_results.SickwResults):
        """Take Sickw line and add to local array and Google Sheets"""
        self.lines.append(line)
        self.current_worksheet.add_rows(1)
        self.current_worksheet.update_row(
            self.current_worksheet.rows,
            values=[
                str(line.result_id),
                line.status,
                line.serial_number,
                line.description,
                line.name,
                line.a_number,
                line.model_id,
                line.capacity,
                line.color,
                line.type,
                str(line.year),
            ],
        )

        self.current_worksheet.adjust_column_width(1, 11)

    def del_other_worksheets(self):
        """Testing function to remove all but current worksheet"""
        for delete in self.worksheets[0:-1]:
            self.sheet.del_worksheet(delete)
