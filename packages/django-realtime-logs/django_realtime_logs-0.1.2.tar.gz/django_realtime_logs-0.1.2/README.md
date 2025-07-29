# django-realtime-logs

A real-time log viewer for Django using WebSocket and Django Channels.  
It allows developers to view server logs live in the browser, making debugging easier without relying on external tools like Grafana.

---

## Features

- Real-time streaming of your Django `runtime.log` file via WebSocket.
- Simple UI to display logs with auto-scrolling.
- Built as a reusable Django app, easy to integrate.
- Uses Django Channels for WebSocket support.
- Lightweight and minimal dependencies.

---

## Installation

```bash
pip install django-realtime-logs
```

## Usage

- Add `django_realtime_logs` to `INSTALLED_APPS`
In your settings.py, add:
```bash
INSTALLED_APPS = [
    # existing apps...
    'django_realtime_logs',
]

ASGI_APPLICATION = 'your_project_name.asgi.application'  # Replace with your ASGI module path

# Configure your channel layers (using InMemoryChannelLayer for development)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

```
- Configure Logging in settings.py
Make sure your logging configuration writes logs to runtime.log in your project directory:
```bash
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'runtime.log',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'DEBUG',
    },
}

```
- Include `/logs/` and set up WebSocket with ASGI(asgi.py)
Modify your asgi.py to route HTTP and WebSocket connections:
```bash
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django_realtime_logs.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(websocket_urlpatterns)),
})

```
- Include `/logs/` in urls.py
Add the logs route to your main urls.py:
```bash
path("logs/", include("django_realtime_logs.urls")),
```
-You must use an ASGI server like daphne or uvicorn to support WebSockets.
-Install daphne
```bash
pip install daphne
```
-Run the server
```bash
daphne -p 8001 your_project_name.asgi:application
```
Replace your_project_name with your Django project folder name.

- Visit `/logs/` in the browser
```bash
http://localhost:8001/logs/
```