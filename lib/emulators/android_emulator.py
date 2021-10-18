import ctypes
import lib.logger as logging
import os
import random
import subprocess
import time
from ctypes import windll
from distutils.version import LooseVersion
from platform import release

import cv2
import win32api
import win32con
import win32gui
import win32process
import win32ui
from numpy import frombuffer
from ppadb.client import Client

from lib.functions import get_text_from_image, is_strings_similar, is_images_similar, is_color_similar, r_sleep, \
    get_file_properties, convert_colors_in_image, crop_image_array, wait_until

logger = logging.get_logger(__name__)

PW_CLIENTONLY = 1  # Only the client area of the window is copied to hdcBlt. By default, the entire window is copied.
PW_RENDERFULLCONTENT = 2  # Properly capture DirectComposition window contents. Available from Windows 8.1
MARVEL_FUTURE_FIGHT_APK = 'com.netmarble.mherosgb'

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

    hwnd, parent_hwnd = None, None
    x, y = None, None
    parent_x, parent_y = None, None
    parent_width, parent_height = None, None
    width, height = None, None
    adb = None
    mff_device = None
    adb_width, adb_height = None, None
    last_frame = None
    screen_locked = False
    _version = None

    def __init__(self, name, child_name, adb_path):
        """Class initialization.

        :param str name: main window's name of the emulator.
        :param str child_name: child window's name of inner control window.
        """
        self.adb_path = adb_path
        self.name = name
        self.child_name = child_name
        self.update_handlers()
        self._set_params_by_version()
        if self.initialized:
            logger.debug(f"Initialized {self.__class__.__name__} object with name {self.name} "
                          f"version {self.get_version()} "
                          f"and resolution {self.width, self.height}; "
                          f"main window: {self.x1, self.y1, self.x2, self.y2}, parent: {self.parent_x, self.parent_y};")

    def start_android_debug_bridge(self, adb_path):
        self.adb = AndroidDebugBridge()
        self.adb.start_server(adb_path=adb_path)

    def init_adb_device(self, serial):
        self.start_android_debug_bridge(adb_path=self.adb_path)
        if serial:
            self.mff_device = self.adb.get_device_by_serial(serial=serial)
        else:
            self.mff_device = self.adb.get_device_with_mff_installed()
        self.adb_width, self.adb_height = self.mff_device.wm_size().width, self.mff_device.wm_size().height
        logger.info(f"Initialized Android Debug Bridge serial {self.mff_device.serial}")

    def get_process_exe(self):
        """Gets path of emulator's executable file.

        :rtype: str
        """
        try:
            p_hwnd, process_id = win32process.GetWindowThreadProcessId(self.parent_hwnd)
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, process_id)
            process_exe = win32process.GetModuleFileNameEx(process, 0)
            return process_exe
        except BaseException:
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
        except BaseException:
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
        except BaseException:
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
                self._update_rect_from_parent_hwnd()
            except BaseException:
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

    @property
    def initialized(self):
        """Property that checks whether emulator has active handlers.

        :return: was emulator initialized properly or not.
        :rtype: bool
        """
        hwnd_found = self.hwnd is not None and self.parent_hwnd is not None
        hwnd_active = win32gui.GetWindowText(self.parent_hwnd) == self.name and win32gui.GetWindowText(
            self.hwnd) == self.child_name
        rect_found = self.x is not None and self.y is not None
        parent_found = self.parent_x is not None and self.parent_y is not None
        return hwnd_found and hwnd_active and rect_found and parent_found

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
        box = (int(rect[0] * self.width), int(rect[1] * self.height),
               int(rect[2] * self.width), int(rect[3] * self.height))
        return crop_image_array(self.get_screen_directx(), box)

    @staticmethod
    def get_image_from_image(image, rect):
        """Gets image from another image. Basically just crops it.

        :param numpy.ndarray image: image.
        :param tuple[float, float, flaot, float] | lib.game.ui.Rect rect: rectangle to crop.

        :rtype: numpy.ndarray
        """
        height, width, channel = image.shape
        box = (rect[0] * width, rect[1] * height,
               rect[2] * width, rect[3] * height)
        return crop_image_array(image, box)

    def get_screen_color(self, positions, screen=None):
        """Gets color from emulator's screen by it position.

        :param list[tuple[int, int]] positions: list of (x,y) color positions.
        :param numpy.ndarray screen: screen image.

        :return: list of (r,g,b) colors.
        :rtype: list[tuple[int, int, int]]
        """
        screen = screen if screen is not None else self.get_screen_directx()
        positions = [(position[1], position[0]) for position in positions]  # cv2 image's shape is (height, width)
        return [screen[position] for position in positions]

    def get_position_inside_screen_rectangle(self, rect, global_coordinates=True):
        """Gets (x,y) position inside screen rectangle.

        :param tuple[float, float, float, float] | lib.game.ui.Rect rect: local rectangle inside (0, 0, 1, 1) range.

        :return: (x, y) position inside screen rectangle.
        :rtype: tuple[int, int]
        """
        width, height = (self.adb_width, self.adb_height) if global_coordinates else (self.width, self.height)
        if rect[0] == rect[2] and rect[1] == rect[3]:
            return int(rect[0] * width), int(rect[1] * height)
        x, y = random.uniform(rect[0], rect[2]), random.uniform(rect[1], rect[3])
        return int(x * width), int(y * height)

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
        positions = [self.get_position_inside_screen_rectangle(rect, global_coordinates=False) for rect in rects]
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
        self.mff_device.input_tap(x, y)
        r_sleep(duration * 2)

    def close_marvel_future_fight(self):
        """Closes current opened app in emulator. Should be implemented in child classes."""
        return self.adb.stop_marvel_future_fight(self.mff_device)

    def start_marvel_future_fight(self):
        return self.adb.start_marvel_future_fight(self.mff_device)

    @property
    def restartable(self):
        """Checks if app can be restarted. Should be implemented in child classes."""
        return self.adb and self.adb.client

    def swipe(self, from_ui, to_ui, duration=1):
        """Swipes from one UI element to another.

        :param lib.game.ui.UIElement from_ui: UI element of dragging position "From".
        :param lib.game.ui.UIElement to_ui: UI element of dragging position "To".
        :param float duration: duration of swiping in seconds.
        """
        from_position = self.get_position_inside_screen_rectangle(from_ui.button_rect.global_rect)
        to_position = self.get_position_inside_screen_rectangle(to_ui.button_rect.global_rect)
        self.mff_device.input_swipe(*from_position, *to_position, int(duration * 1000))

    def get_screen_directx(self):
        """Get screen image from emulator's main window.

        :return: image from emulator in BGR format.
        :rtype: numpy.ndarray
        """
        if not self.initialized:
            return None
        if self.is_minimized:
            self.maximize()
        self.update_window_rectangles()
        while self.screen_locked:
            if self.last_frame is not None:
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
        image = frombuffer(bmp_arr, dtype='uint8').reshape((bmp_info['bmHeight'], bmp_info['bmWidth'],
                                                            int(bmp_info['bmWidthBytes'] / bmp_info['bmWidth'])))
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)
        image = crop_image_array(image, (self.x1, self.y1, self.x2, self.y2))
        self.last_frame = image
        return image


