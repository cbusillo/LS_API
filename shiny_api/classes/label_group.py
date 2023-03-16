import os
from pydantic import BaseModel
import shiny_api.modules.load_config as config
from shiny_api.modules.load_config import DEFAULT_LABELS

print(f"Importing {os.path.basename(__file__)}...")


class LabelGroup(BaseModel):
    """Class to hold label group data"""

    name: str
    labels: list[str]
    printer_ip: str

    @staticmethod
    def load_from_defaults():
        return {name: LabelGroup(name=name, labels=label_group["labels"], printer_ip=label_group["printer_ip"])
                for name, label_group in config.DEFAULT_LABELS.items()}


if __name__ == "__main__":
    for label_group in DEFAULT_LABELS:
        print(label_group)
    # label_group = LabelGroup(name="Main Labels", printer_ip=config.PRINTER_IP)
