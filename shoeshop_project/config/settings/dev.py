from .base import *

DEBUG = True

if DEBUG:
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]


def custom_show_toolbar(request):
    return False


DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}

INSTALLED_APPS += ['debug_toolbar', ]

ALLOWED_HOSTS = [
    '127.0.0.1',
    'localhost',
    'app',
    'postgres',
    '5.35.85.27',
]