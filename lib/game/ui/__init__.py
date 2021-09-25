from .elements import *
from .general import *

# Custom overrides for UI elements
from settings.ui_override import *

current_module = __import__(__name__, fromlist=['*'])


def get_by_name(name):
    """Get UIElement or other attribute by name from all modules inside `ui` module.

    :param str name: name of UIElement or attribute.
    """
    return getattr(current_module, name, None)
