import json
import os
from distutils.version import LooseVersion
from os.path import exists

from PyQt5.QtWidgets import QMainWindow
from multiprocess.managers import SyncManager

import lib.gui.designes.main_window as design
import lib.logger as logging
from lib.emulators.bluestacks import BlueStacks
from lib.emulators.nox_player import NoxPlayer
from lib.functions import bgr_to_rgb
from lib.game import ui
from lib.game.battle_bot import BattleBot
from lib.game.game import Game
from lib.game.ui.general import Rect
from lib.gui.helper import TwoStateButton, set_default_icon, Timer, try_to_disconnect
from lib.gui.logger import QTextEditFileLogger
from lib.gui.queue_manager import QueueList
from lib.gui.single_task_manager import AutoPlayTask, DailyTriviaTask, WorldBossInvasionTask, SquadBattleAllTask, \
    DangerRoomOneBattleTask, RestartGameTask, ComicCardsTask, CustomGearTask, DispatchMissionAcquireTask, \
    EnhancePotentialTask, ShadowlandAllFloorsTask
from lib.gui.threading import ThreadPool
from lib.gui.widgets.game_image import ScreenImageLabel
from lib.gui.widgets.setup_emulator import SetupEmulator
from lib.video_capture import EmulatorCapture

logger = logging.get_logger(__name__)


def load_game_settings(path="settings/gui/game.json"):
    """Loads game settings for GUI."""
    if exists(path):
        try:
            with open(path, encoding='utf-8') as json_data:
                return json.load(json_data)
        except json.decoder.JSONDecodeError as err:
            logger.error(err)
            with open(path, encoding='utf-8') as json_data:
                logger.error(f"Corrupted data in {path} file. File content:\n{json_data.readlines()}")
    return {}


def save_game_settings(json_data, path="settings/gui/game.json"):
    """Stores game settings."""
    with open(path, mode='w', encoding='utf-8') as file:
        json.dump(json_data, file)


