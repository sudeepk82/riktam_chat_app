from channels.routing import ProtocolTypeRouter, URLRouter
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "riktam.settings")

import django

django.setup()


# import app.routing
from django.core.asgi import get_asgi_application
from django.urls import re_path
from chat_app.consumers import GroupConsumer, ChatRoomConsumer
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

websocket_urlpatterns = [
    re_path(r"^ws/chat_app_groups/$", GroupConsumer.as_asgi()),
    re_path(r"^ws/(?P<group_id>[^/]+)/$", ChatRoomConsumer.as_asgi()),
    # re_path(r"^ws/riktam_chat_app/$", AppConsumer.as_asgi()),
]
# the websocket will open at 127.0.0.1:8000/ws/<room_name>
application = ProtocolTypeRouter(
    {
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
        "http": get_asgi_application(),
    },
)
