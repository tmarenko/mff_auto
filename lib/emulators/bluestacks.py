import win32api, win32con
import time
import logging
from lib.emulators.android_emulator import AndroidEmulator
from distutils.version import LooseVersion

BLUESTACKS_4_EXE = "Bluestacks.exe"
BLUESTACKS_5_CHILD_NAME = "plrNativeInputWindow"
BLUESTACKS_5_EXE = "HD-Player.exe"


class BlueStacks(AndroidEmulator):
    """Class for working with BlueStacks emulator."""

    def __init__(self, name="BlueStacks", child_name="BlueStacks Android PluginAndroid", key_handle_name="BlueStacks"):
        """Class initialization.

        :param name: main window's name of the emulator.
        :param child_name: child window's name of inner control window.
        :param key_handle_name: name of windows's key handler.
        """
        super().__init__(name=name, child_name=child_name, key_handle_name=key_handle_name)

    def _set_params_by_version(self):
        """Set params for BlueStacks by its version."""
        version = self.get_version()
        if version and version >= LooseVersion('5.0'):
            self.child_name = BLUESTACKS_5_CHILD_NAME
        self.update_windows()

    def _get_key_layout_handle(self, hwnd, wildcard):
        """Get window's key handler.

        :param hwnd: window handle.
        :param wildcard: wildcard.
        """
        if self.parent_hwnd:
            self.key_handle = self.parent_hwnd

    def close_current_app(self):
        """Close current opened app in emulator."""
        raise NotImplementedError("BlueStacks doesn't support closing apps through shortcuts.")

    @property
    def restartable(self):
        """Returns if app can be restarted."""
        logging.warning(f"{self.name} {self.get_version()}: doesn't support closing apps through shortcuts.")
        return False

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
            self.win32_api_post_message(self.hwnd, win32con.WM_LBUTTONDOWN, 0, win32api.MAKELONG(x, y))
            self.win32_api_post_message(self.hwnd, win32con.WM_MOUSEMOVE, win32con.WM_LBUTTONDOWN,
                                        win32api.MAKELONG(x, y))
            time.sleep(sleep_amount)
        self.win32_api_post_message(self.hwnd, win32con.WM_LBUTTONUP, 0, win32api.MAKELONG(*to_position))
