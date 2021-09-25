import autoit
import logging
import os
import win32gui
from xml.etree import ElementTree
from configparser import ConfigParser
from distutils.version import LooseVersion
from lib.emulators.android_emulator import AndroidEmulator

NOX_EXE = "Nox.exe"
GRAPHIC_ENGINE_TYPE_DIRECTX = 1
DEFAULT_NOX_ID = "Nox_0"
OLD_VERSION_INDEX = 8
NOX_6_KEY_HANDLE_NAME = "main_title_barWindow"
NOX_6_KEY_HANDLE_CLASS = "Qt5QWindowIcon"
NOX_7_KEY_HANDLE_NAME = "Form"
NOX_7_KEY_HANDLE_CLASS = "Qt5QWindowToolSaveBits"
NOX_7_0_1_1_CHILD_NAME = "sub"


class NoxPlayer(AndroidEmulator):
    """Class for working with NoxPlayer emulator."""

    def __init__(self, name="NoxPlayer", child_name="ScreenBoardClassWindow", key_handle_name=None):
        """Class initialization.

        :param str name: main window's name of the emulator.
        :param str child_name: child window's name of inner control window.
        :param str key_handle_name: name of windows's key handler.
        """
        super().__init__(name=name, child_name=child_name, key_handle_name=key_handle_name)
        self.close_app_shortcut = self._get_keyboard_shortcut_for_closing_app() if self.initialized else None

    def _set_params_by_version(self):
        """Sets params for NoxPlayer by its version."""
        self.key_handle_name = NOX_6_KEY_HANDLE_NAME
        self.key_handle_class = NOX_6_KEY_HANDLE_CLASS
        version = self.get_version()
        if version and version >= LooseVersion('7.0.0.0'):
            self.key_handle_name = NOX_7_KEY_HANDLE_NAME
            self.key_handle_class = NOX_7_KEY_HANDLE_CLASS
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

    def _get_key_layout_handle(self, hwnd, wildcard):
        """Gets information about general key handler.

        :param int hwnd: window handle.
        :param str wildcard: wildcard.
        """
        if self.key_handle_name == win32gui.GetWindowText(hwnd) and self.key_handle_class == win32gui.GetClassName(
                hwnd) and self.parent_hwnd == win32gui.GetParent(hwnd):
            self.key_handle = hwnd

    def close_current_app(self):
        """Closes current opened app in emulator."""
        hwnd = self.key_handle if self.key_handle else self.main_key_handle
        try:
            autoit.control_send_by_handle(hwnd, hwnd, f"^{self.close_app_shortcut}")
        except autoit.AutoItError as err:
            logging.error(f"Error during sending to control {hwnd}:\n{err}")
            self.update_handlers()
            hwnd = self.key_handle if self.key_handle else self.main_key_handle
            logging.warning(f"Updating window's info, new control is {hwnd}")
            autoit.control_send_by_handle(hwnd, hwnd, f"^{self.close_app_shortcut}")

    def update_handlers(self):
        """Updates window's handlers and stores info from them."""
        was_closed = not self.initialized
        win32gui.EnumWindows(self._get_window_info, None)
        win32gui.EnumWindows(self._get_key_layout_handle, None)
        win32gui.EnumChildWindows(self.parent_hwnd, self._get_key_layout_handle, None)
        win32gui.EnumChildWindows(self.parent_hwnd, self._get_emulator_window_info, None)
        if was_closed and self.initialized:
            self.close_app_shortcut = self._get_keyboard_shortcut_for_closing_app()
            self._set_params_by_version()

    @staticmethod
    def _read_config_file(config_file="conf.ini"):
        """Reads NoxPlayer's config file.

        :param str config_file: name of the config file.

        :rtype: ConfigParser
        """
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
        """Saves NoxPlayer's config file.

        :param ConfigParser config: config to save.
        :param str config_file: name of the config file to save as.
        """
        path = os.path.join(os.getenv('APPDATA'), "..", "Local", "Nox", config_file)
        with open(path, 'w', encoding="utf-8") as file:
            config.write(file)

    def _get_virtual_machine_id(self):
        """Gets NoxPlayer's Virtual Machine ID of current process.

        :rtype: int
        """
        path = os.path.join(os.getenv('APPDATA'), "..", "Local", "MultiPlayerManager", "multiplayer.xml")
        try:
            for _, elem in ElementTree.iterparse(path):
                if elem.attrib.get("name") == self.name:
                    return elem.attrib['id']
        except FileNotFoundError:
            return logging.warning(f"Can't find NoxPlayer's multiplayer settings in %APPDATA% folder by path: {path}.")

    def get_config_file(self):
        """Gets config that is related to current emulator's process.

        :rtype: ConfigParser
        """
        vm_id = self._get_virtual_machine_id()
        config_file = "conf.ini" if vm_id in [DEFAULT_NOX_ID, None] else f"clone_{vm_id}_conf.ini"
        return self._read_config_file(config_file=config_file), config_file

    def set_config_for_bot(self):
        """Sets necessary configs to NoxPlayer. Graphic engine should be set to DirectX,
        restart shortcut should be set as hotkey (index within 1-10 range).

        Works only at 6.x.x versions of NoxPlayer.
        """
        config, config_file = self.get_config_file()
        if not config or not config.has_section("toolbar_setting") or not config.has_section("setting"):
            return
        config["toolbar_setting"].clear()
        config["toolbar_setting"] = {"toolbar_close_all_index": f"{OLD_VERSION_INDEX}"}
        config["setting"]["graphic_engine_type"] = f"{GRAPHIC_ENGINE_TYPE_DIRECTX}"
        self._save_config_file(config=config, config_file=config_file)
        logging.info(f"{self.name}: saved config file {config_file}. Need to restart emulator to apply changes.")

    def _get_keyboard_shortcut_for_closing_app(self):
        """Gets keyboard shortcut for closing all apps from config file."""
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
        """Checks if app can be restarted."""
        keys_found = self.key_handle is not None and self.main_key_handle is not None
        return keys_found and self.close_app_shortcut is not None
