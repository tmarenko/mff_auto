import win32gui, win32process, win32api, win32con
import pywintypes
from PyQt5.QtWidgets import QDialog, QListWidgetItem
from PyQt5.QtGui import QIcon
from lib.gui.helper import Timer, screen_to_gui_image, try_to_disconnect, set_default_icon
from lib.gui.widgets.game_image import ScreenImageLabel
import lib.gui.designes.setup_player as player_design
import lib.gui.designes.setup_game as game_design

from lib.game.game import Game
from lib.players.nox_player import NoxWindow, NOX_EXE
from lib.players.bluestacks import BlueStacks, BLUESTACKS_EXE
from lib.game.ui import Rect
import lib.logger as logging

logger = logging.get_logger(__name__)


class PlayerProcess(QListWidgetItem):
    """Class for working with player's process."""

    def __init__(self, player, process_name, process_id):
        """Class initialization.

        :param player: instance of game player.
        :param process_name: player's process name.
        :param process_id: player's process ID.
        """
        super().__init__()
        self.process_name = process_name
        self.process_id = process_id
        self.player = player
        self.setText(player.name)
        self.update_thumbnail()

    def update_thumbnail(self):
        """Update icon with thumbnail of player's screen."""
        try:
            if self.player.initialized:
                self.player.update_windows_rect()
                thumbnail = screen_to_gui_image(self.player.get_screen_image())
                self.setIcon(QIcon(thumbnail))
                # TODO: if you see black screen then change settings of noxplayer
        except pywintypes.error:
            self.player.hwnd = None
            self.setText(f"{self.text()} (INACTIVE)")


class SetupPlayer(QDialog, player_design.Ui_Dialog):
    """Class for working with setting up player's settings for GUI."""

    def __init__(self):
        """Class initialization."""
        super().__init__()
        self.setupUi(self)
        set_default_icon(self)
        win32gui.EnumWindows(self.get_processes_info, None)
        self.timer = Timer()
        self.timer.set_timer(self.update_processes_thumbnails)
        self.players_list_widget.itemClicked.connect(self.on_item_select)
        self.selected_player = None
        self.selected_player_process = None
        self.next_button.clicked.connect(self.run_game_setup)
        self.setup_game = None

    def run_player_setup(self):
        """Run the setup."""
        self.show()
        self.exec_()

    def run_game_setup(self):
        """Start setting up game settings."""
        self.hide()
        if self.selected_player.restartable:
            self.setup_game = SetupGame(player=self.selected_player)
            self.setup_game.show()
            self.setup_game.exec()

    def player_processes(self):
        """Processes iterator."""
        for i in range(self.players_list_widget.count()):
            yield self.players_list_widget.item(i)

    def get_processes_info(self, hwnd, wildcard):
        """Get all processes info and add to list those that has same process name as Nox.

        :param hwnd: window handle.
        :param wildcard: wildcard.
        """
        name = win32gui.GetWindowText(hwnd)
        p_hwnd, process_id = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, 0, process_id)
            process_exe = win32process.GetModuleFileNameEx(process, 0)
            if any(exe_name in process_exe for exe_name in [NOX_EXE, BLUESTACKS_EXE]):
                self.add_process_to_list(process_name=name, process_id=process_id, process_exe=process_exe)
        except pywintypes.error:
            pass

    def add_process_to_list(self, process_name, process_id, process_exe):
        """Add process to list widget.

        :param process_name: player's process name.
        :param process_id: player's process ID.
        :param process_exe: player's executable.
        """
        if [p for p in self.player_processes() if p.process_name == process_name or p.process_id == process_id]:
            return
        if NOX_EXE in process_exe:
            player = NoxWindow(name=process_name)
        if BLUESTACKS_EXE in process_exe:
            player = BlueStacks(name=process_name)
        if player.initialized:
            process = PlayerProcess(player=player, process_name=process_name, process_id=process_id)
            self.players_list_widget.addItem(process)

    def update_processes_thumbnails(self):
        """Update processes' thumbnails."""
        win32gui.EnumWindows(self.get_processes_info, None)
        for process in self.player_processes():
            process.update_thumbnail()

    def on_item_select(self, item):
        """Event when item is selected."""
        self.selected_player = item.player
        self.selected_player_process = item.process_name
        self.selected_player_info_label.setText(f"Selected: {item.process_name}")
        self.next_button.setEnabled(True)

    def get_player_and_game_app(self):
        """Get player's name and game app rect after setup."""
        if not self.selected_player or not self.setup_game:
            logger.error("Something went wrong while setting up player's name and app position.")
        player_name = self.selected_player_process
        game_app = self.setup_game.game_app_rect if self.setup_game else None
        return player_name, self.selected_player.__class__.__name__, game_app


class SetupGame(QDialog, game_design.Ui_Dialog):
    """Class for working with setting up game's settings for GUI."""

    def __init__(self, player):
        """Class initialization.

        :param player: instance of game player.
        """
        super().__init__()
        self.setupUi(self)
        set_default_icon(self)
        self.player = player
        self.game = Game(self.player)
        self.screen_image = ScreenImageLabel(widget=self.screen_image_label, player=self.player)
        self.set_visibility_to_all(True)
        self.is_game_opened_q()
        self.game_app_rect = None
        self.screen_image_label.mousePressEvent = self.screen_click_event
        self.ready_to_press = False

    def screen_click_event(self, event):
        """Click event on screen image."""
        if not self.ready_to_press:
            return
        x, y = event.pos().x(), event.pos().y()
        player_rect = Rect(0, 0, self.player.width, self.player.height)
        game_app_rect = Rect(x / self.screen_image.widget.size().width(),
                             y / self.screen_image.widget.size().height(),
                             x / self.screen_image.widget.size().width(),
                             y / self.screen_image.widget.size().height())
        game_app_global_rect = game_app_rect.to_global(player_rect)
        self.game_app_rect = (game_app_global_rect[0] / self.player.width, game_app_global_rect[1] / self.player.height,
                              game_app_global_rect[2] / self.player.width, game_app_global_rect[3] / self.player.height)
        self.player.click_button(self.game_app_rect)

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
        self.top_text_label.setText("Look at the player's screen image below. Is MFF game opened right now?")
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
        if self.player.restartable:
            self.player.close_current_app()
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
        self.top_text_label.setText("Look at the player's screen image below. Click on this image where MFF game icon.")
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
        self.top_text_label.setText(f"Found game app at ({self.game_app_rect}). Setup complete!")
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
