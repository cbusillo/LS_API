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
from modules import load_config as config
from classes.google_mysql import Database
from classes.api_serial import Serial


print(f"Importing {os.path.basename(__file__)}...")


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
        # cv2.namedWindow("Serial Capture")
        Clock.schedule_interval(self.update, 0.1)

    def update(self, _):
        """Handle clock updates"""
        result, serial_image = self.capture.read()

        # bgray = serial_image[..., 0]
        # blured1 = cv2.medianBlur(bgray, 3)
        # blured2 = cv2.medianBlur(bgray, 51)
        # divided = np.ma.divide(blured1, blured2).data
        # normed = np.uint8(255 * divided / divided.max())
        # _, threshed = cv2.threshold(normed, 100, 255, cv2.THRESH_OTSU)

        serial_image = cv2.cvtColor(serial_image, cv2.COLOR_BGR2GRAY)
        _, threshed = cv2.threshold(serial_image, 127, 255, cv2.THRESH_BINARY)

        if result:
            serial_image_data = pytesseract.image_to_data(threshed, output_type=pytesseract.Output.DICT)
        lines = ""
        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf > 80:
                if word[0:1].isalpha():
                    output = f"Conf: {conf} {word}"
                    print(output)
                    lines = lines + output + "\n"

        self.status.text = lines
        buf1 = cv2.flip(threshed, 0)
        buf = buf1.tobytes()
        texture1 = Texture.create(size=(threshed.shape[1], threshed.shape[0]), colorfmt="luminance")
        texture1.blit_buffer(buf, colorfmt="luminance", bufferfmt="ubyte")
        self.scanned_image.texture = texture1


class SerialCamera(App):
    """Get image from camera and start serial check"""

    def build(self):
        Window.left = 220  # 0
        Window.top = 100
        Window.size = (config.CAM_WIDTH / 2, config.CAM_HEIGHT)
        return PhotoWindow()


SerialCamera().run()


def testing():
    """Launch testing debug"""
    api_db = Database()
    api_db.add_serial("12345")
    serials = api_db.get_all(Serial)
    for serial in serials:
        print(serial.serial_number)
    print(api_db.exists(Serial, "12345"))
