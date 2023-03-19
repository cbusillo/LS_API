"""webview to print labels"""
import json
from flask import render_template
from shiny_api.modules import load_config as config


def table_editor_view(active_table: str = ""):
    """View for Table Editor"""
    buttons = {
        "age":
            "config/age.json",
        "config":
            "config/config.json",
        "devices":
            "config/devices.json",
        "secret":
            "~/.secret.json"
    }
    if active_table == "":
        return render_template(
            'table_editor.jinja-html',
            title="Table Editor",
            buttons=buttons
        )
    table_json = {}
    with open(f"{config.SCRIPT_DIR}{buttons[active_table]}", encoding="utf8") as file:
        table_json = json.load(file)
    temp_json = {}
    if active_table == "devices":
        for device_name, values in table_json.items():
            value_list = []
            value_name = ""
            for count, value in enumerate(values):
                match count:
                    case 0:
                        value_name = "Current"
                    case 1:
                        value_name = "Released"
                    case 2:
                        value_name = "Base Price"
                    case 3:
                        value_name = "Cellular Base Price"
                    case 4:
                        value_name = "URL"
                value_list.append({value_name: value})
            temp_json[device_name] = value_list
        table_json = temp_json

    return render_template(
        f'table_{active_table}.jinja-html',
        title=f"{active_table.title()} Editor",
        table=table_json,
        buttons=buttons)
