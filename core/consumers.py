import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from django.contrib.auth.models import AnonymousUser


class NotificationConsumer(WebsocketConsumer):
    group_name = 'notification'

    def connect(self):
        if not isinstance(self.scope["user"], AnonymousUser):
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()

    def disconnect(self, event):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_notification(self, event):
        self.send(json.dumps({
            "type": "websocket.send",
            "data": event.get("value")
        }))


class ErrorConsumer(WebsocketConsumer):
    group_name = 'error'

    def connect(self):
        if not isinstance(self.scope["user"], AnonymousUser):
            async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
            self.accept()

    def disconnect(self, event):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def send_error(self, event):
        self.send(json.dumps({
            "type": "websocket.send",
            "data": event.get("value")
        }))
