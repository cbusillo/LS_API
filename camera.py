"""Take picture from webcam"""
import os
import cv2
import pytesseract
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.button import Label
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
import numpy as np
from skimage.transform import rotate
from skimage.color import rgb2gray
from deskew import determine_skew
from modules import load_config as config
from classes.google_mysql import Database
from classes.api_serial import Serial

# from classes import google_sheets


print(f"Importing {os.path.basename(__file__)}...")


def deskew(image):
    """take image and return straight image"""
    angle = determine_skew(image)
    if angle is None:
        angle = 0
    rotated = rotate(image, angle, resize=True) * 255
    return rotated.astype(np.uint8)


def thresh_image(image):
    """take grayscale image and return Threshholded image"""
    image = cv2.rotate(image, cv2.ROTATE_180)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    image = deskew(image)
    _, image = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
    return image


class PhotoWindow(GridLayout):
    """Independent app to scan serials"""

    def __init__(self, **kwargs):
        """Create GUI"""
        super(PhotoWindow, self).__init__(**kwargs)
        self.cols = 1
        self.padding = 100
        self.scanned_image = Image()
        self.add_widget(self.scanned_image)
        self.status = Label()
        self.add_widget(self.status)

        self.capture = cv2.VideoCapture(config.CAM_PORT)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
        self.texture1 = None

        Clock.schedule_interval(self.update, 0.1)

    def update(self, _):
        """Handle clock updates"""
        result, serial_image = self.capture.read()

        if result:
            threshed = thresh_image(serial_image)
            serial_image_data = pytesseract.image_to_data(
                threshed,
                output_type=pytesseract.Output.DICT,
                config="--psm 12",
            )
        lines = ""
        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf > 50 and word[0:1].lower() == "d" and len(word) >= 8:
                if word.lower().strip() == "dmpykq6vjf8j":
                    output = f"Conf: {conf} {word}"
                    print(output)
                    lines = f"{lines} {output}\n"
                else:
                    print(f"{word} fail at {conf}")

        print()
        self.status.text = lines

        cv2.imshow("test", threshed)
        buf1 = cv2.flip(serial_image, 0)
        buf = buf1.tobytes()
        if self.texture1 is None:
            self.texture1 = Texture.create()
        self.texture1.blit_buffer(buf, colorfmt="rgb", bufferfmt="ubyte")
        self.scanned_image.texture = self.texture1


class SerialCamera(App):
    """Get image from camera and start serial check"""

    def build(self):
        Window.left = 220  # 0
        Window.top = 100
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
