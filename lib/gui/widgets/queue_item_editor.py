from PyQt5.QtWidgets import QListWidgetItem, QDialog
from PyQt5.QtCore import Qt
import lib.gui.designes.queue_editor_window as design
from lib.gui.helper import set_default_icon

from lib.game.missions.legendary_battle import LegendaryBattle
from lib.game.missions.alliance_battles import AllianceBattles
from lib.game.missions.dimension_missions import DimensionMissions
from lib.game.missions.epic_quests import StupidXMen, MutualEnemy, BeginningOfTheChaos, DoomsDay, \
    TwistedWorld, TheBigTwin, VeiledSecret, TheFault, FateOfTheUniverse
from lib.game.missions.coop import CoopPlay
from lib.game.missions.danger_room import DangerRoom
from lib.game.missions.timeline import TimelineBattle
from lib.game.missions.invasion import WorldBossInvasion
from lib.game.missions.squad_battles import SquadBattles
from lib.game.missions.world_bosses import WorldBosses
from lib.game.ui import load_game_modes
import lib.logger as logging

logger = logging.get_logger(__name__)


class QueueItem(QListWidgetItem):
    """Class for working with queue item as a widget."""

    def __init__(self, func, parameters, mode_name):
        """Class initialization.

        :param func: function to execute in queue.
        :param parameters: function's parameters.
        :param str mode_name: name of game mode.
        """
        super().__init__()
        self.func = func
        self.parameters = parameters
        self.mode_name = mode_name
        self.setText(self.name)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Checked)

    def get_executor(self):
        """Get function with parameters to execute."""
        if self.is_checked:
            return self.func, self.parameters
        return None, None

    @property
    def is_checked(self):
        """Is item checked to execute."""
        return self.checkState() == Qt.Checked

    def set_checked(self, checked=True):
        """Set checked state to item."""
        state = Qt.Checked if checked else Qt.Unchecked
        self.setCheckState(state)

    @property
    def name(self):
        """Get queue item's name for GUI."""
        additional_text = ' '
        mission_mode = self.parameters.get("mode")
        times = self.parameters.get("times")
        if mission_mode:
            additional_text += f"({mission_mode} mode)"
        if times:
            additional_text += f"({times} times)"
        else:
            additional_text += "(all available)"
        return f"{self.mode_name}{additional_text}"


