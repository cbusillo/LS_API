"""Class file for websocket consumer"""
import json
from channels.generic.websocket import WebsocketConsumer  # type: ignore
from asgiref.sync import async_to_sync


class LsFunctionsConsumer(WebsocketConsumer):
    """Class to handle websocket connections"""

    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("updates", self.channel_name)
        message = json.dumps(
            {"type": "connection_established", "message": "Connection established"}
        )
        self.send(text_data=message)

    def disconnect(self, _close_code):
        """Disconnect client from group"""
        async_to_sync(self.channel_layer.group_add("updates", self.channel_name))

    def receive(self, text_data: str = "", _bytes_data: bytes = b""):
        """send received message back to client"""
        message = text_data
        self.send(text_data=message)

    def status(self, event):
        """Update status group"""
        message = event["message"]
        self.send(text_data=json.dumps({"type": "status", "message": message}))
        print(message)
