from datetime import datetime
from PIL import ImageDraw, ImageFont
from threading import Thread
import cv2
import numpy
import os
import win32api
import win32con

import lib.logger as logging
logger = logging.get_logger(__name__)

ELEMENT_TIME_ON_SCREEN_SEC = 1.5
ELEMENTS_WIDTH = 10


class ElementOnScreen:
    """Class for working with elements on screen."""

    GREEN_COLOR = "#00ff00"
    CYAN_COLOR = "#00ffff"
    MAGENTA_COLOR = "#ff00ff"
    RED_COLOR = "#ff0000"

    def __init__(self, name=None, color=None, box=None, position=None):
        """Class initialization."""
        self.time = datetime.now()
        self.box = box
        self.position = position
        self.name = name
        self.color = color

    @property
    def on_screen_seconds(self):
        """Returns total seconds of how long is element on screen."""
        return (datetime.now() - self.time).total_seconds()


class NoxPlayerSource:
    """Class for getting frames from Nox Player."""

    def __init__(self, player):
        """Class initialization.

        :param player.NoxWindow player: instance of game player.
        """
        self.player = player
        self.player.screen_elements = []
        self.font = ImageFont.load_default()
        self.player.get_screen_text = self.get_screen_text_decorator(self.player, self.player.get_screen_text)
        self.player.get_image_from_image = self.get_image_from_image_decorator(self.player,
                                                                               self.player.get_image_from_image)
        self.player.is_ui_element_on_screen = self.is_ui_element_on_screen_decorator(self.player,
                                                                                     self.player.is_ui_element_on_screen)
        self.player.is_image_on_screen = self.is_image_on_screen_decorator(self.player,
                                                                           self.player.is_image_on_screen)
        win32api.PostMessage = self.win32api_post_message_decorator(self.player, win32api.PostMessage)

    def frame(self):
        """Get frame from Nox Player.

        :return: RGB numpy array of frame.
        """
        image = numpy.array(self.get_player_screen())
        rgb_image = image[..., ::-1]
        return rgb_image

    def get_player_screen(self):
        """Get player screen and add debug drawings on it.

        :return: PIL.Image image.
        """
        screen = self.player._get_screen().copy()
        self.player.screen_elements = [element for element in self.player.screen_elements
                                       if element.on_screen_seconds < ELEMENT_TIME_ON_SCREEN_SEC]
        if self.player.screen_elements:
            draw = ImageDraw.Draw(screen)
            for element in self.player.screen_elements:
                if element.position:
                    x, y = element.position
                    r = ELEMENTS_WIDTH
                    ex, ey = ((x - r), (y - r)), ((x + r), (y + r))
                    draw.ellipse(xy=(ex, ey), fill=element.color)
                if element.box:
                    current_time = element.on_screen_seconds
                    l1 = [0, ELEMENT_TIME_ON_SCREEN_SEC]
                    l2 = [ELEMENTS_WIDTH, 0]
                    draw.rectangle(xy=element.box, outline=element.color, width=int(numpy.interp(current_time, l1, l2)))
                if element.name:
                    w, h = draw.textsize(element.name, self.font)
                    x, y = (element.box[0] + element.box[2] - w) / 2, (element.box[1] + element.box[3] - h) / 2
                    draw.text(xy=(x, y), text=element.name, font=self.font, fill=ElementOnScreen.GREEN_COLOR)
        return screen

    @staticmethod
    def get_screen_text_decorator(player, get_screen_text):
        """player.get_screen_text decorator for debug drawing of rectangle."""
        def wrapped(ui_element, screen=None):
            box = (ui_element.rect.global_rect[0] * player.width, ui_element.rect.global_rect[1] * player.height,
                   ui_element.rect.global_rect[2] * player.width, ui_element.rect.global_rect[3] * player.height)
            element = ElementOnScreen(name=ui_element.name, box=box, color=ElementOnScreen.GREEN_COLOR)
            player.screen_elements.append(element)
            return get_screen_text(ui_element=ui_element, screen=screen)
        return wrapped

    @staticmethod
    def get_image_from_image_decorator(player, get_image_from_image):
        """player.get_image_from_image decorator for debug drawing of rectangle."""
        def wrapped(image, ui_element):
            box = (ui_element.rect.global_rect[0] * player.width, ui_element.rect.global_rect[1] * player.height,
                   ui_element.rect.global_rect[2] * player.width, ui_element.rect.global_rect[3] * player.height)
            element = ElementOnScreen(name=ui_element.name, box=box, color=ElementOnScreen.GREEN_COLOR)
            player.screen_elements.append(element)
            return get_image_from_image(image=image, ui_element=ui_element)
        return wrapped

    @staticmethod
    def is_ui_element_on_screen_decorator(player, is_ui_element_on_screen):
        """player.is_ui_element_on_screen decorator for debug drawing of rectangle."""
        def wrapped(ui_element, screen=None):
            on_screen = is_ui_element_on_screen(ui_element=ui_element, screen=screen)
            if on_screen and not os.path.exists(f"debug_screen\\{ui_element.name}.png"):
                player.last_frame.copy().save(f"debug_screen\\{ui_element.name}.png")
            elements = [element for element in player.screen_elements if element.name == ui_element.name]
            for element in elements:
                element.color = ElementOnScreen.MAGENTA_COLOR if on_screen else element.color
            return on_screen
        return wrapped

    @staticmethod
    def is_image_on_screen_decorator(player, is_image_on_screen):
        """player.is_image_on_screen decorator for debug drawing of image rectangle."""
        def wrapped(ui_element, screen=None):
            rect = ui_element.rect if ui_element.rect else ui_element.button
            box = (rect.global_rect[0] * player.width, rect.global_rect[1] * player.height,
                   rect.global_rect[2] * player.width, rect.global_rect[3] * player.height)
            element = ElementOnScreen(name=ui_element.name, box=box, color=ElementOnScreen.CYAN_COLOR)
            player.screen_elements.append(element)
            on_screen = is_image_on_screen(ui_element=ui_element, screen=screen)
            element.color = ElementOnScreen.MAGENTA_COLOR if on_screen else element.color
            return on_screen
        return wrapped

    @staticmethod
    def win32api_post_message_decorator(player, post_message):
        """win32api.PostMessage decorator for debug drawing of click or drag."""
        def wrapped(*args, **kwargs):
            if args[1] == win32con.WM_MOUSEMOVE:
                dword = args[3]
                x, y = dword & 0xffff, dword >> 16
                element = ElementOnScreen(position=(x, y), color=ElementOnScreen.RED_COLOR)
                player.screen_elements.append(element)
            return post_message(*args, **kwargs)
        return wrapped


