import os
from distutils.version import LooseVersion
import win32gui

from lib.emulators.android_emulator import AndroidEmulator

NOX_EXE = "Nox.exe"
NOX_7_0_1_1_CHILD_NAME = "sub"
NOX_ADB = "nox_adb.exe"


class NoxPlayer(AndroidEmulator):
    """Class for working with NoxPlayer emulator."""

    def __init__(self, name="NoxPlayer", child_name="ScreenBoardClassWindow"):
        """Class initialization.

        :param str name: main window's name of the emulator.
        :param str child_name: child window's name of inner control window.
        """
        super().__init__(name=name, child_name=child_name, adb_path=None)
        self.adb_path = os.path.join(os.path.dirname(self.get_process_exe()), NOX_ADB)

    def _set_params_by_version(self):
        """Sets params for NoxPlayer by its version."""
        version = self.get_version()
        if version and version >= LooseVersion('7.0.1.1'):
            self.child_name = NOX_7_0_1_1_CHILD_NAME
        self.update_handlers()

    def _get_emulator_window_info(self, hwnd, wildcard):
        """Gets information about child emulator's window.
        Child window usually receives mouse events (clicks, drags).

        :param int hwnd: window handle.
        :param str wildcard: wildcard.
        """
        if self.child_name in win32gui.GetWindowText(hwnd):
            self.hwnd = hwnd
            version = self.get_version()
            if version and version >= LooseVersion('7.0.1.1'):
                self.hwnd = win32gui.GetParent(hwnd)
            self._update_rect_from_main_hwnd()
