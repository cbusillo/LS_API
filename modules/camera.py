"""Take picture from webcam"""
import os
import cv2
from kivy.uix.button import Button
import pytesseract
from modules import load_config as config
from classes.google_mysql import Database
from classes.api_serial import Serial

# TODO get info from serial number api
print(f"Importing {os.path.basename(__file__)}...")


def take_serial_image(caller: Button):
    """Take image from document camera and return string of serial number."""

    capture = cv2.VideoCapture(config.CAM_PORT)
    capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)

    while True:
        result = False
        while not result:

            result, serial_image = capture.read()
            serial_image = cv2.cvtColor(serial_image, cv2.COLOR_BGR2GRAY)
            (_, black_and_white_image) = cv2.threshold(serial_image, 127, 255, cv2.THRESH_BINARY)

            if result:
                serial_image_data = pytesseract.image_to_data(
                    black_and_white_image, config="--psm 12", output_type=pytesseract.Output.DICT
                )

        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf > 5:
                if word[0:1] == "D":
                    caller.text = f"{caller.text.split(chr(10))[0]}\n{word}"
                    print(word)

        cv2.imshow("Serial Image", black_and_white_image)
        if cv2.waitKey(1000) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            caller.disabled = False
            caller.text = caller.text.split("\n")[0]
            break
        cv2.destroyAllWindows()


def testing():
    """Launch testing debug"""
    api_db = Database()
    api_db.add_serial("12345")
    serials = api_db.get_all(Serial)
    for serial in serials:
        print(serial.serial_number)
    print(api_db.exists(Serial, "12345"))
