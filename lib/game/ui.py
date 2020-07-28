import json
import os
from lib.functions import load_image


class Rect:
    """Class for working with rectangles."""

    def __init__(self, x1, y1, x2, y2, parent=None):
        """Class initialization.

        :param x1: left top corner width.
        :param y1: left top corner height.
        :param x2: right bottom corner width.
        :param y2: right bottom corner height.
        :param ui.Rect parent: parent rectangle.
        """
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.parent = parent
        self._tuple = self.x1, self.y1, self.x2, self.y2

    def __getitem__(self, index):
        """Get rect values by index same as rect object was a tuple."""
        return self._tuple[index]

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
                    parent=parent.parent)


class UIElement:
    """Class for working with UI elements."""

    def __init__(self, name="Test", text="Default text", threshold=120, chars=None, save_file=None, image=None,
                 text_rect=None, button_rect=None, description=None):
        """Class initialization.

        :param name: name of element.
        :param text: text of element.
        :param threshold: threshold of gray-scale for grabbing image's text.
        :param chars: available character in element's text.
        :param save_file: name of file for saving element.
        :param image: numpy.array image, if element is image without text.
        :param text_rect: rectangle of text.
        :param button_rect: rectangle of button, if element contains button.
        :param description: description of UI element.
        """
        self.name = name
        self.text = text
        self.threshold = threshold
        self.chars = chars
        self.save_file = save_file
        self.image = image
        self.rect = text_rect
        self.button = button_rect
        self.description = description
        self.scale = 3 if chars else 1

    @staticmethod
    def from_json(json_data, path_to_images):
        """Create UI element from JSON.

        :param json_data: JSON.
        :param path_to_images: path to images.

        :return: UI element.
        """
        for key in json_data:
            data = json_data[key]
            image = load_image(os.path.join(path_to_images or "", data['image_path'])) if 'image_path' in data else None
            text_rect = data['text_rect']
            text_rect = text_rect if not text_rect else Rect(text_rect['x1'], text_rect['y1'],
                                                             text_rect['x2'], text_rect['y2'])
            button_rect = data['button_rect']
            button_rect = button_rect if not button_rect else Rect(button_rect['x1'], button_rect['y1'],
                                                                   button_rect['x2'], button_rect['y2'])
            return UIElement(name=key, text=data['text'], threshold=data['image_threshold'], chars=data['chars'],
                             save_file=data['image_save_file'], image=image, text_rect=text_rect,
                             button_rect=button_rect, description=data['description'])


def load_ui_settings(path="settings/ui", path_to_images="images"):
    """Load UI settings from JSON files.

    :param path: path to settings.
    :param path_to_images: path to images.

    :return: dictionary with UI elements.
    """
    ui = {}
    for json_file in [pos_json for pos_json in os.listdir(path) if pos_json.endswith('.json')]:
        with open(os.path.join(path, json_file), encoding='utf-8') as json_data:
            for setting in json.load(json_data):
                u = UIElement.from_json(json_data=setting, path_to_images=path_to_images)
                ui[u.name] = u
    return ui


def load_game_modes(path="settings/game_modes.json"):
    """Load game modes info.

    :param path: path to settings.

    :return: dictionary of info.
    """
    with open(path, encoding='utf-8') as json_data:
        return json.load(json_data)


def load_daily_trivia(path="settings/daily_trivia.json"):
    """Load daily trivia's questions and answers.

    :param path: path to settings.

    :return: dictionary of questions and answers.
    """
    with open(path, encoding='utf-8') as json_data:
        return json.load(json_data)
