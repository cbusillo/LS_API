import json
from channels_redis.core import RedisChannelLayer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class LsFunctionsConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        async_to_sync(self.channel_layer.group_add)("updates", self.channel_name)
        message = json.dumps(
            {"type": "connection_established", "message": "Connection established"}
        )
        self.send(text_data=message)

    def disconnect(self, _close_code):
        async_to_sync(self.channel_layer.group_add("updates", self.channel_name))

    def receive(self, text_data):
        message = text_data
        self.send(text_data=message)

    def status(self, event):
        message = event["message"]
        self.send(text_data=json.dumps({"type": "status", "message": message}))
        print(message)