class QueueItemEditor(QDialog, design.Ui_Dialog):
    """Class for working with editing elements of queue list."""

    UNAVAILABLE_MODES = ["SHADOWLAND", "WORLD EVENT"]  # unrealized game modes

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        """
        super().__init__()
        self.setupUi(self)
        set_default_icon(window=self)
        self.game = game
        self.setWindowModality(Qt.ApplicationModal)
        self.modes = [_DoomsDay(game), _BeginningOfTheChaos(game), _MutualEnemy(game), _FateOfTheUniverse(game),
                      _TwistedWorld(game), _StupidXMen(game), _TheBigTwin(game), _VeiledSecret(game), _TheFault(game),
                      _CoopPlay(game), _TimelineBattle(game), _LegendaryBattle(game), _SquadBattles(game),
                      _AllianceBattle(game), _WorldBosses(game), _DimensionMissions(game), _WorldBossInvasion(game),
                      _DangerRoom(game)]
        self.mode_names = [mode.mode_name for mode in self.modes]
        self.loaded_modes = [mode for mode in load_game_modes() if mode not in self.UNAVAILABLE_MODES]
        if len(self.modes) != len(self.loaded_modes) + 1:
            logger.error("Length of loaded modes isn't equal manual setup modes.")
        self.queue_item = None
        self.current_mode = None
        self.on_startup()
        self.mode_combo_box.currentTextChanged.connect(self.mode_combo_box_changed)
        self.all_stages_check_box.stateChanged.connect(self.all_stages_changed)
        self.editor_button_box.accepted.connect(self.render_queue_item)

    @staticmethod
    def from_result_item(game, queue_item):
        """Create editor from queue item.

        :param lib.game.game.Game game: instance of game.
        :param QueueItem queue_item: queue item.
        """
        editor = QueueItemEditor(game)
        editor.queue_item = queue_item
        mode = [mode for mode in editor.modes if mode.mode_name == queue_item.mode_name]
        if mode:
            editor.current_mode = mode[0]
            editor.current_mode.item_settings = GameMode.QueueItemSettings.from_settings(queue_item.parameters)
            editor.mode_combo_box.setCurrentText(editor.current_mode.mode_name)
            editor.mode_combo_box_changed()
            editor.set_values_to_all_elements(editor.current_mode.item_settings)
            return editor
        logger.error(f"Error during creating Item Editor from item instance for mode: {queue_item.mode_name}.")

    @staticmethod
    def from_settings(game, settings):
        """Create editor from JSON-settings similar to 'GameMode.QueueItemSettings'.

        :param lib.game.game.Game game: instance of game.
        :param dict settings: dictionary of settings.
        """
        editor = QueueItemEditor(game)
        mode = [mode for mode in editor.modes if mode.mode_name == settings.get("mode_name")]
        if mode:
            editor.current_mode = mode[0]
            editor.current_mode.item_settings = GameMode.QueueItemSettings.from_settings(settings)
            editor.set_values_to_all_elements(editor.current_mode.item_settings)
            return editor
        logger.error(f"Error during creating Item Editor from item instance with settings: {settings}.")

    def on_startup(self):
        """Update values of GUI elements on startup."""
        self.mode_combo_box.clear()
        self.mode_combo_box.addItems(self.mode_names)
        self.mode_combo_box_changed()
        self.all_stages_changed()

    def mode_combo_box_changed(self):
        """'Game mode' combobox event when value is changed."""
        text = self.mode_combo_box.currentText()
        mode = [mode for mode in self.modes if mode.mode_name == text]
        if mode:
            self.current_mode = mode[0]
            self.set_visibility_to_all_elements(self.current_mode.mode_settings)
            self.set_values_to_all_elements(self.current_mode.item_settings)
            if self.current_mode.mode_settings.mission_modes:
                self.mission_mode_combo_box.clear()
                self.mission_mode_combo_box.addItems(self.current_mode.mode_settings.mission_modes)

    def set_visibility_to_all_elements(self, mode_settings):
        """Set visibility to all GUI elements by game mode.

        :param GameMode.ModeSettings mode_settings: settings of game mode.
        """
        self.all_stages_check_box.setVisible(mode_settings.all_stages)
        self.all_stages_check_box.setEnabled(mode_settings.all_stages)
        self.stages_label.setVisible(mode_settings.stages)
        self.stages_label.setEnabled(mode_settings.stages)
        self.stages_spin_box.setVisible(mode_settings.stages)
        self.stages_spin_box.setEnabled(mode_settings.stages)
        self.farm_bios_check_box.setVisible(mode_settings.farm_bios)
        self.farm_bios_check_box.setEnabled(mode_settings.farm_bios)
        # TODO: add ability to stop missions
        # self.zero_boosts_check_box.setVisible(mode_settings.zero_boosts_stop)
        # self.zero_boosts_check_box.setEnabled(mode_settings.zero_boosts_stop)
        self.zero_boosts_check_box.setVisible(False)
        self.zero_boosts_check_box.setEnabled(False)
        self.difficulty_label.setVisible(mode_settings.difficulty)
        self.difficulty_label.setEnabled(mode_settings.difficulty)
        self.difficulty_spin_box.setVisible(mode_settings.difficulty)
        self.difficulty_spin_box.setEnabled(mode_settings.difficulty)
        self.use_hidden_tickets_checkbox.setVisible(mode_settings.use_hidden_tickets)
        self.use_hidden_tickets_checkbox.setEnabled(mode_settings.use_hidden_tickets)
        self.dm_acquire_rewards_checkbox.setVisible(mode_settings.acquire_rewards)
        self.dm_acquire_rewards_checkbox.setEnabled(mode_settings.acquire_rewards)
        self.mission_mode_label.setVisible(bool(mode_settings.mission_modes))
        self.mission_mode_combo_box.setEnabled(bool(mode_settings.mission_modes))
        self.mission_mode_combo_box.setVisible(bool(mode_settings.mission_modes))
        self.mission_mode_label.setEnabled(bool(mode_settings.mission_modes))
        self.timeline_skip_label.setVisible(mode_settings.skip_opponents)
        self.timeline_skip_label.setEnabled(mode_settings.skip_opponents)
        self.timeline_skip_combobox.setVisible(mode_settings.skip_opponents)
        self.timeline_skip_combobox.setEnabled(mode_settings.skip_opponents)

    def set_values_to_all_elements(self, item_settings):
        """Set value to all GUI elements by queue item.

        :param GameMode.QueueItemSettings item_settings: settings of queue item.
        """
        if item_settings.all_stages:
            self.all_stages_check_box.setChecked(item_settings.all_stages)
        if item_settings.stages_num:
            self.stages_spin_box.setValue(item_settings.stages_num)
            self.all_stages_check_box.setChecked(False)
        if item_settings.farm_bios:
            self.farm_bios_check_box.setChecked(item_settings.farm_bios)
        if item_settings.zero_boosts_stop:
            self.zero_boosts_check_box.setChecked(item_settings.zero_boosts_stop)
        if item_settings.difficulty:
            self.difficulty_spin_box.setValue(item_settings.difficulty)
        if item_settings.use_hidden_tickets:
            self.use_hidden_tickets_checkbox.setChecked(item_settings.use_hidden_tickets)
        if item_settings.acquire_rewards:
            self.dm_acquire_rewards_checkbox.setChecked(item_settings.acquire_rewards)
        if item_settings.mission_mode:
            self.mission_mode_combo_box.setCurrentText(item_settings.mission_mode)
        if item_settings.skip_opponent_count:
            self.timeline_skip_combobox.setValue(item_settings.skip_opponent_count)
        self.all_stages_changed()

    def all_stages_changed(self):
        """'All stages' checkbox event when value is changed"""
        if self.current_mode.mode_settings.all_stages:
            checked = self.all_stages_check_box.isChecked()
            self.stages_label.setEnabled(not checked)
            self.stages_spin_box.setEnabled(not checked)

    def get_setting_values(self, mode_settings):
        """Retrieve settings from GUI elements according to available game mode's settings.

        :param GameMode.ModeSettings mode_settings: game mode's settings.
        """
        all_stages = self.all_stages_check_box.isChecked() if mode_settings.all_stages else None
        farm_bios = self.farm_bios_check_box.isChecked() if mode_settings.farm_bios else None
        zero_boosts = self.zero_boosts_check_box.isChecked() if mode_settings.zero_boosts_stop else None
        stages_num = self.stages_spin_box.value() if mode_settings.stages and not all_stages else None
        difficulty = self.difficulty_spin_box.value() if mode_settings.difficulty else None
        use_hidden_tickets = self.use_hidden_tickets_checkbox.isChecked() if mode_settings.use_hidden_tickets else None
        acquire_rewards = self.dm_acquire_rewards_checkbox.isChecked() if mode_settings.acquire_rewards else None
        mission_mode = self.mission_mode_combo_box.currentText() if mode_settings.mission_modes else None
        skip_opponent_count = self.timeline_skip_combobox.value() if mode_settings.skip_opponents else None
        return all_stages, stages_num, farm_bios, zero_boosts, difficulty, use_hidden_tickets, acquire_rewards, \
               mission_mode, skip_opponent_count

    def render_queue_item(self):
        """Render queue item."""
        if self.current_mode:
            item_settings = self.get_setting_values(self.current_mode.mode_settings)
            self.current_mode.item_settings = GameMode.QueueItemSettings(*item_settings)
            return self.render_mode(mode=self.current_mode)
        else:
            logger.error("No mode was selected somehow.")

    def render_mode(self, mode):
        """Render game mode.

        :param GameMode mode: game mode.
        """
        item, settings = mode.render()
        self.queue_item = QueueItem(func=item, parameters=settings, mode_name=mode.mode_name)
        return self.queue_item


class GameMode:
    """Class for working with game mode settings."""

    class ModeSettings:
        """Class for working with available settings for a game mode."""

        def __init__(self):
            """Class initialization."""
            self.all_stages = True
            self.stages = False
            self.farm_bios = False
            self.zero_boosts_stop = False
            self.difficulty = False
            self.use_hidden_tickets = False
            self.acquire_rewards = False
            self.mission_modes = []
            self.skip_opponents = False

    class QueueItemSettings:
        """Class for working with customizable settings from GUI."""

        def __init__(self, all_stages=None, stages_num=None, farm_bios=None, zero_boosts_stop=None, difficulty=None,
                     use_hidden_tickets=None, acquire_rewards=None, mission_mode=None, skip_opponent_count=None):
            """Class initialization."""
            self.all_stages = all_stages
            self.stages_num = stages_num
            self.farm_bios = farm_bios
            self.zero_boosts_stop = zero_boosts_stop
            self.difficulty = difficulty
            self.use_hidden_tickets = use_hidden_tickets
            self.acquire_rewards = acquire_rewards
            self.mission_mode = mission_mode
            self.skip_opponent_count = skip_opponent_count

        @staticmethod
        def from_settings(item_settings):
            """Create instance of 'QueueItemSettings' from settings.

            :param dict item_settings: dictionary of settings.
            """
            stages_num = item_settings.get("times")
            all_stages = True if not stages_num else None
            farm_bios = item_settings.get("farm_shifter_bios")
            zero_boosts_stop = None  # TODO: add ability to stop missions
            difficulty = item_settings.get("difficulty")
            use_hidden_tickets = item_settings.get("use_hidden_tickets")
            acquire_rewards = item_settings.get("acquire_rewards")
            mission_mode = item_settings.get("mode")
            skip_opponent_count = item_settings.get("skip_opponent_count")
            return GameMode.QueueItemSettings(all_stages=all_stages, stages_num=stages_num, farm_bios=farm_bios,
                                              zero_boosts_stop=zero_boosts_stop, difficulty=difficulty,
                                              use_hidden_tickets=use_hidden_tickets, acquire_rewards=acquire_rewards,
                                              mission_mode=mission_mode, skip_opponent_count=skip_opponent_count)

        def render(self):
            """Render settings for game mode."""
            params = {}
            if not self.all_stages and self.stages_num:
                params.update({"times": self.stages_num})
            if self.farm_bios:
                params.update({"farm_shifter_bios": self.farm_bios})
            if self.mission_mode:
                params.update({"mode": self.mission_mode})
            if self.difficulty:
                params.update({"difficulty": self.difficulty})
            if self.use_hidden_tickets:
                params.update({"use_hidden_tickets": self.use_hidden_tickets})
            if self.acquire_rewards:
                params.update({"acquire_rewards": self.acquire_rewards})
            if self.zero_boosts_stop:
                # TODO: add ability to stop missions
                pass
            if self.skip_opponent_count:
                params.update({"skip_opponent_count": self.skip_opponent_count})
            return params

    def __init__(self, game, mode_name, mode_module):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        :param str mode_name: name of mode.
        :param mode_module: class or module of game mode.
        """
        self.game = game
        self.mode_name = mode_name
        self.mode_module = mode_module
        self.mode_settings = GameMode.ModeSettings()
        self.item_settings = GameMode.QueueItemSettings()

    def render(self):
        """Render function and settings for game mode."""
        game_mode = self.mode_module(self.game)

        def do_missions(*args, **kwargs):
            # Screen will never unlock itself inside side-process
            game_mode.player.screen_locked = False
            return game_mode.do_missions(*args, **kwargs)

        return do_missions, self.item_settings.render()


