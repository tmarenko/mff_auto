import ctypes
import logging
import random
import time
from ctypes import windll
from distutils.version import LooseVersion
from platform import release

import autoit
import pywintypes
import win32api
import win32con
import win32gui
import win32process
import win32ui
from PIL import Image
from numpy import array

from lib.functions import get_text_from_image, is_strings_similar, is_images_similar, is_color_similar, r_sleep, \
    get_file_properties, convert_colors_in_image

PW_CLIENTONLY = 1  # Only the client area of the window is copied to hdcBlt. By default, the entire window is copied.
PW_RENDERFULLCONTENT = 2  # Properly capture DirectComposition window contents. Available from Windows 8.1

# Set process as high-DPI aware to get actual window's coordinates. Set WM_PAINT flag by OS version
if release() == "10":
    PRINT_FLAG = PW_RENDERFULLCONTENT
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
else:
    PRINT_FLAG = PW_CLIENTONLY
    ctypes.windll.user32.SetProcessDPIAware()
ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000040)  # Prevent Windows going to sleep mode


class AndroidEmulator(object):
    """Class for working with Android emulators."""

    def __init__(self, name, child_name, key_handle_name):
        """Class initialization.

        :param str name: main window's name of the emulator.
        :param str child_name: child window's name of inner control window.
        :param str key_handle_name: name of windows's key handler.
        """
        self._init_variables()
        self._version = None
        self.name = name
        self.child_name = child_name
        self.key_handle_name = key_handle_name
        self.screen_locked = False
        self.last_frame = None
        self.update_handlers()
        self._set_params_by_version()
        if self.initialized:
            logging.debug(f"Initialized {self.__class__.__name__} object with name {self.name} "
                          f"version {self.get_version()} "
                          f"and resolution {self.width, self.height}; "
                          f"main window: {self.x1, self.y1, self.x2, self.y2}, parent: {self.parent_x, self.parent_y}")

    def _init_variables(self):
        """Variables initialization."""
        self.parent_x, self.parent_y, self.parent_width, self.parent_height, \
        self.parent_hwnd, self.parent_thread, self.main_key_handle = (None,) * 7
        self.x, self.y, self.width, self.height, self.hwnd, self.key_handle = (None,) * 6
        # Storing external functions for process manager context (video_capture decorators)
        self.autoit_control_click_by_handle = autoit.control_click_by_handle
        self.win32_api_post_message = win32api.PostMessage

    def get_process_exe(self):
        """Gets path of emulator's executable file.

        :rtype: str
        """
        try:
            p_hwnd, process_id = win32process.GetWindowThreadProcessId(self.parent_hwnd)
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, process_id)
            process_exe = win32process.GetModuleFileNameEx(process, 0)
            return process_exe
        except pywintypes.error:
            return None

    def get_version(self):
        """Get emulator's version from properties of .exe file.

        :rtype: LooseVersion
        """
        if self._version:
            return self._version
        process_exe = self.get_process_exe()
        if process_exe:
            self._version = LooseVersion(get_file_properties(process_exe).get("FileVersion"))
        return self._version

    def _set_params_by_version(self):
        """Sets params for different versions of emulator.
        Can be overridden in child classes."""
        pass

    def update_handlers(self):
        """Updates window's handlers and stores info from them."""
        win32gui.EnumWindows(self._get_window_info, None)
        win32gui.EnumChildWindows(self.parent_hwnd, self._get_key_layout_handle, None)
        win32gui.EnumChildWindows(self.parent_hwnd, self._get_emulator_window_info, None)

    def update_window_rectangles(self):
        """Updates window's rectangles."""
        self._update_rect_from_parent_hwnd()
        self._update_rect_from_main_hwnd()

    def _update_rect_from_parent_hwnd(self):
        """Finds parent's window rectangle and stores it's coordinates."""
        if not self.parent_hwnd:
            return
        try:
            rect = win32gui.GetWindowRect(self.parent_hwnd)
            self.parent_x = rect[0]
            self.parent_y = rect[1]
            self.parent_width = rect[2] - rect[0]
            self.parent_height = rect[3] - rect[1]
        except pywintypes.error:
            pass

    def _update_rect_from_main_hwnd(self):
        """Finds emulator's window rectangle and stores it's coordinates."""
        if not self.hwnd:
            return
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            self.x = rect[0]
            self.y = rect[1]
            self.width = rect[2] - rect[0]
            self.height = rect[3] - rect[1]
            self.x1 = self.x - self.parent_x
            self.y1 = self.y - self.parent_y
            self.x2 = self.width + self.x1
            self.y2 = self.height + self.y1
        except pywintypes.error:
            pass

    def _get_window_info(self, hwnd, wildcard):
        """Gets information about main emulator's window. Stores window handler and main key handler.
        Main window usually renders graphics.

        :param int hwnd: window handle.
        :param str wildcard: wildcard.
        """
        if self.name == win32gui.GetWindowText(hwnd):
            try:
                self.parent_hwnd = hwnd
                self.parent_thread = win32process.GetWindowThreadProcessId(self.parent_hwnd)
                self.main_key_handle = win32gui.GetDlgItem(self.parent_hwnd, 0)
                self._update_rect_from_parent_hwnd()
            except pywintypes.error:
                pass

    def _get_emulator_window_info(self, hwnd, wildcard):
        """Gets information about child emulator's window.
        Child window usually receives mouse events (clicks, drags).

        :param int hwnd: window handle.
        :param str wildcard: wildcard.
        """
        if self.child_name in win32gui.GetWindowText(hwnd):
            self.hwnd = hwnd
            self._update_rect_from_main_hwnd()

    def _get_key_layout_handle(self, hwnd, wildcard):
        """Gets information about general key handler.
        Should be implemented in child classes.

        :param int hwnd: window handle.
        :param str wildcard: wildcard.
        """
        raise NotImplementedError

    @property
    def initialized(self):
        """Property that checks whether emulator has active handlers.

        :return: was emulator initialized properly or not.
        :rtype: bool
        """
        hwnd_found = self.hwnd is not None and self.parent_hwnd is not None
        hwnd_active = win32gui.GetWindowText(self.parent_hwnd) == self.name and win32gui.GetWindowText(
            self.hwnd) == self.child_name
        keys_found = self.key_handle is not None and self.main_key_handle is not None
        rect_found = self.x is not None and self.y is not None
        parent_found = self.parent_x is not None and self.parent_y is not None
        return hwnd_found and hwnd_active and keys_found and rect_found and parent_found

    @property
    def is_minimized(self):
        """Property that check whether emulator's main window minimized or not."""
        return win32gui.IsIconic(self.parent_hwnd)

    def maximize(self):
        """Maximizes emulator's main window."""
        win32api.PostMessage(self.parent_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)

    def get_screen_image(self, rect=(0, 0, 1, 1)):
        """Gets image of emulator's screen.

        :param tuple[float, float, float, float] | lib.game.ui.Rect rect: rectangle of screen to capture.

        :rtype: numpy.ndarray
        """
        box = (rect[0] * self.width, rect[1] * self.height,
               rect[2] * self.width, rect[3] * self.height)
        screen = self._get_screen().crop(box)
        return array(screen)

    @staticmethod
    def get_image_from_image(image, rect):
        """Gets image from another image. Basically just crops it.

        :param numpy.ndarray image: image.
        :param tuple[float, float, flaot, float] | lib.game.ui.Rect rect: rectangle to crop.

        :rtype: numpy.ndarray
        """
        image = Image.fromarray(image)
        box = (rect[0] * image.width, rect[1] * image.height,
               rect[2] * image.width, rect[3] * image.height)
        screen = image.crop(box)
        return array(screen)

    def get_screen_color(self, positions, screen=None):
        """Gets color from emulator's screen by it position.

        :param list[tuple[int, int]] positions: list of (x,y) color positions.
        :param numpy.ndarray screen: screen image.

        :return: list of (r,g,b) colors.
        :rtype: list[tuple[int, int, int]]
        """
        screen = screen if screen is not None else self._get_screen()
        return [screen.getpixel(position) for position in positions]

    def get_position_inside_screen_rectangle(self, rect, offset=0.1):
        """Gets (x,y) position inside screen rectangle with padding offset.

        :param tuple[float, float, float, float] | lib.game.ui.Rect rect: local rectangle inside (0, 0, 1, 1) range.
        :param float offset: padding offset inside rectangle.

        :return: (x, y) position inside screen rectangle.
        :rtype: tuple[int, int]
        """
        x1, x2, dx = rect[0], rect[2], rect[2] - rect[0]
        y1, y2, dy = rect[1], rect[3], rect[3] - rect[1]
        if x1 == x2 and y1 == y2:
            return int(x1 * self.width), int(y1 * self.height)
        x1, x2 = x1 + dx * offset, x2 - dx * offset
        y1, y2 = y1 + dy * offset, y2 - dy * offset
        x, y = random.uniform(x1, x2), random.uniform(y1, y2)
        return int(x * self.width), int(y * self.height)

    def get_screen_text(self, ui_element, screen=None):
        """Gets text from emulator's screen.

        :param lib.game.ui.UIElement ui_element: UI element that has all info for text recognition.
        :param numpy.ndarray screen: screen image.

        :return: text from the image.
        :rtype: str
        """
        image = self.get_screen_image(ui_element.text_rect) if screen is None else screen
        if ui_element.color_to_convert:
            image = convert_colors_in_image(image=image, colors=ui_element.color_to_convert)
        return get_text_from_image(image=image, threshold=ui_element.text_threshold,
                                   chars=ui_element.available_characters,
                                   max_height=ui_element.tesseract_resize_height,
                                   save_file=ui_element.name)

    def is_image_on_screen(self, ui_element, screen=None):
        """Checks if image is on screen.

        :param lib.game.ui.UIElement ui_element: UI element hat has all info for image recognition.
        :param numpy.ndarray screen: screen image.

        :rtype: bool
        """
        image = self.get_screen_image(ui_element.image_rect) if screen is None else screen
        return is_images_similar(image1=image, image2=ui_element.image,
                                 overlap=ui_element.image_threshold, save_file=ui_element.name)

    def is_ui_element_on_screen(self, ui_element, screen=None):
        """Checks if UI element is on screen.

        :param lib.game.ui.UIElement ui_element: UI element hat has all info for text recognition.
        :param numpy.ndarray screen: screen image.

        :rtype: bool
        """
        text_on_screen = self.get_screen_text(ui_element, screen)
        return is_strings_similar(ui_element.text, text_on_screen)

    def is_color_similar(self, color, rects, screen=None):
        """Checks if color on screen is similar to given color.

        :param tuple[int, int, int] color: color to check.
        :param list[tuple[float, float, float, float]] | list[lib.game.ui.Rect] rects: color position rectangles.
        :param numpy.ndarray screen: screen image.

        :rtype: bool
        """
        positions = [self.get_position_inside_screen_rectangle(rect) for rect in rects]
        screen_colors = self.get_screen_color(positions=positions, screen=screen)
        similar = False
        for screen_color in screen_colors:
            similar = similar or True if is_color_similar(color, screen_color) else similar or False
        return similar

    def click_button(self, ui_element, min_duration=0.1, max_duration=0.25):
        """Clicks inside button rectangle by it's UI element.

        :param lib.game.ui.UIElement ui_element: UI element.
        :param float min_duration: minimum duration between clicking.
        :param float max_duration: maximum duration between clicking.
        """
        duration = random.uniform(min_duration, max_duration)
        r_sleep(duration)
        x, y = self.get_position_inside_screen_rectangle(ui_element.button_rect.global_rect)
        self.autoit_control_click_by_handle(self.parent_hwnd, self.hwnd, x=x, y=y)
        r_sleep(duration * 2)

    def press_key(self, key, system_key=False):
        """Presses key (keys should be configured inside emulator).

        :param str key: key name.
        :param bool system_key: is emulator's system (main) key or not.
        """
        handle = self.key_handle if not system_key else self.main_key_handle
        autoit.control_send_by_handle(self.main_key_handle, handle, key)

    def close_current_app(self):
        """Closes current opened app in emulator. Should be implemented in child classes."""
        raise NotImplementedError

    @property
    def restartable(self):
        """Checks if app can be restarted. Should be implemented in child classes."""
        raise NotImplementedError

    def drag(self, from_ui, to_ui, duration=0.7, steps_count=100):
        """Drags from one UI element to another.

        :param lib.game.ui.UIElement from_ui: UI element of dragging position "From".
        :param lib.game.ui.UIElement to_ui: UI element of dragging position "To".
        :param float duration: duration of dragging.
        :param int steps_count: steps of dragging.
        """

        def linear_point(x1, y1, x2, y2, n):
            p_x = ((x2 - x1) * n) + x1
            p_y = ((y2 - y1) * n) + y1
            return int(p_x), int(p_y)

        from_position = self.get_position_inside_screen_rectangle(from_ui.button_rect.global_rect)
        to_position = self.get_position_inside_screen_rectangle(to_ui.button_rect.global_rect)
        self.win32_api_post_message(self.hwnd, win32con.WM_MOUSEMOVE, 0, win32api.MAKELONG(*from_position))
        self.win32_api_post_message(self.hwnd, win32con.WM_LBUTTONDOWN, 0, win32api.MAKELONG(*from_position))

        sleep_amount = duration / steps_count
        steps = [linear_point(*from_position, *to_position, n / steps_count) for n in range(steps_count)]
        for x, y in steps:
            self.win32_api_post_message(self.hwnd, win32con.WM_MOUSEMOVE, win32con.WM_LBUTTONDOWN,
                                        win32api.MAKELONG(x, y))
            time.sleep(sleep_amount)
        self.win32_api_post_message(self.hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(*to_position))

    def _get_screen(self):
        """Get screen image from emulator's main window.

        :return: image from emulator in BGR format.
        :rtype: PIL.Image.Image
        """
        if not self.initialized:
            return None
        if self.is_minimized:
            self.maximize()
        self.update_window_rectangles()
        while self.screen_locked:
            if self.last_frame:
                return self.last_frame
            time.sleep(0.1)
        self.screen_locked = True

        hwnd_dc = win32gui.GetWindowDC(self.parent_hwnd)
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()

        bit_map = win32ui.CreateBitmap()
        bit_map.CreateCompatibleBitmap(mfc_dc, self.parent_width, self.parent_height)

        save_dc.SelectObject(bit_map)
        windll.user32.PrintWindow(self.parent_hwnd, save_dc.GetSafeHdc(), PW_RENDERFULLCONTENT)

        bmp_info = bit_map.GetInfo()
        bmp_arr = bit_map.GetBitmapBits(True)

        win32gui.DeleteObject(bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        win32gui.ReleaseDC(self.parent_hwnd, hwnd_dc)

        self.screen_locked = False
        parent_img = Image.frombuffer('RGB', (bmp_info['bmWidth'], bmp_info['bmHeight']), bmp_arr, 'raw', 'BGRX', 0, 1)
        img = parent_img.crop((self.x1, self.y1, self.x2, self.y2))
        self.last_frame = img
        return img
