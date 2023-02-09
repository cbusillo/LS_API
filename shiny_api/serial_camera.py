"""Take picture from webcam"""
import os
import threading
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
from kivy.uix.checkbox import CheckBox
from kivy.uix.image import Image
from kivy.uix.gridlayout import GridLayout
from kivy.uix.slider import Slider
import numpy as np
from shiny_api.modules import load_config as config
from shiny_api.classes import sickw_results
from shiny_api.classes.google_sheets import GoogleSheet
from shiny_api.modules.label_print import print_text

print(f"Importing {os.path.basename(__file__)}...")

# Ignore serial number if it contains an item from this list
BLACKLIST = ["BCGA"]


def rotate_image(image, angle):
    """Take image and angle and return rotated image"""
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result


def compute_skew(source_image) -> float:
    """Take image and return angle of text"""
    if len(source_image.shape) == 3:
        height, width, _ = source_image.shape
    elif len(source_image.shape) == 2:
        height, width = source_image.shape
    else:
        print("upsupported image type")

    image = cv2.medianBlur(source_image, 3)
    edges = cv2.Canny(image, threshold1=30, threshold2=100, apertureSize=3, L2gradient=True)
    lines = cv2.HoughLinesP(edges, 1, math.pi / 180, 30, minLineLength=width / 4.0, maxLineGap=height / 4.0)
    total_angle = 0.0

    count = 0
    if lines is None:
        return 0.0
    for x_1, y_1, x_2, y_2 in lines[0]:
        angle = np.arctan2(y_2 - y_1, x_2 - x_1)
        if math.fabs(angle) <= 30:  # excluding extreme rotations
            total_angle += angle
            count += 1

    if count == 0:
        return 0.0
    return (total_angle / count) * 180 / math.pi


def deskew(source_image):
    """Take image, find skew, remove skew, return image"""
    return rotate_image(source_image, compute_skew(source_image))


