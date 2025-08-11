"""
ASGI config for SchoolManagementSystem project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from channels.routing import ProtocolTypeRouter, URLRouter
from chats.middleware import JWTAuthMiddleware
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import chats.routing 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SchoolManagementSystem.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": JWTAuthMiddleware(   # <<<< WRAP YOUR websocket URL ROUTER
        URLRouter(
            chats.routing.websocket_urlpatterns
        )
    ),
})