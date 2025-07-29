import atexit
import sys

from django.conf import settings
from kazoo.client import KazooClient

_instance = None

def _exit():
    global _instance
    _instance.stop()
    _instance = None

def get_zookeeper():
    global _instance

    if _instance is not None:
        return _instance

    _instance = KazooClient(hosts=settings.ZOOKEEPER, timeout=120)
    _instance.start()
    atexit.register(_exit)

    return _instance
