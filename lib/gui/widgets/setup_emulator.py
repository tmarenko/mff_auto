import pywintypes
import win32api
import win32con
import win32gui
import win32process
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QListWidgetItem

import lib.gui.designes.setup_emulator as emulator_design
import lib.gui.designes.setup_game as game_design
import lib.logger as logging
from lib.emulators.bluestacks import BlueStacks, BLUESTACKS_4_EXE, BLUESTACKS_5_EXE
from lib.emulators.nox_player import NoxPlayer, NOX_EXE
from lib.game.game import Game
from lib.game.ui.general import Rect, UIElement
from lib.gui.helper import Timer, screen_to_gui_image, try_to_disconnect, set_default_icon
from lib.gui.widgets.game_image import ScreenImageLabel

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
        except pywintypes.error:
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
        self.emulators_list_widget.itemClicked.connect(self.on_item_select)
        self.selected_emulator = None
        self.selected_emulator_process = None
        self.next_button.clicked.connect(self.run_game_setup)
        self.setup_game = None

    def run_emulator_setup(self):
        """Run the setup."""
        self.show()
        self.exec_()

    def run_game_setup(self):
        """Start setting up game settings."""
        self.hide()
        if isinstance(self.selected_emulator, NoxPlayer):
            self.selected_emulator.set_config_for_bot()
            self.setup_game = SetupGame(emulator=self.selected_emulator)
            self.setup_game.show()
            self.setup_game.exec()
        if isinstance(self.selected_emulator, BlueStacks):
            return

    def emulator_processes(self):
        """Processes iterator."""
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
        except pywintypes.error:
            pass

    def add_process_to_list(self, process_name, process_id, process_exe):
        """Add process to list widget.

        :param str process_name: emulator's process name.
        :param int process_id: emulator's process ID.
        :param str process_exe: emulator's executable.
        """
        if [p for p in self.emulator_processes() if p.process_name == process_name or p.process_id == process_id]:
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
        for process in self.emulator_processes():
            process.update_thumbnail()

    def on_item_select(self, item):
        """Event when item is selected."""
        self.selected_emulator = item.emulator
        self.selected_emulator_process = item.process_name
        self.selected_emulator_info_label.setText(f"Selected: {item.process_name}")
        self.next_button.setEnabled(True)

    def get_emulator_and_game_app(self):
        """Get emulator's name and game app rect after setup."""
        if not self.selected_emulator or not self.setup_game:
            logger.error("Something went wrong while setting up emulator's name and app position.")
        emulator_name = self.selected_emulator_process
        game_app = self.setup_game.game_app_rect if self.setup_game else None  # type: Rect
        return emulator_name, self.selected_emulator.__class__.__name__, game_app.value


