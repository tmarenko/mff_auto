import logging
from lib.emulators.android_emulator import AndroidEmulator

BLUESTACKS_EXE = "Bluestacks.exe"


class BlueStacks(AndroidEmulator):
    """Class for working with BlueStacks emulator."""

    def __init__(self, name="BlueStacks", child_name="BlueStacks Android PluginAndroid", key_handle_name="BlueStacks"):
        """Class initialization.

        :param name: main window's name of the emulator.
        :param child_name: child window's name of inner control window.
        :param key_handle_name: name of windows's key handler.
        """
        super().__init__(name=name, child_name=child_name, key_handle_name=key_handle_name)

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
