import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import accounts.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wego_backend.settings")

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(accounts.routing.websocket_urlpatterns),
})