class SetupGame(QDialog, game_design.Ui_Dialog):
    """Class for working with setting up game's settings for GUI."""

    def __init__(self, emulator):
        """Class initialization.

        :param lib.emulators.android_emulator.AndroidEmulator: instance of game emulator.
        """
        super().__init__()
        self.setupUi(self)
        set_default_icon(window=self)
        self.emulator = emulator
        self.game = Game(self.emulator)
        self.screen_image = ScreenImageLabel(widget=self.screen_image_label, emulator=self.emulator)
        self.set_visibility_to_all(True)
        self.is_game_opened_q()
        self.game_app_rect = None  # type: Rect
        self.screen_image_label.mousePressEvent = self.screen_click_event
        self.ready_to_press = False

    def screen_click_event(self, event):
        """Click event on screen image."""
        if not self.ready_to_press:
            return
        x, y = event.pos().x(), event.pos().y()
        emulator_rect = Rect(0, 0, self.emulator.width, self.emulator.height)
        game_app_rect = Rect(x / self.screen_image.widget.size().width(),
                             y / self.screen_image.widget.size().height(),
                             x / self.screen_image.widget.size().width(),
                             y / self.screen_image.widget.size().height())
        game_app_global_rect = game_app_rect.to_global(emulator_rect)
        self.game_app_rect = Rect(
            game_app_global_rect[0] / self.emulator.width, game_app_global_rect[1] / self.emulator.height,
            game_app_global_rect[2] / self.emulator.width, game_app_global_rect[3] / self.emulator.height)
        game_app_ui = UIElement(name="TEMP_GAME_APP")
        game_app_ui.button_rect = self.game_app_rect
        self.emulator.click_button(game_app_ui)

    def set_visibility_to_all(self, visible=True):
        """Set visibility to all elements in window."""
        self.question_label.setVisible(visible)
        self.top_text_label.setVisible(visible)
        self.yes_button.setEnabled(visible)
        self.yes_button.setVisible(visible)
        self.no_button.setEnabled(visible)
        self.no_button.setVisible(visible)

    def disconnect_a(self):
        """Disconnect functions from buttons."""
        try_to_disconnect(self.yes_button.clicked)
        try_to_disconnect(self.no_button.clicked)

    def is_game_opened_q(self):
        """Question: is game opened?"""
        self.top_text_label.setText("Look at the emulator's screen image below. Is MFF game opened right now?")
        self.question_label.setText("Is game opened right now?")
        self.disconnect_a()
        self.yes_button.clicked.connect(self.is_game_opened_yes)
        self.no_button.clicked.connect(self.is_game_opened_no)

    def is_game_opened_yes(self):
        """Answer: yes, game is opened.
        Question: is game opened?"""
        self.top_text_label.setText("Trying to close the game...")
        self.question_label.setText("Is game opened right now?")
        self.disconnect_a()
        self.yes_button.clicked.connect(self.is_game_opened_yes)
        self.no_button.clicked.connect(self.is_game_opened_no)
        if self.emulator.restartable:
            self.emulator.close_current_app()
        self.top_text_label.setText("Trying to close the game... Game should be closed now.")

    def is_game_opened_no(self):
        """Answer: no, game is closed.
        Question: is app on screen?"""
        self.top_text_label.setText("Then you should see home screen. Is MFF game icon on this screen?")
        self.question_label.setText("Is MFF game icon on the screen?")
        self.disconnect_a()
        self.yes_button.clicked.connect(self.is_game_app_on_screen_yes)
        self.no_button.clicked.connect(self.is_game_app_on_screen_no)

    def is_game_app_on_screen_yes(self):
        """Answer: yes, app on screen.
        Question: is game started?"""
        self.top_text_label.setText(
            "Look at the emulator's screen image below. Click on this image where MFF game icon.")
        self.question_label.setText("Is game started to open?")
        self.disconnect_a()
        self.yes_button.clicked.connect(self.is_game_started_yes)
        self.no_button.clicked.connect(self.is_game_started_no)
        self.ready_to_press = True

    def is_game_app_on_screen_no(self):
        """Answer: no, no app on screen.
        Question: is app on screen?"""
        self.top_text_label.setText("Please move MFF app on the main home screen yourself.")
        self.question_label.setText("Is MFF game icon on the screen?")
        self.disconnect_a()
        self.yes_button.clicked.connect(self.is_game_app_on_screen_yes)
        self.no_button.clicked.connect(self.is_game_app_on_screen_no)

    def is_game_started_yes(self):
        """Answer: yes, game is started.
        Setup is done."""
        if not self.game_app_rect:
            return self.is_game_started_no()
        self.top_text_label.setText(f"Found game app at ({self.game_app_rect.value}). Setup complete!")
        self.question_label.setText("Setup is done")
        self.disconnect_a()
        self.no_button.setVisible(False)
        self.no_button.setEnabled(False)
        self.yes_button.clicked.connect(self.accept)

    def is_game_started_no(self):
        """Answer: no, game isn't started."""
        self.set_visibility_to_all(False)
        self.top_text_label.setVisible(True)
        self.top_text_label.setText("Something wrong with emulator's setup. Check README!")
