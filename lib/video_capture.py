from datetime import datetime
from PIL import ImageDraw, ImageFont
from threading import Thread
from multiprocess.managers import SyncManager, RemoteError
from lib.functions import bgr_to_rgb
from lib.game import ui
import autoit
import cv2
import numpy
import os
import time
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


class EmulatorImageSource:
    """Class for getting frames from Android emulator."""

    def __init__(self, emulator):
        """Class initialization.

        :param emulator: instance of Android emulator.
        """
        self.emulator = emulator
        self.emulator.manager = SyncManager()
        self.emulator.manager.start()
        self.emulator.screen_elements = self.emulator.manager.list()
        self.font = ImageFont.load_default()
        self._decorate()
        self.ui = ui.load_ui_elements()

    def _decorate(self):
        logger.debug("Decorating function for video capture.")
        self._click_button = self.emulator.click_button
        self._get_screen_text = self.emulator.get_screen_text
        self._get_image_from_image = self.emulator.get_image_from_image
        self._is_ui_element_on_screen = self.emulator.is_ui_element_on_screen
        self._is_image_on_screen = self.emulator.is_image_on_screen
        self._PostMessage = self.emulator.win32_api_post_message
        self._control_click_by_handle = self.emulator.autoit_control_click_by_handle

        self.emulator.click_button = self.click_button_decorator(self.emulator, self.emulator.click_button)
        self.emulator.get_screen_text = self.get_screen_text_decorator(self.emulator, self.emulator.get_screen_text)
        self.emulator.get_image_from_image = self.get_image_from_image_decorator(self.emulator,
                                                                                 self.emulator.get_image_from_image)
        self.emulator.is_ui_element_on_screen = self.is_ui_element_on_screen_decorator(self.emulator,
                                                                                       self.emulator.is_ui_element_on_screen)
        self.emulator.is_image_on_screen = self.is_image_on_screen_decorator(self.emulator,
                                                                             self.emulator.is_image_on_screen)
        self.emulator.win32_api_post_message = self.win32api_post_message_decorator(self.emulator, win32api.PostMessage)
        self.emulator.autoit_control_click_by_handle = self.control_click_by_handle_decorator(self.emulator,
                                                                                              autoit.control_click_by_handle)

    def undecorate(self):
        logger.debug("Reverting functions to original state.")
        self.emulator.get_screen_text = self._get_screen_text
        self.emulator.get_image_from_image = self._get_image_from_image
        self.emulator.is_ui_element_on_screen = self._is_ui_element_on_screen
        self.emulator.is_image_on_screen = self._is_image_on_screen
        self.emulator.click_button = self._click_button
        self.emulator.win32_api_post_message = self._PostMessage
        self.emulator.autoit_control_click_by_handle = self._control_click_by_handle

    def frame(self):
        """Get frame from emulator.

        :return: RGB numpy array of frame.
        """
        image = numpy.array(self.get_emulator_screen())
        return bgr_to_rgb(image)

    def get_emulator_screen(self):
        """Get emulator's screen and add debug drawings on it.

        :return: PIL.Image image.
        """
        screen = self.emulator._get_screen().copy()
        try:
            self.emulator.screen_elements[:] = [element for element in self.emulator.screen_elements
                                                if element.on_screen_seconds < ELEMENT_TIME_ON_SCREEN_SEC]
            draw = ImageDraw.Draw(screen)
            self._hide_user_name(draw)
            for element in self.emulator.screen_elements:
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
        except (KeyError, OSError, RemoteError, EOFError):
            logger.debug(f"{self.__class__.__name__} got an error during it's closing.")
        return screen

    def _hide_user_name(self, draw):
        ui_element = self.ui['USER_NAME']
        box = (ui_element.rect.global_rect[0] * self.emulator.width, ui_element.rect.global_rect[1] * self.emulator.height,
               ui_element.rect.global_rect[2] * self.emulator.width, ui_element.rect.global_rect[3] * self.emulator.height)
        draw.rectangle(xy=box, outline="#000000", fill="#000000")

    @staticmethod
    def click_button_decorator(emulator, click_button):
        """emulator.click_button decorator for debug drawing of rectangle."""
        def wrapped(button_rect, **kwargs):
            box = (button_rect.global_rect[0] * emulator.width, button_rect.global_rect[1] * emulator.height,
                   button_rect.global_rect[2] * emulator.width, button_rect.global_rect[3] * emulator.height)
            element = ElementOnScreen(name="", box=box, color=ElementOnScreen.RED_COLOR)
            if emulator.screen_elements is not None:
                emulator.screen_elements.append(element)
            return click_button(button_rect=button_rect, **kwargs)
        return wrapped

    @staticmethod
    def get_screen_text_decorator(emulator, get_screen_text):
        """emulator.get_screen_text decorator for debug drawing of rectangle."""
        def wrapped(ui_element, screen=None):
            box = (ui_element.rect.global_rect[0] * emulator.width, ui_element.rect.global_rect[1] * emulator.height,
                   ui_element.rect.global_rect[2] * emulator.width, ui_element.rect.global_rect[3] * emulator.height)
            element = ElementOnScreen(name=ui_element.name, box=box, color=ElementOnScreen.GREEN_COLOR)
            if emulator.screen_elements is not None:
                emulator.screen_elements.append(element)
            return get_screen_text(ui_element=ui_element, screen=screen)
        return wrapped

    @staticmethod
    def get_image_from_image_decorator(emulator, get_image_from_image):
        """emulator.get_image_from_image decorator for debug drawing of rectangle."""
        def wrapped(image, ui_element):
            box = (ui_element.rect.global_rect[0] * emulator.width, ui_element.rect.global_rect[1] * emulator.height,
                   ui_element.rect.global_rect[2] * emulator.width, ui_element.rect.global_rect[3] * emulator.height)
            element = ElementOnScreen(name=ui_element.name, box=box, color=ElementOnScreen.GREEN_COLOR)
            if emulator.screen_elements is not None:
                emulator.screen_elements.append(element)
            return get_image_from_image(image=image, ui_element=ui_element)
        return wrapped

    @staticmethod
    def is_ui_element_on_screen_decorator(emulator, is_ui_element_on_screen):
        """emulator.is_ui_element_on_screen decorator for debug drawing of rectangle."""
        def wrapped(ui_element, screen=None):
            on_screen = is_ui_element_on_screen(ui_element=ui_element, screen=screen)
            elements = [element for element in emulator.screen_elements if element.name == ui_element.name]
            for element in elements:
                if emulator.screen_elements is not None and on_screen:
                    element.color = ElementOnScreen.MAGENTA_COLOR
                    emulator.screen_elements.append(element)
            return on_screen
        return wrapped

    @staticmethod
    def is_image_on_screen_decorator(emulator, is_image_on_screen):
        """emulator.is_image_on_screen decorator for debug drawing of image rectangle."""
        def wrapped(ui_element, screen=None):
            rect = ui_element.rect if ui_element.rect else ui_element.button
            box = (rect.global_rect[0] * emulator.width, rect.global_rect[1] * emulator.height,
                   rect.global_rect[2] * emulator.width, rect.global_rect[3] * emulator.height)
            element = ElementOnScreen(name=ui_element.name, box=box, color=ElementOnScreen.CYAN_COLOR)
            on_screen = is_image_on_screen(ui_element=ui_element, screen=screen)
            element.color = ElementOnScreen.MAGENTA_COLOR if on_screen else element.color
            if emulator.screen_elements is not None:
                emulator.screen_elements.append(element)
            return on_screen
        return wrapped

    @staticmethod
    def win32api_post_message_decorator(emulator, post_message):
        """win32api.PostMessage decorator for debug drawing of click or drag."""
        def wrapped(*args, **kwargs):
            if args[1] == win32con.WM_MOUSEMOVE:
                dword = args[3]
                x, y = dword & 0xffff, dword >> 16
                element = ElementOnScreen(position=(x, y), color=ElementOnScreen.RED_COLOR)
                if emulator.screen_elements is not None:
                    emulator.screen_elements.append(element)
            return post_message(*args, **kwargs)
        return wrapped

    @staticmethod
    def control_click_by_handle_decorator(emulator, control_click_by_handle):
        """autoit.control_click_by_handle decorator for debug drawing of click."""
        def wrapped(hwnd, h_ctrl, **kwargs):
            x, y = kwargs.get("x", 0), kwargs.get("y", 0)
            element = ElementOnScreen(position=(x, y), color=ElementOnScreen.RED_COLOR)
            if emulator.screen_elements is not None:
                emulator.screen_elements.append(element)
            return control_click_by_handle(hwnd, h_ctrl, **kwargs)
        return wrapped


