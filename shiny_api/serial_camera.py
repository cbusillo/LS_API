"""Take picture from webcam"""
import os
import time
import math
import re
from functools import partial
import cv2
import pytesseract
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics.texture import Texture
from kivy.uix.button import Label, Button
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
import numpy as np
from shiny_api.modules import load_config as config
from shiny_api.classes import sickw_results

print(f"Importing {os.path.basename(__file__)}...")

# Ignore serial number if it contains an item from this list
BLACKLIST = ["BCGA"]


def rotate_image(image, angle):
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def compute_skew(src_img):
    if len(src_img.shape) == 3:
        height, width, _ = src_img.shape
    elif len(src_img.shape) == 2:
        height, width = src_img.shape
    else:
        print("upsupported image type")

    img = cv2.medianBlur(src_img, 3)
    edges = cv2.Canny(img, threshold1=30, threshold2=100, apertureSize=3, L2gradient=True)
    lines = cv2.HoughLinesP(edges, 1, math.pi / 180, 30, minLineLength=width / 4.0, maxLineGap=height / 4.0)
    angle = 0.0

    cnt = 0
    if lines is not None:
        for x_1, y_1, x_2, y_2 in lines[0]:
            ang = np.arctan2(y_2 - y_1, x_2 - x_1)
            if math.fabs(ang) <= 30:  # excluding extreme rotations
                angle += ang
                cnt += 1

        if cnt == 0:
            return 0.0
        return (angle / cnt) * 180 / math.pi


def deskew(src_img):
    return rotate_image(src_img, compute_skew(src_img))


class SerialCamera(GridLayout):
    """Independent app to scan serials"""

    def __init__(self, **kwargs):
        """Create GUI"""
        super(SerialCamera, self).__init__(**kwargs)

        self.cols = 1
        self.padding = 50

        self.rotate_button = Button(text="Rotate", halign="center", size_hint=(0.1, 0.1))
        self.rotate_button.bind(on_press=self.rotate_button_fn)
        self.add_widget(self.rotate_button)

        self.threshold_slider = Slider(min=0, max=255, value=180, size_hint=(1, 0.15))
        self.threshold_slider.bind(value=self.threshold_change)
        self.add_widget(self.threshold_slider)

        self.threshold_grid = GridLayout()
        self.threshold_grid.cols = 3
        self.threshold_grid.size_hint_y = 0.1

        self.threshold_down_button = Button(text="Threshold down", halign="center")
        self.threshold_down_button.bind(on_press=partial(self.threshold_change, value=-5))
        self.threshold_grid.add_widget(self.threshold_down_button)

        self.threshold_label = Label(text=str(self.threshold_slider.value))
        self.threshold_grid.add_widget(self.threshold_label)

        self.threshold_up_button = Button(text="Threshold up", halign="center")
        self.threshold_up_button.bind(on_press=partial(self.threshold_change, value=5))
        self.threshold_grid.add_widget(self.threshold_up_button)

        self.add_widget(self.threshold_grid)

        self.image_grid = GridLayout()
        self.image_grid.cols = 2

        self.scanned_image = Image()
        self.scanned_image.width = cv2.CAP_PROP_FRAME_WIDTH
        self.scanned_image.height = cv2.CAP_PROP_FRAME_HEIGHT
        self.image_grid.add_widget(self.scanned_image)

        self.threshed_image = Image()
        self.threshed_image.width = cv2.CAP_PROP_FRAME_WIDTH
        self.threshed_image.height = cv2.CAP_PROP_FRAME_HEIGHT
        self.image_grid.add_widget(self.threshed_image)

        self.add_widget(self.image_grid)

        self.status = Label(size_hint=(0.8, 0.2))
        self.add_widget(self.status)

        self.capture = cv2.VideoCapture(config.CAM_PORT)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, config.CAM_HEIGHT)
        Clock.schedule_interval(self.update, 1 / 30)
        self.sickw_history = []
        self.fps_previous = 0
        self.fps_current = 0
        self.rotation = 1
        # self.theshold_value = 180

    def thresh_image(self, image):
        """take grayscale image and return Threshholded image.  Use value from slider"""
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = deskew(image)
        # _, image = cv2.threshold(image, self.threshold_slider.value, 255, cv2.THRESH_BINARY)
        image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 15)

        return image

    def rotate_button_fn(self, _):
        """Rotate 90 degress when button is pressed.  At no rotation set -1 and ignore in code"""
        if self.rotation < 2:
            self.rotation += 1
        else:
            self.rotation = -1

    def threshold_change(self, caller, value=None):
        """change thresholding value in slider when buttons pressed.  Set label value if buttons or slider changes"""
        if isinstance(caller, Button):
            self.threshold_slider.value += value
        self.threshold_label.text = str(int(self.threshold_slider.value))

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
        display_lines = "No succesful reads"
        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf > 40 and len(word) >= 8 and re.sub(r"[^A-Z0-9]", "", word) == word:
                blacklisted = False
                for black in BLACKLIST:
                    if black in word:
                        blacklisted = True

                if not any(d.serial_number == word for d in self.sickw_history) and not blacklisted:
                    sickw = sickw_results.SickwResults(word, sickw_results.APPLE_SERIAL_INFO)
                    self.sickw_history.append(sickw)
                if not blacklisted:
                    output = f"Conf: {conf} {word} Total: {len(self.sickw_history)} "
                    output += f"Matches: {sickw_results.SickwResults.search_list_for_serial(word, self.sickw_history)} "
                    output += f"Sucessful: {sickw_results.SickwResults.success_count(self.sickw_history)}"
                    display_lines += f" {output}\n"
                    print(display_lines)
        self.status.text = display_lines

        self.fps_current = time.time()
        fps = 1 / (self.fps_current - self.fps_previous)
        self.fps_previous = self.fps_current
        cv2.putText(threshed, str(round(fps, 2)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
        cv2.putText(serial_image, str(round(fps, 2)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)

        buf = cv2.flip(serial_image, 0).tobytes()

        texture = Texture.create(size=(config.CAM_WIDTH, config.CAM_HEIGHT), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.scanned_image.texture = texture

        buf = cv2.flip(threshed, 0).tobytes()

        texture = Texture.create(size=(config.CAM_WIDTH, config.CAM_HEIGHT), colorfmt="luminance")
        texture.blit_buffer(buf, colorfmt="luminance", bufferfmt="ubyte")
        self.threshed_image.texture = texture


class SerialCameraApp(App):
    """Get image from camera and start serial check"""

    def build(self):
        Window.left = 0  # 0
        Window.top = 0
        Window.size = (config.CAM_WIDTH / 2, config.CAM_HEIGHT * 0.7)
        return SerialCamera()


def start_gui():
    """start the gui, call from project or if run directly"""
    SerialCameraApp().run()


if __name__ == "__main__":
    start_gui()
