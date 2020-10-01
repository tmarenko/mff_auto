import autoit
import logging
import os
import win32gui
import win32process
from lib.players.android_emulator import AndroidEmulator

NOX_EXE = "Nox.exe"


class NoxWindow(AndroidEmulator):
    """Class for working with NoxPlayer emulator."""

    def __init__(self, name="NoxPlayer", child_name="ScreenBoardClassWindow", key_handle_name="Form"):
        """Class initialization.

        :param name: main window's name of the player.
        :param child_name: child window's name of inner control window.
        :param key_handle_name: name of windows's key handler.
        """
        super().__init__(name=name, child_name=child_name, key_handle_name=key_handle_name)
        self.close_app_shortcut = self._get_keyboard_shortcut_for_closing_app()

    def _get_key_layout_handle(self, hwnd, wildcard):
        """Get window's key handler.

        :param hwnd: window handle.
        :param wildcard: wildcard.
        """
        if self.parent_thread and self.key_handle_name in win32gui.GetWindowText(hwnd):
            # Checking if handler is child of main window.
            if win32process.GetWindowThreadProcessId(hwnd)[0] == self.parent_thread[0]:
                self.key_handle = hwnd

    def close_current_app(self):
        """Close current opened app in player."""
        autoit.control_send_by_handle(self.player_key_handle, self.player_key_handle, f"^{self.close_app_shortcut}")

    @staticmethod
    def _read_config_file():
        """Read NoxPlayer's config file."""
        path = os.path.join(os.getenv('APPDATA'), "..", "Local", "Nox", "conf.ini")
        try:
            with open(path, "r", encoding="utf-8") as file:
                return file.readlines()
        except FileNotFoundError:
            logging.warning(f"Can't find NoxPlayer's settings in %APPDATA% folder by path: {path}. "
                            f"Try to reinstall NoxPlayer.")

    def _get_keyboard_shortcut_for_closing_app(self):
        """Get keyboard shortcut for closing all apps from config file."""
        name = f"{self.name} {self.get_version()}"
        config_file = self._read_config_file()
        if not config_file:
            return
        close_all_shortcut = [line.strip() for line in config_file if "toolbar_close_all_index" in line]
        if close_all_shortcut:
            shortcut_name, shortcut_position = close_all_shortcut[0].split("=")
            logging.debug(f"{name}: found `Close App` shortcut at position {shortcut_position}")
            if int(shortcut_position) <= 10:
                return int(shortcut_position) - 1
            else:
                logging.warning(f"{name}: shortcut position is greater than {10}, can't be casted via keyboard. "
                                f"Try to open NoxPlayer settings -> `Interface settings` and then change position "
                                f"of `Close all apps` toolbar and then restart the bot.")
                return
        logging.warning(f"{name}: can't find config `toolbar_close_all_index` in NoxPlayer's config file.")
        return

    @property
    def restartable(self):
        """Returns if app can be restarted."""
        return self.close_app_shortcut is not None