class _LegendaryBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "LEGENDARY BATTLE", LegendaryBattle)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True


class _VeiledSecret(GameMode):

    def __init__(self, game):
        super().__init__(game, "VEILED SECRET", VeiledSecret)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.zero_boosts_stop = True


class _MutualEnemy(GameMode):

    def __init__(self, game):
        super().__init__(game, "MUTUAL ENEMY", MutualEnemy)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _StupidXMen(GameMode):

    def __init__(self, game):
        super().__init__(game, "STUPID X-MEN", StupidXMen)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _TheBigTwin(GameMode):

    def __init__(self, game):
        super().__init__(game, "THE BIG TWIN", TheBigTwin)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.zero_boosts_stop = True


class _BeginningOfTheChaos(GameMode):

    def __init__(self, game):
        super().__init__(game, "BEGINNING OF THE CHAOS", BeginningOfTheChaos)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _TwistedWorld(GameMode):

    def __init__(self, game):
        super().__init__(game, "TWISTED WORLD", TwistedWorld)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _DoomsDay(GameMode):

    def __init__(self, game):
        super().__init__(game, "DOOM'S DAY", DoomsDay)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _TheFault(GameMode):

    def __init__(self, game):
        super().__init__(game, "THE FAULT", TheFault)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _FateOfTheUniverse(GameMode):

    def __init__(self, game):
        super().__init__(game, "FATE OF THE UNIVERSE", FateOfTheUniverse)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _CoopPlay(GameMode):

    def __init__(self, game):
        super().__init__(game, "CO-OP PLAY", CoopPlay)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True


