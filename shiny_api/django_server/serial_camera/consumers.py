"""Web socket consumer to receive and process frames from the client"""
import base64
import time
import threading
import numpy
import cv2
import pytesseract
from channels.generic.websocket import WebsocketConsumer


class CameraConsumer(WebsocketConsumer):
    """Class to receive and process frames"""

    desired_fps = 1
    last_processed_frame_time = None

    def connect(self):
        """Run when new connection is established"""
        self.accept()

    def receive(self, text_data=None, bytes_data=None):
        """Run when new frame is received"""
        current_time = time.time()

        if self.last_processed_frame_time is None or (current_time - self.last_processed_frame_time) >= 1 / self.desired_fps:
            if threading.active_count() < 5:
                ocr_thread = threading.Thread(target=self.process_frame, args=[text_data])
                ocr_thread.start()
            self.last_processed_frame_time = current_time

    def process_frame(self, text_data):
        """Process the frame"""
        if text_data == "" or text_data == "Hello Server!":
            return
        cv_image = self.image_to_cv2(text_data)

        extracted_text = self.get_text_from_image(cv_image)
        cleaned_text = self.clean_serial_text(extracted_text)

        self.send_text(cleaned_text)
        self.send_image(cv_image)

    def get_text_from_image(self, image) -> dict[str, str]:
        """Get dict from the image text"""
        image_data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT,
            config="--psm 11",  # -c tessedit_char_whitelist=' 0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'",
        )
        return image_data

    def clean_serial_text(self, ocr_words):
        """Clean the serial text"""
        serial_text = {}
        for conf, word in zip(ocr_words["conf"], ocr_words["text"]):
            if conf < 40 or len(word) < 8:
                continue
            serial_text[word] = conf
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
