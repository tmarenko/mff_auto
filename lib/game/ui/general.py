import os
from copy import deepcopy
from lib.functions import load_image, bgr_to_rgb as rgb_to_bgr


class Rect:
    """Class for working with rectangles."""

    def __init__(self, x1, y1, x2, y2, parent=None, name=""):
        """Class initialization.

        :param float x1: left top corner width.
        :param float y1: left top corner height.
        :param float x2: right bottom corner width.
        :param float y2: right bottom corner height.
        :param Rect parent: parent rectangle.
        """
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.parent = parent

    def __getitem__(self, index):
        """Gets rect values by index same as rect object was a tuple."""
        return (self.x1, self.y1, self.x2, self.y2)[index]

    @property
    def value(self):
        """Coordinate values of rectangle.

        :rtype: tuple[float, float, float, float]
        """
        return self.x1, self.y1, self.x2, self.y2

    @property
    def width(self):
        """Width of rectangle.

        :rtype: float
        """
        return self.x2 - self.x1

    @property
    def height(self):
        """Height of rectangle.

        :rtype: float
        """
        return self.y2 - self.y1

    @property
    def global_rect(self):
        """Gets rect with global coordinates relative to parent's coordinates.

        :rtype: Rect
        """
        if self.parent:
            return self.to_global(self.parent).global_rect
        return self

    def to_global(self, parent):
        """Transforms rectangle coordinates to global coordinates of parent rectangle.

        :param Rect parent: parent rectangle.

        :return: new Rect with global coordinates.
        :rtype: Rect
        """
        return Rect(parent.x1 + parent.width * self.x1,
                    parent.y1 + parent.height * self.y1,
                    parent.x1 + parent.width * self.x2,
                    parent.y1 + parent.height * self.y2,
                    parent=parent.parent, name=self.name)


class UIElement:
    """Class for working with UI elements."""

    STABLE_MAX_HEIGHT_FOR_TESSERACT = 72  # 72 is stable on 720p/1080p/1440p

    description = None  # type: str
    button_rect = None  # type: Rect
    text_rect = None  # type: Rect
    image_rect = None  # type: Rect
    image = None  # type: numpy.ndarray
    text = None  # type: str
    image_threshold = None  # type: int
    text_threshold = None  # type: int
    image_color = None  # type: (int, int, int)
    color_to_convert = None  # type: ((int, int, int), )
    available_characters = None  # type: str
    tesseract_resize_height = STABLE_MAX_HEIGHT_FOR_TESSERACT  # type: int
    offset = None  # type: Rect

    def __init__(self, name="Test"):
        """Class initialization.

        :param str name: name of element.
        """
        self.name = name

    def __str__(self):
        return self.name

    def copy(self):
        """Returns copy of an UI element.

        :rtype: UIElement
        """
        return deepcopy(self)


def load_ui_image(path, images_folder="images"):
    """Loads image into UI element and converts it to RGB.

    :param str path: path to image.
    :param str images_folder: path to `images` folder.

    :rtype: numpy.ndarray
    """
    # Emulator's screen operates in BGR mode. All loaded images must be converted
    image = rgb_to_bgr(load_image(os.path.join(images_folder, path)))
    return image