class AndroidDebugBridge:

    client = None

    def start_server(self, adb_path):
        logger.debug(f"Restarting ADB server by path: {adb_path}")
        call = subprocess.run([adb_path, "kill-server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logger.info(call.stdout)
        call = subprocess.run([adb_path, "start-server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logger.info(call.stdout)
        self.client = Client()

    def get_device_by_serial(self, serial):
        """

        :param serial:
        :return:
        :rtype: ppadb.device.Device
        """
        self.client._execute_cmd(cmd=f"host:connect:{serial}")
        return self.client.device(serial)

    def get_device_with_mff_installed(self):
        devices = self.client.devices()
        logger.debug(f"Found devices over ADB: {[device.serial for device in devices]}")
        for device in devices:
            try:
                list_packages = device.list_packages()
                logger.debug(f"Packages on device {device.serial}: {list_packages}")
                if MARVEL_FUTURE_FIGHT_APK in list_packages:
                    return device
            except RuntimeError as err:
                logger.error(f"Error on device {device.serial}: {err}")

    @staticmethod
    def is_mff_running(device):
        top_activity = device.get_top_activity()
        if top_activity:
            return MARVEL_FUTURE_FIGHT_APK in top_activity.package

    def start_marvel_future_fight(self, device):
        if self.is_mff_running(device):
            logger.warning(f"Trying to start `{MARVEL_FUTURE_FIGHT_APK}` but it's already started.")
        logger.info(f"Starting `{MARVEL_FUTURE_FIGHT_APK}` at device {device.serial}")
        device.shell(f"am start {MARVEL_FUTURE_FIGHT_APK}/.SRNativeActivity")
        if wait_until(self.is_mff_running, device=device):
            return True
        logger.error(f"`{MARVEL_FUTURE_FIGHT_APK}` haven't started.")

    def stop_marvel_future_fight(self, device):
        if not self.is_mff_running(device):
            logger.warning(f"Trying to stop `{MARVEL_FUTURE_FIGHT_APK}` but it's already stopped.")
        logger.info(f"Stopping `{MARVEL_FUTURE_FIGHT_APK}` at device {device.serial}")
        device.shell(f"am force-stop {MARVEL_FUTURE_FIGHT_APK}")
        if wait_until(self.is_mff_running, device=device, condition=False):
            return True
        logger.error(f"`{MARVEL_FUTURE_FIGHT_APK}` haven't stopped.")