class _AllianceBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "ALLIANCE BATTLE", AllianceBattles)
        self.mode_settings.all_stages = False
        self.mode_settings.mission_modes = [AllianceBattles.MODE.ALL_BATTLES, AllianceBattles.MODE.NORMAL]


class _TimelineBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "TIMELINE BATTLE", TimelineBattle)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.skip_opponents = True


class _WorldBosses(GameMode):

    def __init__(self, game):
        super().__init__(game, "WORLD BOSS", WorldBosses)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True
        self.mode_settings.mission_modes = [WorldBosses.MODE.ULTIMATE, WorldBosses.MODE.NORMAL,
                                            WorldBosses.MODE.BEGINNER]


class _DimensionMissions(GameMode):

    def __init__(self, game):
        super().__init__(game, "DIMENSION MISSION", DimensionMissions)
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.zero_boosts_stop = True
        self.mode_settings.difficulty = True
        self.mode_settings.use_hidden_tickets = True
        self.mode_settings.acquire_rewards = True


class _SquadBattles(GameMode):

    def __init__(self, game):
        super().__init__(game, "SQUAD BATTLE", SquadBattles)
        self.mode_settings.all_stages = False
        self.mode_settings.mission_modes = [SquadBattles.MODE.ALL_BATTLES, SquadBattles.MODE.DAILY_RANDOM]


class _WorldBossInvasion(GameMode):

    def __init__(self, game):
        super().__init__(game, "WORLD BOSS INVASION", WorldBossInvasion)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True


class _DangerRoom(GameMode):

    def __init__(self, game):
        super().__init__(game, "DANGER ROOM", DangerRoom)
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.mission_modes = [DangerRoom.MODE.NORMAL, DangerRoom.MODE.EXTREME]
