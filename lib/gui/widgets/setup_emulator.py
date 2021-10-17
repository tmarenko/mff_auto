import win32api
import win32con
import win32gui
import win32process
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QListWidgetItem
from typing import Union

import lib.gui.designes.setup_emulator as emulator_design
import lib.logger as logging
from lib.emulators import BlueStacks, BLUESTACKS_4_EXE, BLUESTACKS_5_EXE, NoxPlayer, NOX_EXE
from lib.gui.helper import Timer, screen_to_gui_image, set_default_icon

logger = logging.get_logger(__name__)


class EmulatorProcess(QListWidgetItem):
    """Class for working with emulator's process."""

    def __init__(self, emulator, process_name, process_id):
        """Class initialization.

        :param lib.emulators.android_emulator.AndroidEmulator emulator: instance of game emulator.
        :param str process_name: emulator's process name.
        :param int process_id: emulator's process ID.
        """
        super().__init__()
        self.process_name = process_name
        self.process_id = process_id
        self.emulator = emulator
        self.setText(emulator.name)
        self.update_thumbnail()

    def update_thumbnail(self):
        """Update icon with thumbnail of emulator's screen."""
        try:
            if self.emulator.initialized:
                self.emulator.update_window_rectangles()
                thumbnail = screen_to_gui_image(self.emulator.get_screen_image())
                self.setIcon(QIcon(thumbnail))
        except BaseException:
            self.emulator.hwnd = None
            self.setText(f"{self.text()} (INACTIVE)")


class SetupEmulator(QDialog, emulator_design.Ui_Dialog):
    """Class for working with setting up emulator's settings for GUI."""

    def __init__(self):
        """Class initialization."""
        super().__init__()
        self.setupUi(self)
        set_default_icon(window=self)
        win32gui.EnumWindows(self.get_processes_info, None)
        self.timer = Timer()
        self.timer.set_timer(self.update_processes_thumbnails)
        self.emulators_list_widget.itemClicked.connect(self.on_emulator_item_select)
        self.selected_emulator = None  # type: Union[BlueStacks, NoxPlayer, None]
        self.selected_emulator_process = None
        self.next_button.clicked.connect(self.close)

    def run_emulator_setup(self):
        """Run the setup."""
        self.show()
        self.exec_()

    def items(self):
        """List widget's items iterator."""
        for i in range(self.emulators_list_widget.count()):
            yield self.emulators_list_widget.item(i)

    def get_processes_info(self, hwnd, wildcard):
        """Get all processes info and add to list those that has same process name as Nox.

        :param int hwnd: window handle.
        :param str wildcard: wildcard.
        """
        name = win32gui.GetWindowText(hwnd)
        p_hwnd, process_id = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, process_id)
            process_exe = win32process.GetModuleFileNameEx(process, 0)
            if any(exe_name in process_exe for exe_name in [NOX_EXE, BLUESTACKS_4_EXE, BLUESTACKS_5_EXE]):
                self.add_process_to_list(process_name=name, process_id=process_id, process_exe=process_exe)
        except BaseException:
            pass

    def add_process_to_list(self, process_name, process_id, process_exe):
        """Add process to list widget.

        :param str process_name: emulator's process name.
        :param int process_id: emulator's process ID.
        :param str process_exe: emulator's executable.
        """
        if [p for p in self.items() if p.process_name == process_name or p.process_id == process_id]:
            return
        if NOX_EXE in process_exe:
            emulator = NoxPlayer(name=process_name)
        if BLUESTACKS_4_EXE in process_exe or BLUESTACKS_5_EXE in process_exe:
            emulator = BlueStacks(name=process_name)
        if emulator.initialized:
            process = EmulatorProcess(emulator=emulator, process_name=process_name, process_id=process_id)
            self.emulators_list_widget.addItem(process)

    def update_processes_thumbnails(self):
        """Update processes' thumbnails."""
        win32gui.EnumWindows(self.get_processes_info, None)
        for process in self.items():
            process.update_thumbnail()

    def on_emulator_item_select(self, item: EmulatorProcess):
        """Event when item is selected."""
        self.selected_emulator = item.emulator
        self.selected_emulator_process = item.process_name
        self.selected_emulator_info_label.setText(f"Selected: {item.process_name}")
        self.next_button.setEnabled(True)

    def get_emulator_and_game_app(self):
        """Get emulator's name and game app rect after setup."""
        if not self.selected_emulator or not self.selected_emulator_process:
            logger.error("Something went wrong while setting up emulator.")
        return self.selected_emulator_process, self.selected_emulator.__class__.__name__
