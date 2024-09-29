"""
ASGI config for data_management_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path, re_path
from user_management.consumers import MachineDataConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_management_system.settings')

websocket_urlpatterns = [
    re_path(r'ws/machine_data/$', MachineDataConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns) 
    ),
})