class SerialCamera(GridLayout):
    """Independent app to scan serials"""

    def __init__(self, **kwargs):
        """Create GUI and setup clocks to run image updates and OCR"""
        super(SerialCamera, self).__init__(**kwargs)

        self.cols = 1
        self.padding = 50

        self.rotate_image_button = Button(text="Rotate", size_hint=(0.1, 0.1))
        self.rotate_image_button.bind(on_press=self.rotate_image)
        self.add_widget(self.rotate_image_button)

        self.threshold_slider = Slider(min=0, max=255, value=180, size_hint=(1, 0.15))
        self.threshold_slider.bind(value=self.threshold_change)
        self.add_widget(self.threshold_slider)

        self.threshold_grid = GridLayout()
        self.threshold_grid.cols = 4
        self.threshold_grid.size_hint_y = 0.1

        self.threshold_auto_checkbox = CheckBox(size_hint=(0.1, None), active=True)
        self.threshold_grid.add_widget(self.threshold_auto_checkbox)
        self.threshold_down_button = Button(text="Threshold down")
        self.threshold_down_button.bind(on_press=partial(self.threshold_change, value=-5))
        self.threshold_grid.add_widget(self.threshold_down_button)

        self.threshold_label = Label(text=str(self.threshold_slider.value))
        self.threshold_grid.add_widget(self.threshold_label)

        self.threshold_up_button = Button(text="Threshold up")
        self.threshold_up_button.bind(on_press=partial(self.threshold_change, value=5))
        self.threshold_grid.add_widget(self.threshold_up_button)

        self.add_widget(self.threshold_grid)

        self.image_grid = GridLayout()
        self.image_grid.cols = 2

        self.original_image = None
        self.original_image_display = Image()
        self.original_image_display.width = cv2.CAP_PROP_FRAME_WIDTH
        self.original_image_display.height = cv2.CAP_PROP_FRAME_HEIGHT
        self.image_grid.add_widget(self.original_image_display)

        self.threshed_image = None
        self.threshed_image_display = Image()
        self.threshed_image_display.width = cv2.CAP_PROP_FRAME_WIDTH
        self.threshed_image_display.height = cv2.CAP_PROP_FRAME_HEIGHT
        self.image_grid.add_widget(self.threshed_image_display)

        self.add_widget(self.image_grid)

        self.status = Label(size_hint=(0.8, 0.2))
        self.add_widget(self.status)

        self.capture_grid = GridLayout(size_hint=(1, 0.1), cols=2)
        self.capture_grid.capture_auto = CheckBox(size_hint=(0.1, None))
        self.capture_grid.add_widget(self.capture_grid.capture_auto)
        self.capture_grid.capture_button = Button(text="Capture Serial")
        self.capture_grid.capture_button.bind(on_press=self.run_ocr)
        self.capture_grid.add_widget(self.capture_grid.capture_button)
        self.add_widget(self.capture_grid)

        self.capture = cv2.VideoCapture(config.CAM_PORT)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, config.CAM_WIDTH)

        Clock.schedule_interval(self.capture_image, 1 / 30)
        Clock.schedule_interval(self.update_threshed_image, 1 / 5)
        Clock.schedule_interval(self.run_ocr, 0.1)
        self.sickw_history = []
        self.rotation = -1
        self.serial_sheet = GoogleSheet("Shiny API")

    def thresh_image(self, image):
        """Take grayscale image and return Threshholded image.  Use value from slider or auto if checked"""
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = deskew(image)
        if self.threshold_auto_checkbox.active:
            image = cv2.adaptiveThreshold(image, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 7, 7)
        else:
            _, image = cv2.threshold(image, self.threshold_slider.value, 255, cv2.THRESH_BINARY)

        return image

    def capture_image(self, delta_time):
        """Capture image on 30fps clock to original_image and set to texture"""
        result, self.original_image = self.capture.read()
        if not result:
            self.capture.set(1280, 720)
            result, self.original_image = self.capture.read()
        if not result:
            return
        if self.rotation > -1:
            self.original_image = cv2.rotate(self.original_image, self.rotation)

        self.original_image_display.texture = self.update_image_texture(self.original_image, "bgr", 1 / delta_time)

    def update_threshed_image(self, delta_time: float):
        """Update threshed image and texture from original on clock"""
        self.threshed_image = self.thresh_image(self.original_image)
        self.threshed_image_display.texture = self.update_image_texture(self.threshed_image, "luminance", 1 / delta_time)

    def rotate_image(self, _):
        """Rotate 90 degress when button is pressed.  At no rotation set -1 and ignore in code"""
        if self.rotation < 2:
            self.rotation += 1
        else:
            self.rotation = -1

    def threshold_change(self, caller, value=None):
        """change thresholding value in slider when buttons pressed.
        Set label value if buttons or slider changes.  Deactivate auto check"""
        self.threshold_auto_checkbox.active = False
        if isinstance(caller, Button):
            self.threshold_slider.value += value
        self.threshold_label.text = str(int(self.threshold_slider.value))

    def run_ocr(self, caller):
        """Start a thread to OCR on each clock"""
        if isinstance(caller, Button) or self.capture_grid.capture_auto.active is True:
            if threading.active_count() < 2:
                ocr_thread = threading.Thread(target=self.ocr_thread)
                ocr_thread.start()

    def ocr_thread(self):
        """Use Tesseract to read data from threshed image"""
        if self.threshed_image is None:
            return
        serial_image_data = pytesseract.image_to_data(
            self.threshed_image,
            output_type=pytesseract.Output.DICT,
            config="--psm 11",  # -c tessedit_char_whitelist=' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'",
        )
        self.status.text = self.find_valid_serial(serial_image_data)

    def find_valid_serial(self, serial_image_data) -> str:
        """Filter out stuff that cannot be serial number, needs to be at least eight characters and all uppercase.
        Filter blacklist words. Check if sickw recognizes serial.  Store to history table in memory including sickw status."""
        output = ""
        display_lines = ""
        for conf, word in zip(serial_image_data["conf"], serial_image_data["text"]):
            if conf < 40 or len(word) < 8:
                continue
            if re.sub(r"[^A-Z0-9]", "", word) != word:
                continue
            for black in BLACKLIST:
                if black in word:
                    continue

            if not any(d.serial_number == word for d in self.sickw_history):
                sickw = sickw_results.SickwResults(word, sickw_results.APPLE_SERIAL_INFO)
                self.sickw_history.append(sickw)
                if sickw.status.lower() == "success":
                    self.serial_sheet.add_line(sickw_results.SickwResults(word, sickw_results.APPLE_SERIAL_INFO))
                    if config.GOOGLE_SHEETS_SERIAL_PRINT:
                        print_text(text=sickw.name, barcode=sickw.serial_number)
            output = f"Conf: {conf} {word} Total: {len(self.sickw_history)} "
            output += f"Matches: {sickw_results.SickwResults.search_list_for_serial(word, self.sickw_history)} "
            output += f"Sucessful: {sickw_results.SickwResults.success_count(self.sickw_history)}"
            display_lines += f" {output}\n"
            print(display_lines)
        if not output:
            output = "No reads"
        return output

    def update_image_texture(self, image, color_format: str, fps: float = 0) -> Texture:
        """Takes and image and returns a flipped texture.  Display FPS"""
        cv2.putText(image, str(round(fps, 2)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 0), 3)
        cv2.putText(image, str(round(fps, 2)), (10, 140), cv2.FONT_HERSHEY_PLAIN, 3, (255, 255, 255), 3)

        buf = cv2.flip(image, 0).tobytes()
        texture = Texture.create(size=(image.shape[1], image.shape[0]), colorfmt=color_format)
        texture.blit_buffer(buf, colorfmt=color_format, bufferfmt="ubyte")
        return texture


class SerialCameraApp(App):
    """Get image from camera and start serial check"""

    def build(self):
        Window.left = 300  # 0
        Window.top = 300
        Window.size = (config.CAM_WIDTH / 2, config.CAM_HEIGHT * 0.7)
        return SerialCamera()


def start_gui():
    """start the gui, call from project or if run directly"""
    SerialCameraApp().run()


if __name__ == "__main__":
    start_gui()
