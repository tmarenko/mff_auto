import autoit
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
        autoit.control_send_by_handle(self.player_key_handle, self.player_key_handle, "^7")  # CTRL+7 shortcut

    @property
    def restartable(self):
        """Returns if app can be restarted."""
        return self.get_version() in ["6.3.0.0", "6.3.0.1", "6.3.0.2", "6.3.0.4", "6.3.0.5"]
