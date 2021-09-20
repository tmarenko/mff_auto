import json
import os
from copy import deepcopy
from lib.functions import load_image, bgr_to_rgb as rgb_to_bgr


class Rect:
    """Class for working with rectangles."""

    def __init__(self, x1, y1, x2, y2, parent=None, name=""):
        """Class initialization.

        :param x1: left top corner width.
        :param y1: left top corner height.
        :param x2: right bottom corner width.
        :param y2: right bottom corner height.
        :param ui.Rect parent: parent rectangle.
        """
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.parent = parent

    def __getitem__(self, index):
        """Get rect values by index same as rect object was a tuple."""
        return (self.x1, self.y1, self.x2, self.y2)[index]

    @property
    def value(self):
        """Coordinate values of rectangle.

        :return: tuple of rectangle's coordinates.
        """
        return self.x1, self.y1, self.x2, self.y2

    @property
    def width(self):
        """Width of rectangle.

        :return: width.
        """
        return self.x2 - self.x1

    @property
    def height(self):
        """Height of rectangle.

        :return: height
        """
        return self.y2 - self.y1

    @property
    def global_rect(self):
        """Get global rect of current rect.

        :return: ui.Rect: global coordinates of the root rect.
        """
        if self.parent:
            return self.to_global(self.parent).global_rect
        return self

    def to_global(self, parent):
        """Transform rectangle coordinates to global coordinates of parent rectangle.

        :param ui.Rect parent: parent rectangle.

        :return: new ui.Rect with global coordinates.
        """
        return Rect(parent.x1 + parent.width * self.x1,
                    parent.y1 + parent.height * self.y1,
                    parent.x1 + parent.width * self.x2,
                    parent.y1 + parent.height * self.y2,
                    parent=parent.parent, name=self.name)


class UIElement:
    """Class for working with UI elements."""

    STABLE_MAX_HEIGHT_FOR_TESSERACT = 72  # 72 is stable on 720p/1080p/1440p

    description = None
    button_rect = None
    text_rect = None
    image_rect = None
    image = None
    text = None
    image_threshold = None
    text_threshold = None
    image_color = None
    color_to_convert = None
    available_characters = None
    tesseract_resize_height = STABLE_MAX_HEIGHT_FOR_TESSERACT

    def __init__(self, name="Test"):
        """Class initialization.

        :param name: name of element.
        """
        self.name = name

    def __str__(self):
        return self.name

    def copy(self):
        """Returns copy of an UI element."""
        return deepcopy(self)


def load_game_modes(path="settings/game_modes.json"):
    """Load game modes info.

    :param path: path to settings.

    :return: dictionary of info.
    """
    with open(path, encoding='utf-8') as json_data:
        return json.load(json_data)


def load_ui_image(path, images_folder="images"):
    # Emulator's screen operates in BGR mode. All loaded images must be converted
    image = rgb_to_bgr(load_image(os.path.join(images_folder, path)))
    return image
