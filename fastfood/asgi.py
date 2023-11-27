"""
ASGI config for fastfood project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""
import os

import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack, BaseMiddleware
from django.conf.urls import url
from django.urls import path
from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fastfood.settings')
django_asgi_app = get_asgi_application()


from core import consumers


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(
                [
                    url(r'order/list/notification/', consumers.NotificationConsumer.as_asgi()),
                    url(r'order/info/error/', consumers.ErrorConsumer.as_asgi()),
                ]
            )
        )
    }
)
