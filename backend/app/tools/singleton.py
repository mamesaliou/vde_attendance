import threading
from typing import Dict


def singleton(cls):

    class SingleClass(cls):  # pylint: disable=too-few-public-methods
        _instance = None
        __module__ = cls.__module__
        __doc__ = cls.__doc__

        def __new__(cls, *args, **kwargs):
            if SingleClass._instance is None:
                SingleClass._instance = super(SingleClass, cls).__new__(cls, *args, **kwargs)
                SingleClass._instance._sealed = False

            return SingleClass._instance

        def __init__(self):
            if not getattr(self, '_sealed', False):
                super().__init__()
                self._sealed = True

    SingleClass.__name__ = cls.__name__
    return SingleClass


class Singleton(type):
    _instances: Dict[object, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._instances:
            with Singleton._lock:
                Singleton._instances.setdefault(cls, super().__call__(*args, **kwargs))
        return Singleton._instances[cls]