class NoxVideoWriter:
    """Class for writing frames to video."""

    def __init__(self, nox_player, output, fps=20.0):
        """Class initialization.

        :param player.NoxWindow nox_player: instance of game player.
        :param output: name of video output file.
        """
        self.source = NoxPlayerSource(nox_player)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # without dll
        # fourcc = cv2.VideoWriter_fourcc(*'avc1') # less size but requires `openh264` .dll in root folder
        # use this link for example: http://ciscobinary.openh264.org/openh264-1.8.0-win32.dll.bz2
        self.video_writer = cv2.VideoWriter(f'{output}.mp4', fourcc, fps, (self.source.player.width,
                                                                           self.source.player.height))

    def release(self):
        """Release video writer."""
        self.video_writer.release()
        cv2.destroyAllWindows()

    def frame(self):
        """Get frame from source.

        :return: frame.
        """
        return self.source.frame()

    def write(self, frame):
        """Write frame to video.

        :param frame: frame.
        """
        self.video_writer.write(frame)


class NoxCapture:
    """Class for capturing video from Nox Player."""

    def __init__(self, nox_player):
        """Class initialization.

        :param player.NoxWindow nox_player: instance of game player.
        """
        output = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        self.video_capture = NoxVideoWriter(nox_player, f"logs/{output}")
        self.thread = Thread(target=self.capture)
        self.thread.daemon = True
        self._pause = False

    def __enter__(self):
        """Context manager's enter."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager's exit."""
        self.stop()

    def capture(self):
        """Capture video."""
        logger.debug("Started capturing Nox Player.")
        while True:
            if not self._pause:
                frame = self.video_capture.frame()
                self.video_capture.write(frame)

    def start(self):
        """Start capturing."""
        self.thread.start()

    def stop(self):
        """Stop capturing."""
        logger.debug("Stopping video capture.")
        self.video_capture.release()

    def pause(self):
        """Pause capturing."""
        logger.debug("Pausing video capture.")
        self._pause = True

    def resume(self):
        """Resume capturing."""
        logger.debug("Resuming video capture.")
        self._pause = False

