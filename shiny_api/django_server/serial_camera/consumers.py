"""Websocket consumer to receive image from client and send back a black and white image"""
import base64
from io import BytesIO
from channels.generic.websocket import WebsocketConsumer
from PIL import Image


class CameraConsumer(WebsocketConsumer):
    """Class to receive image from client and send back a black and white image"""

    def connect(self):
        """Connect client"""
        self.accept()

    def disconnect(self, code):
        """Disconnect client from group"""
        self.disconnect(code)

    def receive(self, text_data=None, _bytes_data=None):
        """send received message back to client"""
        if "," in text_data:
            base64_data = text_data.split(",")[1]  # Only decode the base64 data after the comma
        else:
            base64_data = text_data

        img_data = base64.b64decode(base64_data)
        img = Image.open(BytesIO(img_data))
        gray = img.convert("L")  # Convert to grayscale
        bw_img = gray.point(lambda x: 0 if x < 128 else 255, "1")  # Convert to 1-bit image
        output_buffer = BytesIO()
        bw_img.save(output_buffer, format="PNG")
        bw_img_base64 = base64.b64encode(output_buffer.getvalue()).decode("utf-8")
        self.send(bw_img_base64)
