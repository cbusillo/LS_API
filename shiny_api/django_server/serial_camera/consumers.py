"""Consumers for the serial camera app WS."""
import base64
import time
import cv2
import numpy as np
from channels.generic.websocket import WebsocketConsumer
import pytesseract


class CameraConsumer(WebsocketConsumer):
    """Class to receive and process frames"""

    desired_fps = 1
    last_processed_frame_time = None

    def connect(self):
        self.accept()

    def disconnect(self, code):
        pass

    def receive(self, text_data=None, bytes_data=None):
        current_time = time.time()

        if self.last_processed_frame_time is None or (current_time - self.last_processed_frame_time) >= 1 / self.desired_fps:
            self.process_frame(text_data)
            self.last_processed_frame_time = current_time

    def process_frame(self, text_data):
        if text_data == "" or text_data == "Hello Server!":
            return

        base64_data = text_data
        img_data = base64.b64decode(base64_data)
        img_array = np.frombuffer(img_data, dtype=np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, bw_img = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # OCR processing
        extracted_text = pytesseract.image_to_string(bw_img)

        _, buf = cv2.imencode(".png", bw_img)
        bw_img_base64 = base64.b64encode(buf).decode("utf-8")

        # Send the processed image
        self.send("image_stream: " + bw_img_base64)

        # Send the extracted text
        self.send("text_stream: " + extracted_text)
