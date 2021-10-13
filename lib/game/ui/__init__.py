import lib.logger as logging
from .elements import *
from .general import *

# Custom overrides for UI elements
import settings.ui_override as ui_override

current_module = __import__(__name__, fromlist=['*'])
ui_override_module = __import__(ui_override.__name__, fromlist=['*'])

logger = logging.get_logger(__name__)


def get_by_name(name):
    """Get UIElement or other attribute by name from all modules inside `ui` module.

    :param str name: name of UIElement or attribute.
    """
    return getattr(current_module, name, None)


def find_names_of_module(module):
    import ast

    with open(module.__file__, encoding='utf-8-sig') as f:
        code = f.read()

    tree = ast.parse(code)
    assignments = (node for node in tree.body if isinstance(node, ast.Assign))
    return {target.value.id for a in assignments for target in a.targets}


overrided = find_names_of_module(ui_override_module)
if overrided:
    logger.info(f"UI elements were override: {'; '.join(overrided)}")
