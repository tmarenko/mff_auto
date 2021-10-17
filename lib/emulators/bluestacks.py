from distutils.version import LooseVersion
from lib.emulators.android_emulator import AndroidEmulator

BLUESTACKS_4_EXE = "Bluestacks.exe"
BLUESTACKS_5_CHILD_NAME = "plrNativeInputWindow"
BLUESTACKS_5_EXE = "HD-Player.exe"


class BlueStacks(AndroidEmulator):
    """Class for working with BlueStacks emulator."""

    def __init__(self, name="BlueStacks", child_name="BlueStacks Android PluginAndroid"):
        """Class initialization.

        :param str name: main window's name of the emulator.
        :param str child_name: child window's name of inner control window.
        """
        super().__init__(name=name, child_name=child_name, adb_path="adb.exe")

    def _set_params_by_version(self):
        """Sets params for BlueStacks by its version."""
        version = self.get_version()
        if version and version >= LooseVersion('5.0'):
            self.child_name = BLUESTACKS_5_CHILD_NAME
        self.update_handlers()
