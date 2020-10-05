import autoit
import logging
import os
import win32gui
import win32process
from xml.etree import ElementTree
from configparser import ConfigParser
from lib.players.android_emulator import AndroidEmulator

NOX_EXE = "Nox.exe"
GRAPHIC_ENGINE_TYPE_DIRECTX = 1
DEFAULT_NOX_ID = "Nox_0"
OLD_VERSION_INDEX = 8


class NoxWindow(AndroidEmulator):
    """Class for working with NoxPlayer emulator."""

    def __init__(self, name="NoxPlayer", child_name="ScreenBoardClassWindow", key_handle_name="Form"):
        """Class initialization.

        :param name: main window's name of the player.
        :param child_name: child window's name of inner control window.
        :param key_handle_name: name of windows's key handler.
        """
        super().__init__(name=name, child_name=child_name, key_handle_name=key_handle_name)
        self.close_app_shortcut = self._get_keyboard_shortcut_for_closing_app() if self.initialized else None

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

    def update_windows(self):
        """Update window's handlers."""
        was_closed = not self.initialized
        super(NoxWindow, self).update_windows()
        if was_closed and self.initialized:
            self.close_app_shortcut = self._get_keyboard_shortcut_for_closing_app()

    @staticmethod
    def _read_config_file(config_file="conf.ini"):
        """Read NoxPlayer's config file."""
        path = os.path.join(os.getenv('APPDATA'), "..", "Local", "Nox", config_file)
        try:
            config = ConfigParser()
            config.read(path)
            return config
        except FileNotFoundError:
            logging.warning(f"Can't find NoxPlayer's settings in %APPDATA% folder by path: {path}. "
                            f"Try to reinstall NoxPlayer.")

    @staticmethod
    def _save_config_file(config, config_file="conf.ini"):
        """Save NoxPlayer's config file."""
        path = os.path.join(os.getenv('APPDATA'), "..", "Local", "Nox", config_file)
        with open(path, 'w', encoding="utf-8") as file:
            config.write(file)

    def _get_virtual_machine_id(self):
        """Get NoxPlayer's Virtual Machine ID of current process."""
        path = os.path.join(os.getenv('APPDATA'), "..", "Local", "MultiPlayerManager", "multiplayer.xml")
        try:
            for event, elem in ElementTree.iterparse(path):
                if elem.attrib.get("name") == self.name:
                    return elem.attrib['id']
        except FileNotFoundError:
            logging.warning(f"Can't find NoxPlayer's multiplayer settings in %APPDATA% folder by path: {path}.")
            return None

    def get_config_file(self):
        """Get config file related to current emulator's process."""
        vm_id = self._get_virtual_machine_id()
        config_file = "conf.ini" if vm_id in [DEFAULT_NOX_ID, None] else f"clone_{vm_id}_conf.ini"
        return self._read_config_file(config_file=config_file), config_file

    def set_config_for_bot(self):
        """Set necessary configs to NoxPlayer.
        Graphic engine should be set to DirectX,
        restart shortcut should be set as hotkey (index within 1-10 range)."""
        config, config_file = self.get_config_file()
        if not config or not config.has_section("toolbar_setting") or not config.has_section("setting"):
            return
        config["toolbar_setting"].clear()
        config["toolbar_setting"] = {"toolbar_close_all_index": f"{OLD_VERSION_INDEX}"}
        config["setting"]["graphic_engine_type"] = f"{GRAPHIC_ENGINE_TYPE_DIRECTX}"
        self._save_config_file(config=config, config_file=config_file)
        logging.info(f"{self.name}: saved config file {config_file}. Need to restart emulator to apply changes.")

    def _get_keyboard_shortcut_for_closing_app(self):
        """Get keyboard shortcut for closing all apps from config file."""
        name = f"{self.name} {self.get_version()}"
        config, _ = self.get_config_file()
        if not config or not config.has_section("toolbar_setting"):
            return
        close_all_shortcut = config["toolbar_setting"].get("toolbar_close_all_index")
        if close_all_shortcut:
            logging.debug(f"{name}: found `Close App` shortcut at position {close_all_shortcut}")
            if int(close_all_shortcut) <= 10:
                return int(close_all_shortcut) - 1
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
