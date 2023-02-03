"""Take picture from webcam"""
import os
import time
import re
import cv2
import pytesseract
from functools import partial
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.button import Label, Button
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
import numpy as np
from skimage.transform import rotate
from deskew import determine_skew
from modules import load_config as config
from classes.google_mysql import Database
from classes.api_serial import Serial
import modules.connect_sickw as connect_sickw

# from classes import google_sheets


print(f"Importing {os.path.basename(__file__)}...")

APPLE_SERIAL_INFO = 26
BLACKLIST = ["BCGA"]


def deskew(image: Image):
    """take image and return straight image"""

    angle = determine_skew(image)
    if angle is None:
        angle = 0
    rotated = rotate(image, angle, resize=False) * 255
    return rotated.astype(np.uint8)


class PhotoWindow(GridLayout):
    """Independent app to scan serials"""

    def __init__(self, **kwargs):
        """Create GUI"""
        super(PhotoWindow, self).__init__(**kwargs)
        # self.width = config.CAM_WIDTH
        # self.height = config.CAM_HEIGHT
        # self.size = [1920, 1080]

        self.cols = 1
        self.padding = 100

        self.rotate_button = Button(text="Rotate", halign="center", size_hint=(0.1, 0.1))
        self.rotate_button.bind(on_press=self.rotate_button_fn)
        self.add_widget(self.rotate_button)
        self.threshold_up_button = Button(text="Threshold up", halign="center", size_hint=(0.1, 0.1))
        self.threshold_up_button.bind(on_press=partial(self.threshold_button_fn, 5))
        self.add_widget(self.threshold_up_button)
        self.threshold_down_button = Button(text="Threshold down", halign="center", size_hint=(0.1, 0.1))
        self.threshold_down_button.bind(on_press=partial(self.threshold_button_fn, -5))
        self.add_widget(self.threshold_down_button)

        self.scanned_image = Image()
        self.scanned_image.width = cv2.CAP_PROP_FRAME_WIDTH
        self.scanned_image.height = cv2.CAP_PROP_FRAME_HEIGHT
        self.add_widget(self.scanned_image)

        self.status = Label()
        self.add_widget(self.status)

        self.capture = cv2.VideoCapture(config.CAM_PORT)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
        Clock.schedule_interval(self.update, 1 / 30)
        self.serial_history = []
        self.fps_previous = 0
        self.fps_current = 0
        self.rotation = 1
        self.theshold_value = 150

    def thresh_image(self, image):
        """take grayscale image and return Threshholded image"""
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = deskew(image)
        _, image = cv2.threshold(image, self.theshold_value, 255, cv2.THRESH_BINARY)
        # image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 15)

        return image

    def rotate_button_fn(self, _):
        if self.rotation < 2:
            self.rotation += 1
        else:
            self.rotation = -1

    def threshold_button_fn(self, change, _):
        if self.theshold_value + change < 255 and self.theshold_value + change > -1:
            self.theshold_value += change

    def update(self, _):
        """Handle clock updates"""
        result, serial_image = self.capture.read()
        if self.rotation > -1:
            serial_image = cv2.rotate(serial_image, self.rotation)
        if result:
            threshed = self.thresh_image(serial_image)
            serial_image_data = pytesseract.image_to_data(
                threshed,
                output_type=pytesseract.Output.DICT,
                config="--psm 11",  # -c tessedit_char_whitelist=' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'",
            )
        display_lines = ""
        miss = True
        serial_previous = False
        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf > 60 and len(word) >= 8 and re.sub(r"[^A-Z0-9]", "", word) == word:
                blacklisted = False
                for black in BLACKLIST:
                    if black in word:
                        blacklisted = True
                # if word.upper().strip() == "GG7X2LZ6JF88":
                if word not in self.serial_history and not blacklisted:
                    result = connect_sickw.get_data(word, APPLE_SERIAL_INFO)
                    self.serial_history.append(
                        {
                            word,
                            result["status"],
                        }
                    )

                output = f"Conf: {conf} {word} Total: {len(self.serial_history)}"
                print(output)
                display_lines += f" {output}\n"
                miss = False
                # else:
                #    print(f"{word} fail at {conf}")
            elif "serial" in word.lower():
                serial_previous = True
        if miss is True:
            print(".", end="")
        self.status.text = display_lines

        self.fps_current = time.time()
        fps = 1 / (self.fps_current - self.fps_previous)
        self.fps_previous = self.fps_current
        cv2.putText(threshed, str(round(fps, 2)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

        # cv2.imshow("test", threshed)
        buf1 = cv2.flip(threshed, 0)
        buf = buf1.tobytes()
        # if self.scanned_image.texture is None:
        self.scanned_image.texture = Texture.create(size=(config.CAM_WIDTH, config.CAM_HEIGHT), colorfmt="luminance")
        self.scanned_image.texture.blit_buffer(buf, colorfmt="luminance", bufferfmt="ubyte")


class SerialCamera(App):
    """Get image from camera and start serial check"""

    def build(self):
        Window.left = 0  # 0
        Window.top = 0
        Window.size = (config.CAM_WIDTH / 2, config.CAM_HEIGHT)
        return PhotoWindow()


if __name__ == "__main__":
    SerialCamera().run()


def testing():
    """Launch testing debug"""
    api_db = Database()
    api_db.add_serial("12345")
    serials = api_db.get_all(Serial)
    for serial in serials:
        print(serial.serial_number)
    print(api_db.exists(Serial, "12345"))