class MainWindow(QMainWindow, design.Ui_MainWindow):
    """Class for working with main GUI window."""

    recorder = None

    @classmethod
    def pause_recorder(cls):
        if isinstance(cls.recorder, EmulatorCapture):
            cls.recorder.pause()

    @classmethod
    def resume_recorder(cls):
        if isinstance(cls.recorder, EmulatorCapture):
            cls.recorder.resume()

    def __init__(self, file_logger, settings):
        """Class initialization.

        :param logging.FileHandler file_logger: file handler of log-file.
        :param PyQt5.QtCore.QSettings.QSettings settings: GUI settings.
        """
        super().__init__()
        self.setupUi(self)
        set_default_icon(window=self)
        self.settings = settings
        self._init_window_settings()
        self.emulator_name, self.emulator_type, self.game_app_rect, self.emulator, self.game = None, None, None, None, None
        self.load_settings_from_file()
        self.game.file_logger_name = None
        if file_logger:
            self.game.file_logger_name = file_logger.baseFilename
            self.logger = QTextEditFileLogger(all_logger_widget=self.logger_text,
                                              info_logger_widget=self.logger_text_info,
                                              error_logger_widget=self.logger_text_error,
                                              log_file=file_logger.baseFilename)
        else:
            self.logger_text.setPlainText("Cannot create log file because `logs` folder doesn't exists.")
        run_and_stop_button = self.create_blockable_button(button=self.run_queue_button)
        self.queue_list = QueueList(list_widget=self.queue_list_widget, run_and_stop_button=run_and_stop_button,
                                    add_button=self.add_queue_button, edit_button=self.edit_queue_button,
                                    remove_button=self.remove_queue_button, game=self.game,
                                    queue_selector_buttons=[self.queue_button_1, self.queue_button_2,
                                                            self.queue_button_3, self.queue_button_4])
        self.screen_image = ScreenImageLabel(emulator=self.emulator, widget=self.screen_label)
        self.acquire_heroic_quest_rewards_checkbox.stateChanged.connect(self.acquire_heroic_quest_rewards_state_changed)
        self.low_memory_mode_checkbox.stateChanged.connect(self.low_memory_mode_state_changed)
        self.mission_team_spin_box.valueChanged.connect(self.mission_team_changed)
        self.timeline_team_spin_box.valueChanged.connect(self.timeline_team_changed)
        self.threads = ThreadPool()
        self._user_name_acquired = False
        self.update_labels()
        self.label_timer = Timer()
        self.label_timer.set_timer(self.update_labels, timer_ms=5000)
        self.blockable_buttons = [self.run_queue_button, self.add_queue_button, self.edit_queue_button,
                                  self.remove_queue_button]
        self.tasks = []
        self.create_tasks()

        if self.emulator.initialized and self.emulator.restartable:
            if not self.game.is_main_menu() and not BattleBot(self.game, None).is_battle():
                if not self.game.go_to_main_menu():
                    logger.warning("Can't get to the main menu. Restarting the game just in case.")
                    self.restart_game_button.click()
        self._create_menu_for_recorder()

    def _init_window_settings(self):
        """Restores the State of a GUI from settings."""
        self.resize(self.settings.value("MainWindow/size", defaultValue=self.size()))
        self.move(self.settings.value("MainWindow/pos", defaultValue=self.pos()))
        if self.settings.value("MainWindow/isMaximized") == 'true':
            self.showMaximized()
        self.low_memory_mode_checkbox.setChecked(
            self.settings.value("mff_low_memory_mode", defaultValue="false").lower() == "true")

    def update_labels(self):
        """Updates game's labels in thread to prevent GUI freezing."""
        self.threads.run_thread(target=self._update_labels)

    def _update_labels(self):
        """Updates game's labels such as: username, energy, gold and boost points."""
        if not self.emulator.initialized:
            return
        if not self._user_name_acquired and self.game.is_main_menu():
            self.label_username.setText(self.game.user_name)
            self._user_name_acquired = True
        self.label_energy.setText(f"Energy: {self.game.energy} / {self.game.energy_max}")
        self.label_gold.setText(f"Gold: {self.game.gold}")
        self.label_boosts.setText(f"Boosts: {self.game.boost} / {100}")

    def mission_team_changed(self):
        """'Mission team' spinbox event when value is changed."""
        team = self.mission_team_spin_box.value()
        self.game.set_mission_team(team)
        logger.info(f"Team number for missions : {self.game.mission_team}")
        self.save_settings_to_file()

    def timeline_team_changed(self):
        """'Timeline team' spinbox event when value is changed."""
        team = self.timeline_team_spin_box.value()
        self.game.set_timeline_team(team)
        logger.info(f"Team number for TimeLine battles : {self.game.timeline_team}")
        self.save_settings_to_file()

    def acquire_heroic_quest_rewards_state_changed(self):
        """'Acquire heroic quest rewards' checkbox even when value is changed."""
        if self.acquire_heroic_quest_rewards_checkbox.isChecked():
            self.game.ACQUIRE_HEROIC_QUEST_REWARDS = True
        else:
            self.game.ACQUIRE_HEROIC_QUEST_REWARDS = False
        logger.info(f"Acquire Heroic Quest rewards: {self.game.ACQUIRE_HEROIC_QUEST_REWARDS}")
        self.save_settings_to_file()

    def low_memory_mode_state_changed(self):
        """'Low memory mode' checkbox even when value is changed."""
        self.settings.setValue("mff_low_memory_mode", self.low_memory_mode_checkbox.isChecked())
        os.environ['MFF_LOW_MEMORY_MODE'] = str(self.low_memory_mode_checkbox.isChecked())
        logger.info(f"Low memory mode: {self.low_memory_mode_checkbox.isChecked()}")

    def load_settings_from_file(self):
        """Loads settings and applies them to game."""
        game_settings = load_game_settings()
        if not game_settings:
            self.setup_gui_first_time()
            return self.load_settings_from_file()
        self.game_app_rect = game_settings.get("game_app_rect")
        self.emulator_name = game_settings.get("emulator_name")
        self.emulator_type = game_settings.get("emulator_type")
        self.timeline_team_spin_box.setValue(game_settings.get("timeline_team"))
        self.mission_team_spin_box.setValue(game_settings.get("mission_team"))
        self.acquire_heroic_quest_rewards_checkbox.setChecked(game_settings.get("acquire_heroic_quest_rewards", True))
        self.init_emulator_and_game()
        self.game.set_mission_team(self.mission_team_spin_box.value())
        self.game.set_timeline_team(self.timeline_team_spin_box.value())
        self.game.ACQUIRE_HEROIC_QUEST_REWARDS = self.acquire_heroic_quest_rewards_checkbox.isChecked()

    def save_settings_to_file(self):
        """Stores GUI settings to file."""
        game_settings = {
            "timeline_team": self.game.timeline_team,
            "mission_team": self.game.mission_team,
            "acquire_heroic_quest_rewards": self.game.ACQUIRE_HEROIC_QUEST_REWARDS,
            "emulator_name": self.emulator_name,
            "emulator_type": self.emulator_type,
            "game_app_rect": self.game_app_rect
        }
        save_game_settings(game_settings)
        logger.debug("Game settings saved.")

    def setup_gui_first_time(self):
        """Setups GUI settings for first time.
        Runs `SetupEmulator` and retrieves information about emulator and game app."""
        setup = SetupEmulator()
        setup.run_emulator_setup()
        self.emulator_name, self.emulator_type, self.game_app_rect = setup.get_emulator_and_game_app()
        game_settings = {
            "timeline_team": self.timeline_team_spin_box.value(),
            "mission_team": self.mission_team_spin_box.value(),
            "acquire_heroic_quest_rewards": self.acquire_heroic_quest_rewards_checkbox.isChecked(),
            "low_memory_mode": self.low_memory_mode_checkbox.isChecked(),
            "emulator_name": self.emulator_name,
            "emulator_type": self.emulator_type,
            "game_app_rect": self.game_app_rect
        }
        save_game_settings(game_settings)
        logger.debug("Saving setting from first setup.")

    def init_emulator_and_game(self):
        """Initializes emulator and game objects."""
        if not self.emulator_name:
            self.setup_gui_first_time()
        if self.emulator_type == NoxPlayer.__name__:
            self.emulator = NoxPlayer(self.emulator_name)
            if self.emulator.get_version() and self.emulator.get_version() < LooseVersion('7.0.0.0'):
                menu = self.menuBar.addMenu("Emulator")
                action = menu.addAction(f"Make {self.emulator.name} restartable")
                action.triggered.connect(self.emulator.set_config_for_bot)
        if self.emulator_type == BlueStacks.__name__:
            self.emulator = BlueStacks(self.emulator_name)
        if not self.emulator.restartable:
            self.restart_game_button.setEnabled(False)
            self.restart_game_button.setText(f"{self.restart_game_button.text()}\n"
                                             "[Unavailable (check logs)]")
            self.restart_game_button = None
        self.game = Game(self.emulator)
        self.manager = SyncManager()
        self.manager.start()
        self.game._modes = self.manager.dict()
        if self.game_app_rect:
            ui.GAME_APP.button_rect = Rect(*self.game_app_rect)

    def _create_menu_for_recorder(self):
        """Creates menu bar for emulator recording."""
        menu = self.menuBar.addMenu("Video Recorder")
        self.recorder_action = menu.addAction("Start recording")
        self.recorder_action.triggered.connect(self._start_recording)

    def _start_recording(self):
        """Starts recording video from emulator."""
        MainWindow.recorder = EmulatorCapture(self.emulator)
        MainWindow.recorder.start()
        MainWindow.recorder.pause()

        self.recorder_action.setText("Stop recording")
        try_to_disconnect(self.recorder_action.triggered, self._start_recording)
        self.recorder_action.triggered.connect(self._stop_recording)

        self.screen_image.get_image_func = lambda: bgr_to_rgb(MainWindow.recorder.video_capture.source.frame())

    def _stop_recording(self):
        """Stops recording video from emulator."""
        MainWindow.recorder.stop()
        MainWindow.recorder = None

        self.recorder_action.setText("Start recording")
        try_to_disconnect(self.recorder_action.triggered, self._stop_recording)
        self.recorder_action.triggered.connect(self._start_recording)

        self.screen_image.get_image_func = self.emulator.get_screen_image

    def closeEvent(self, event):
        """Main window close event."""
        self.queue_list.stop_queue()
        for task in self.tasks:
            task.abort()
        self.save_settings_to_file()
        self.queue_list.save_queue_to_file()
        self.settings.setValue("MainWindow/size", self.size())
        self.settings.setValue("MainWindow/isMaximized", self.isMaximized())
        self.settings.setValue("MainWindow/pos", self.pos())
        self.settings.setValue("mff_low_memory_mode", self.low_memory_mode_checkbox.isChecked())

    def create_blockable_button(self, button):
        """Creates button that blocks others."""
        if not button:
            return
        two_state_button = TwoStateButton(button=button)
        two_state_button.connect_first_state(self.block_buttons, caller_button=button)
        two_state_button.connect_second_state(self.unblock_buttons)
        two_state_button.signals.first_state.connect(self.unblock_buttons)
        return two_state_button

    def block_buttons(self, caller_button):
        """Blocks buttons except caller one.

        :param PyQt5.QtWidgets.QPushButton.QPushButton caller_button: button that called the event.
        """
        buttons_to_block = [button for button in self.blockable_buttons if
                            button and button.isEnabled() and button != caller_button]
        for button in buttons_to_block:
            button.setEnabled(False)

    def unblock_buttons(self):
        """Unblocks all buttons."""
        for button in self.blockable_buttons:
            if button:
                button.setEnabled(True)

    def _create_task(self, button, task_class):
        """Creates blockable button for task and initialized it.

        :param PyQt5.QtWidgets.QPushButton.QPushButton button: button to run the task.
        :param type[lib.gui.single_task_manager.SingleTask] task_class: class object of the task.
        """
        blockable_button = self.create_blockable_button(button=button)
        task = task_class(game=self.game, button=blockable_button)
        self.blockable_buttons.append(button)
        self.tasks.append(task)

    def create_tasks(self):
        """Creates all available tasks."""
        self._create_task(button=self.autoplay_button, task_class=AutoPlayTask)
        self._create_task(button=self.daily_trivia_button, task_class=DailyTriviaTask)
        self._create_task(button=self.world_boss_invasion_button, task_class=WorldBossInvasionTask)
        self._create_task(button=self.squad_battle_button, task_class=SquadBattleAllTask)
        self._create_task(button=self.danger_room_button, task_class=DangerRoomOneBattleTask)
        self._create_task(button=self.restart_game_button, task_class=RestartGameTask)
        self._create_task(button=self.comic_cards_button, task_class=ComicCardsTask)
        self._create_task(button=self.custom_gear_button, task_class=CustomGearTask)
        self._create_task(button=self.dispatch_mission_rewards, task_class=DispatchMissionAcquireTask)
        self._create_task(button=self.enhance_potential_button, task_class=EnhancePotentialTask)
        self._create_task(button=self.shadowland_button, task_class=ShadowlandAllFloorsTask)
