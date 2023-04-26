"""Web socket consumer to receive and process frames from the client"""
import base64
from datetime import datetime, timedelta
import json
import time
import threading
import numpy
import cv2
import pytesseract
import pytz
from channels.generic.websocket import WebsocketConsumer


class CameraConsumer(WebsocketConsumer):
    """Class to receive and process frames"""

    desired_fps = 1
    last_processed_frame_time = None
    confidence_level = 0

    def connect(self):
        """Run when new connection is established"""
        self.accept()

    def receive(self, text_data=None, _bytes_data=None):
        """Run when new frame is received"""
        if text_data is None:
            return
        frame_data = json.loads(text_data)
        if self.is_frame_stale(frame_data.get("timestamp")):
            return

        frame_image_data = frame_data.get("image")
        if frame_image_data == b"":
            return

        if threading.active_count() < 10:
            ocr_thread = threading.Thread(target=self.process_frame, args=[frame_image_data])
            ocr_thread.start()

    def process_frame(self, text_data):
        """Process the frame"""
        start_time = time.time()
        if text_data == "" or text_data == "Hello Server!":
            return
        cv_image = self.image_to_cv2(text_data)

        extracted_text = self.get_text_from_image(cv_image)
        cleaned_text = self.clean_serial_text(extracted_text)

        self.send_text(cleaned_text)
        self.send_image(cv_image)
        finish_time = time.time()
        time_taken = finish_time - start_time
        print(f"{cleaned_text} {time_taken} seconds")

    def get_text_from_image(self, image) -> dict[str, str]:
        """Get dict from the image text"""
        image_data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            config="--psm 11 -c tessedit_char_whitelist=': 0123456789ABCDEFGHIJKLMNPQRTUVWXYZ'",
        )
        return image_data

    def clean_serial_text(self, ocr_words):
        """Clean the serial text"""
        serial_text = {}
        for confidence, word in zip(ocr_words["conf"], ocr_words["text"]):
            word = word.replace(":", "").strip()
            if confidence < self.confidence_level or len(word) < 8:
                continue
            serial_text[word] = confidence

        return serial_text

    def image_to_cv2(self, base64_data):
        """process the image for computer vision"""
        image_data = base64.b64decode(base64_data)
        image_array = numpy.frombuffer(image_data, dtype=numpy.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        image_gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        image_denoise = cv2.fastNlMeansDenoising(image_gray, None, 10, 7, 21)  # pyright: reportGeneralTypeIssues=false

        image_edges = cv2.Canny(image_denoise, 100, 200)
        return image_edges

    def send_text(self, text: list[str]):
        """Send the serial text"""

        self.send(f"text_stream: {' '.join(text)}")

    def send_image(self, image):
        """Send the serial text"""
        _, buffer = cv2.imencode(".png", image)
        edge_image_base64 = base64.b64encode(buffer).decode("utf-8")
        self.send("image_stream: " + edge_image_base64)

    def is_frame_stale(self, timestamp):
        """Check if the frame is stale"""
        timezone = pytz.timezone("America/New_York")
        frame_datetime = datetime.fromisoformat(timestamp)
        frame_datetime = frame_datetime.astimezone(timezone)
        current_time = datetime.now().astimezone(timezone)
        time_difference = current_time - frame_datetime
        return time_difference > timedelta(seconds=1)
