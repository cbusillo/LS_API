"""connect to Google's MySQL DB"""
import os
import json
import pygsheets
import shiny_api.modules.load_config as config


print(f"Importing {os.path.basename(__file__)}...")


# dataframe = pd.DataFrame()
# dataframe["serial"] = ["1234"]
google_sheets_connection = pygsheets.authorize(service_account_json=json.dumps(config.SHEETS_ACCESS))
serial_sheet = google_sheets_connection.open(config.GOOGLE_SHEETS_SERIAL_NAME)
print(serial_sheet)
# google_sheets_connection.create(config.GOOGLE_SHEETS_SERIAL_NAME)
# google_sheets_serial = google_sheets_connection.open(config.GOOGLE_SHEETS_SERIAL_NAME)
# google_sheets_serial[0].set_dataframe(dataframe, (1, 1))
# # google_sheets_serial = google_sheets_connection.open(config.GOOGLE_SHEETS_SERIAL_NAME)
serial_sheet.share("Laptoptester123@gmail.com", role="reader", type="anyone")

# sheets = google_sheets_connection.spreadsheets()
