from .general import *
from .elements import *

# Custom overrides for UI elements
from settings.ui_override import *

current_module = __import__(__name__, fromlist=['*'])


def get_by_name(name):
    return getattr(current_module, name, None)
