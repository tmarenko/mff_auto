import autoit
import ctypes
import logging
import win32gui, win32ui, win32process, win32api, win32con
import random
import time
import pywintypes
from platform import release
from PIL import Image
from ctypes import windll
from numpy import array
from lib.functions import get_text_from_image, is_strings_similar, get_position_inside_rectangle, is_images_similar,\
    is_color_similar, r_sleep, get_file_properties

# Set process as high-DPI aware to get actual window's coordinates
if release() == "10":
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
else:
    ctypes.windll.user32.SetProcessDPIAware()
ctypes.windll.kernel32.SetThreadExecutionState(0x80000000 | 0x00000040)  # Prevent Windows going to sleep mode


class AndroidEmulator(object):
    """Class for working with Android emulator's window."""

    def __init__(self, name, child_name, key_handle_name):
        """Class initialization.

        :param name: main window's name of the player.
        :param child_name: child window's name of inner control window.
        :param key_handle_name: name of windows's key handler.
        """
        self._init_variables()
        self._version = None
        self.name = name
        self.child_name = child_name
        self.key_handle_name = key_handle_name
        self.screen_locked = False
        self.last_frame = None
        self.update_windows()
        if self.initialized:
            logging.debug(f"Initialized {self.__class__.__name__} object with name {self.name} "
                          f"version {self.get_version()} "
                          f"and resolution {self.width, self.height}; "
                          f"main window: {self.x1, self.y1, self.x2, self.y2}, parent: {self.parent_x, self.parent_y}")

    def _init_variables(self):
        """Variables initialization."""
        self.parent_x, self.parent_y, self.parent_width, self.parent_height, \
            self.parent_hwnd, self.parent_thread, self.player_key_handle = (None,) * 7
        self.x, self.y, self.width, self.height, self.hwnd, self.key_handle = (None,) * 6
        # Storing external functions for process manager context (video_capture decorators)
        self.autoit_control_click_by_handle = autoit.control_click_by_handle
        self.win32_api_post_message = win32api.PostMessage

    def get_process(self):
        """Get path to process of emulator's executable."""
        try:
            p_hwnd, process_id = win32process.GetWindowThreadProcessId(self.parent_hwnd)
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, process_id)
            process_exe = win32process.GetModuleFileNameEx(process, 0)
            return process_exe
        except pywintypes.error:
            return None

    def get_version(self):
        """Get emulator's version from properties of .exe file."""
        if self._version:
            return self._version
        process_exe = self.get_process()
        if process_exe:
            self._version = get_file_properties(process_exe).get("FileVersion")
        return self._version

    def update_windows(self):
        """Update window's handlers."""
        win32gui.EnumWindows(self._get_window_info, None)
        win32gui.EnumChildWindows(self.parent_hwnd, self._get_key_layout_handle, None)
        win32gui.EnumChildWindows(self.parent_hwnd, self._get_player_window_info, None)

    def update_windows_rect(self):
        """Update window's rectangles."""
        self._update_rect_from_parent_hwnd()
        self._update_rect_from_player_hwnd()

    def _update_rect_from_parent_hwnd(self):
        """Update parent's window rectangle."""
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

    def _update_rect_from_player_hwnd(self):
        """Update player's window rectangle."""
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
        """Get main window info.

        :param hwnd: window handle.
        :param wildcard: wildcard.
        """
        if self.name == win32gui.GetWindowText(hwnd):
            try:
                self.parent_hwnd = hwnd
                self.parent_thread = win32process.GetWindowThreadProcessId(self.parent_hwnd)
                self.player_key_handle = win32gui.GetDlgItem(self.parent_hwnd, 0)
                self._update_rect_from_parent_hwnd()
            except pywintypes.error:
                pass

    def _get_player_window_info(self, hwnd, wildcard):
        """Get child window info.

        :param hwnd: window handle.
        :param wildcard: wildcard.
        """
        if self.child_name in win32gui.GetWindowText(hwnd):
            self.hwnd = hwnd
            self._update_rect_from_player_hwnd()

    def _get_key_layout_handle(self, hwnd, wildcard):
        """Get window's key handler.

        :param hwnd: window handle.
        :param wildcard: wildcard.
        """
        raise NotImplementedError

    @property
    def initialized(self):
        """Was player initialized properly.

        :return: True or False.
        """
        hwnd_found = self.hwnd is not None and self.parent_hwnd is not None
        hwnd_active = win32gui.GetWindowText(self.parent_hwnd) == self.name and win32gui.GetWindowText(self.hwnd) == self.child_name
        keys_found = self.key_handle is not None and self.player_key_handle is not None
        rect_found = self.x is not None and self.y is not None
        parent_found = self.parent_x is not None and self.parent_y is not None
        # TODO: keys are not necessary, maybe remove them?
        keys_found = True
        return hwnd_found and hwnd_active and keys_found and rect_found and parent_found

    @property
    def is_minimized(self):
        """Is player's window minimized."""
        return win32gui.IsIconic(self.parent_hwnd)

    def maximize(self):
        """Maximize player's window."""
        win32api.PostMessage(self.parent_hwnd, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)

    def get_screen_image(self, rect=(0, 0, 1, 1)):
        """Get screen image.

        :param rect: rectangle of screen.

        :return: numpy.array of image.
        """
        box = (rect[0] * self.width, rect[1] * self.height,
               rect[2] * self.width, rect[3] * self.height)
        screen = self._get_screen().crop(box)
        return array(screen)

    @staticmethod
    def get_image_from_image(image, ui_element):
        """Get screen image from another image.

        :param image: numpy.array of image.
        :param ui.UIElement ui_element: UI element.

        :return: numpy.array of image.
        """
        image = Image.fromarray(image)
        box = (ui_element.rect[0] * image.width, ui_element.rect[1] * image.height,
               ui_element.rect[2] * image.width, ui_element.rect[3] * image.height)
        screen = image.crop(box)
        return array(screen)

    def get_screen_color(self, positions, screen=None):
        """Get color from screen.

        :param positions: list of color positions.
        :param screen: screen image.

        :return: RGB color.
        """
        screen = screen if screen is not None else self._get_screen()
        return [screen.getpixel(position) for position in positions]

    def get_position_inside_screen_rectangle(self, rect, mean_mod=2, sigma_mod=5):
        """Get (x,y) position inside screen rectangle.
         Using normal distribution position usually will be near rectangle center.

        :param rect: rectangle of screen.
        :param mean_mod: mean for distribution.
        :param sigma_mod: standard deviation for distribution.

        :return: (x, y) position inside screen rectangle.
        """
        if rect[0] == rect[2] and rect[1] == rect[3]:
            return int(rect[0] * self.width), int(rect[1] * self.height)
        x, y = get_position_inside_rectangle(rect=rect, mean_mod=mean_mod, sigma_mod=sigma_mod)
        return int(x * self.width), int(y * self.height)

    def get_screen_text(self, ui_element, screen=None):
        """Get text from screen.

        :param ui.UIElement ui_element: UI element.
        :param screen: screen image.

        :return: text from the image.
        """
        image = screen if screen is not None else self.get_screen_image(ui_element.rect)
        return get_text_from_image(image=image, threshold=ui_element.threshold, chars=ui_element.chars,
                                   save_file=ui_element.save_file, max_height=ui_element.max_height)

    def is_image_on_screen(self, ui_element, screen=None):
        """Check if image is on screen.

        :param ui.UIElement ui_element: UI element.
        :param screen: screen image.

        :return: True or False.
        """
        rect = ui_element.rect if ui_element.rect else ui_element.button
        screen_image = screen if screen is not None else self.get_screen_image(rect)
        return is_images_similar(screen_image, ui_element.image, ui_element.threshold, save_file=ui_element.save_file)

    def is_ui_element_on_screen(self, ui_element, screen=None):
        """Check if UI element is on screen.

        :param ui.UIElement ui_element: UI element.
        :param screen: screen image.

        :return: True or False.
        """
        text_on_screen = self.get_screen_text(ui_element, screen)
        return is_strings_similar(ui_element.text, text_on_screen)

    def is_color_similar(self, color, rects, screen=None):
        """Check if color in rects on screen is similar to given color.

        :param color: color to check.
        :param rects: color position rects.
        :param screen: screen image.

        :return: True or False.
        """
        positions = [self.get_position_inside_screen_rectangle(rect) for rect in rects]
        screen_colors = self.get_screen_color(positions=positions, screen=screen)
        similar = False
        for screen_color in screen_colors:
            similar = similar or True if is_color_similar(color, screen_color) else similar or False
        return similar

    def click_button(self, button_rect, min_duration=0.1, max_duration=0.25):
        """Click inside button rectangle.

        :param button_rect: rectangle of button.
        :param min_duration: minimum duration between clicking.
        :param max_duration: maximum duration between clicking.
        """
        duration = random.uniform(min_duration, max_duration)
        r_sleep(duration)
        x, y = self.get_position_inside_screen_rectangle(button_rect)
        self.autoit_control_click_by_handle(self.parent_hwnd, self.hwnd, x=x, y=y)
        r_sleep(duration * 2)

    def press_key(self, key, system_key=False):
        """Press key (keys should be configured inside player).

        :param key: key name.
        :param system_key: is player's system key or not.
        """
        handle = self.key_handle if not system_key else self.player_key_handle
        autoit.control_send_by_handle(self.player_key_handle, handle, key)

    def close_current_app(self):
        """Close current opened app in player."""
        raise NotImplementedError

    @property
    def restartable(self):
        """Returns if app can be restarted."""
        raise NotImplementedError

    def drag(self, from_rect, to_rect, duration=0.7, steps_count=100):
        """Click, hold and drag.

        :param from_rect: rectangle of dragging position "From".
        :param to_rect: rectangle of dragging position "To".
        :param duration: duration of dragging.
        :param steps_count: steps of dragging.
        """
        def linear_point(x1, y1, x2, y2, n):
            p_x = ((x2 - x1) * n) + x1
            p_y = ((y2 - y1) * n) + y1
            return int(p_x), int(p_y)

        from_position = self.get_position_inside_screen_rectangle(from_rect)
        to_position = self.get_position_inside_screen_rectangle(to_rect)
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
        """Get screen image from main window.

        :return: PIL.Image image from window in BGR format.
        """
        if not self.initialized:
            return None
        if self.is_minimized:
            self.maximize()
        self.update_windows_rect()
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
        windll.user32.PrintWindow(self.parent_hwnd, save_dc.GetSafeHdc(), 1)

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