class EmulatorVideoWriter:
    """Class for writing frames to video."""

    def __init__(self, emulator, output, fps=10.0):
        """Class initialization.

        :param emulator: instance of Android emulator.
        :param output: name of video output file.
        """
        self.source = EmulatorImageSource(emulator)
        self.fps = fps
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # without dll
        # fourcc = cv2.VideoWriter_fourcc(*'avc1') # less size but requires `openh264` .dll in root folder
        # use this link for example: http://ciscobinary.openh264.org/openh264-1.8.0-win32.dll.bz2
        self.video_writer = cv2.VideoWriter(f'{output}.mp4', fourcc, self.fps, (self.source.emulator.width,
                                                                                self.source.emulator.height))
        logger.info(f"Creating video capture with name '{output}.mp4'; "
                    f"{self.source.emulator.width}x{self.source.emulator.height}@{self.fps}")

    def release(self):
        """Release video writer."""
        self.video_writer.release()
        self.source.undecorate()
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


class EmulatorCapture:
    """Class for capturing video from Android emulator."""

    def __init__(self, emulator):
        """Class initialization.

        :param emulator: instance of Android emulator.
        """
        output = datetime.now().strftime("%Y-%m-%d_%H.%M.%S")
        self.video_capture = EmulatorVideoWriter(emulator, f"logs/{output}")
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
        logger.debug("Started capturing video.")
        fps_wait = 1 / self.video_capture.fps
        while True:
            if not self._pause:
                frame = self.video_capture.frame()
                self.video_capture.write(frame)
            else:
                time.sleep(fps_wait)

    def start(self):
        """Start capturing."""
        self.thread.start()

    def stop(self):
        """Stop capturing."""
        logger.debug("Stopping video capture.")
        self.video_capture.release()
        self._pause = True

    def pause(self):
        """Pause capturing."""
        logger.debug("Pausing video capture.")
        self._pause = True

    def resume(self):
        """Resume capturing."""
        logger.debug("Resuming video capture.")
        self._pause = False
