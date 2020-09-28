from PyQt5.QtWidgets import QListWidgetItem, QDialog, QToolButton, QMenu
from PyQt5.QtCore import Qt
import lib.gui.designes.queue_editor_window as design
from lib.gui.helper import set_default_icon, reset_player_and_logger

from lib.game.missions.legendary_battle import LegendaryBattle
from lib.game.missions.alliance_battles import AllianceBattles
from lib.game.missions.dimension_missions import DimensionMissions
from lib.game.missions.epic_quests import StupidXMen, MutualEnemy, BeginningOfTheChaos, DoomsDay, \
    TwistedWorld, TheBigTwin, VeiledSecret, TheFault, FateOfTheUniverse, DangerousSisters, CosmicRider, QuantumPower, \
    WingsOfDarkness, InhumanPrincess, MeanAndGreen, ClobberinTime, Hothead, AwManThisGuy, DominoFalls, GoingRogue, \
    FriendsAndEnemies, WeatheringTheStorm, Blindsided, DarkAdvent, IncreasingDarkness, RoadToMonastery, \
    MysteriousAmbush, MonasteryInTrouble, PowerOfTheDark
from lib.game.missions.coop import CoopPlay
from lib.game.missions.danger_room import DangerRoom
from lib.game.missions.timeline import TimelineBattle
from lib.game.missions.invasion import WorldBossInvasion
from lib.game.missions.squad_battles import SquadBattles
from lib.game.missions.world_bosses import WorldBosses
import lib.logger as logging

logger = logging.get_logger(__name__)


class QueueItem(QListWidgetItem):
    """Class for working with queue item as a widget."""

    def __init__(self, func, parameters, mode_name, mode_name_formatted=None):
        """Class initialization.

        :param func: function to execute in queue.
        :param parameters: function's parameters.
        :param str mode_name: name of game mode.
        """
        super().__init__()
        self.func = func
        self.parameters = parameters
        self.mode_name = mode_name
        self.mode_name_formatted = mode_name_formatted if mode_name_formatted else mode_name.title()
        self.setText(self.name)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Checked)
        self.setToolTip(self.name)

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
        additional_text = ''
        farm_bios = self.parameters.get("farm_shifter_bios")
        battle = self.parameters.get("battle")
        mission_mode = self.parameters.get("mode")
        times = self.parameters.get("times")
        if farm_bios:
            additional_text += " [Bio]"
        if battle:
            additional_text += f" [{battle.replace('_', ' ').title()}]"
        if mission_mode:
            additional_text += f" [{mission_mode.replace('_', ' ').title()}]"
        if times:
            additional_text += f" [{times} stages]"
        else:
            additional_text += " [All stages]"
        return f"{self.mode_name.title()} -{additional_text}"


class QueueItemEditor(QDialog, design.Ui_Dialog):
    """Class for working with editing elements of queue list."""

    UNAVAILABLE_MODES = ["SHADOWLAND", "WORLD EVENT"]  # unrealized game modes

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        """
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        set_default_icon(window=self)
        self.game = game
        self.setWindowModality(Qt.ApplicationModal)
        dimensions_missions = _DimensionMissions(game)
        legendary_battles = _LegendaryBattle(game)
        squad_battles = _SquadBattles(game)
        world_boss = _WorldBosses(game)
        timeline_battle = _TimelineBattle(game)
        danger_room = _DangerRoom(game)
        alliance_battle = _AllianceBattle(game)
        coop_play = _CoopPlay(game)
        world_boss_invastion = _WorldBossInvasion(game)
        fate_of_the_universe = _FateOfTheUniverse(game)
        the_fault = _TheFault(game)
        dangerous_sisters = _DangerousSisters(game)
        cosmic_rider = _CosmicRider(game)
        quantum_power = _QuantumPower(game)
        wings_of_darkness = _WingsOfDarkness(game)
        dooms_day = _DoomsDay(game)
        twisted_world = _TwistedWorld(game)
        inhuman_princess = _InhumanPrincess(game)
        mean_and_green = _MeanAndGreen(game)
        clobbering_time = _ClobberinTime(game)
        hothead = _Hothead(game)
        beginning_of_the_chaos = _BeginningOfTheChaos(game)
        stupid_x_men = _StupidXMen(game)
        the_big_twin = _TheBigTwin(game)
        aw_man_this_guy = _AwManThisGuy(game)
        domino_falls = _DominoFalls(game)
        mutual_enemy = _MutualEnemy(game)
        veiled_secret = _VeiledSecret(game)
        going_rogue = _GoingRogue(game)
        friends_and_enemies = _FriendsAndEnemies(game)
        weathering_the_storm = _WeatheringTheStorm(game)
        blindsided = _Blindsided(game)
        dark_advent = _DarkAdvent(game)
        increasing_darkness = _IncreasingDarkness(game)
        road_to_monastery = _RoadToMonastery(game)
        mysterious_ambush = _MysteriousAmbush(game)
        monastery_in_trouble = _MonasteryInTrouble(game)
        power_of_the_dark = _PowerOfTheDark(game)
        self.modes = [dooms_day, beginning_of_the_chaos, mutual_enemy, fate_of_the_universe,
                      twisted_world, stupid_x_men, the_big_twin, veiled_secret, the_fault,
                      coop_play, timeline_battle, legendary_battles, squad_battles,
                      alliance_battle, world_boss, dimensions_missions, world_boss_invastion,
                      danger_room, dangerous_sisters, cosmic_rider, quantum_power, wings_of_darkness, inhuman_princess,
                      mean_and_green, clobbering_time, hothead, aw_man_this_guy, domino_falls, going_rogue,
                      friends_and_enemies, weathering_the_storm, blindsided, dark_advent, increasing_darkness,
                      road_to_monastery, mysterious_ambush, monastery_in_trouble, power_of_the_dark]
        self.mode_names = [mode.mode_name for mode in self.modes]
        self.queue_item = None
        self.current_mode = None
        self.all_stages_check_box.stateChanged.connect(self.all_stages_changed)
        self.editor_button_box.accepted.connect(self.render_queue_item)

        menu_dict = {
            "EPIC QUESTS": {
                "GALACTIC IMPERATIVE": [fate_of_the_universe, the_fault, dangerous_sisters, cosmic_rider, quantum_power,
                                        wings_of_darkness],
                "FIRST FAMILY": [dooms_day, twisted_world, inhuman_princess, mean_and_green, clobbering_time, hothead],
                "X-FORCE": [beginning_of_the_chaos, stupid_x_men, the_big_twin, aw_man_this_guy, domino_falls],
                "RISE OF THE X-MEN": [mutual_enemy, veiled_secret, going_rogue, friends_and_enemies,
                                      weathering_the_storm, blindsided],
                "SORCERER SUPREME": [dark_advent, increasing_darkness, road_to_monastery, mysterious_ambush,
                                     monastery_in_trouble, power_of_the_dark]
            },
            "DIMENSION MISSION": dimensions_missions,
            "LEGENDARY BATTLE": legendary_battles,
            "SQUAD BATTLE": squad_battles,
            "WORLD BOSS": world_boss,
            "TIMELINE BATTLE": timeline_battle,
            "DANGER ROOM": danger_room,
            "ALLIANCE BATTLE": alliance_battle,
            "CO-OP PLAY": coop_play,
            "WORLD BOSS INVASION": world_boss_invastion
        }

        menu = QMenu()
        self.populate_menu(menu=menu, dictionary=menu_dict)
        self.select_mode_tool_button.setPopupMode(QToolButton.InstantPopup)
        self.select_mode_tool_button.setMenu(menu)
        hide_all = GameMode.ModeSettings()
        hide_all.all_stages = False
        self.set_visibility_to_all_elements(hide_all)

    def select_mode(self, mode):
        """Select GameMode from Tool Button Selector."""
        self.select_mode_tool_button.setText(mode.mode_name)
        self.current_mode = mode
        self.set_visibility_to_all_elements(self.current_mode.mode_settings)
        self.set_values_to_all_elements(self.current_mode.item_settings)
        if self.current_mode.mode_settings.mission_modes:
            self.mission_mode_combo_box.clear()
            self.mission_mode_combo_box.addItems(self.current_mode.mode_settings.mission_modes)
        if self.current_mode.mode_settings.legendary_battles:
            self.legendary_battle_combo_box.clear()
            self.legendary_battle_combo_box.addItems(self.current_mode.mode_settings.legendary_battles)
        if self.current_mode.mode_settings.legendary_battle_stages:
            self.legendary_battle_stage_combo_box.clear()
            self.legendary_battle_stage_combo_box.addItems(self.current_mode.mode_settings.legendary_battle_stages)

    def populate_menu(self, menu, dictionary):
        """Populate Selector's menu with dictionary of game modes.

        :param menu: menu to populate.
        :param dictionary: dictionary of game modes.
        """
        def add_mode_to_menu(menu_obj, mode):
            action = menu_obj.addAction(mode.mode_name_formatted)
            action.triggered.connect(lambda: self.select_mode(mode))

        for menu_key, menu_val in dictionary.items():
            if isinstance(menu_val, list):
                sub_menu = menu.addMenu(menu_key)
                for value in menu_val:
                    if isinstance(value, GameMode):
                        add_mode_to_menu(sub_menu, value)
            if isinstance(menu_val, dict):
                sub_menu = menu.addMenu(menu_key)
                self.populate_menu(sub_menu, menu_val)
            if isinstance(menu_val, GameMode):
                add_mode_to_menu(menu, menu_val)

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
            editor.select_mode(editor.current_mode)
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
        self.farm_bios_check_box.setEnabled(self.game.player.restartable and mode_settings.farm_bios)
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
        self.legendary_battle_label.setVisible(bool(mode_settings.legendary_battles))
        self.legendary_battle_label.setEnabled(bool(mode_settings.legendary_battles))
        self.legendary_battle_combo_box.setVisible(bool(mode_settings.legendary_battles))
        self.legendary_battle_combo_box.setEnabled(bool(mode_settings.legendary_battles))
        self.legendary_battle_stage_label.setVisible(bool(mode_settings.legendary_battle_stages))
        self.legendary_battle_stage_label.setEnabled(bool(mode_settings.legendary_battle_stages))
        self.legendary_battle_stage_combo_box.setVisible(bool(mode_settings.legendary_battle_stages))
        self.legendary_battle_stage_combo_box.setEnabled(bool(mode_settings.legendary_battle_stages))

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
        if item_settings.legendary_battles:
            self.legendary_battle_combo_box.setCurrentText(item_settings.legendary_battles)
        if item_settings.legendary_battle_stages:
            self.legendary_battle_stage_combo_box.setCurrentText(item_settings.legendary_battle_stages)
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
        legendary_battles = self.legendary_battle_combo_box.currentText() if mode_settings.legendary_battles else None
        legendary_battle_stages = self.legendary_battle_stage_combo_box.currentText() \
            if mode_settings.legendary_battle_stages else None
        return all_stages, stages_num, farm_bios, zero_boosts, difficulty, use_hidden_tickets, acquire_rewards, \
               mission_mode, skip_opponent_count, legendary_battles, legendary_battle_stages

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
        self.queue_item = QueueItem(func=item, parameters=settings, mode_name=mode.mode_name,
                                    mode_name_formatted=mode.mode_name_formatted)
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
            self.legendary_battles = []
            self.legendary_battle_stages = []

    class QueueItemSettings:
        """Class for working with customizable settings from GUI."""

        def __init__(self, all_stages=None, stages_num=None, farm_bios=None, zero_boosts_stop=None, difficulty=None,
                     use_hidden_tickets=None, acquire_rewards=None, mission_mode=None, skip_opponent_count=None,
                     legendary_battles=None, legendary_battle_stages=None):
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
            self.legendary_battles = legendary_battles
            self.legendary_battle_stages = legendary_battle_stages

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
            legendary_battles = item_settings.get("battle")
            legendary_battle_stages = item_settings.get("stage")
            return GameMode.QueueItemSettings(all_stages=all_stages, stages_num=stages_num, farm_bios=farm_bios,
                                              zero_boosts_stop=zero_boosts_stop, difficulty=difficulty,
                                              use_hidden_tickets=use_hidden_tickets, acquire_rewards=acquire_rewards,
                                              mission_mode=mission_mode, skip_opponent_count=skip_opponent_count,
                                              legendary_battles=legendary_battles,
                                              legendary_battle_stages=legendary_battle_stages)

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
            if self.legendary_battles:
                params.update({"battle": self.legendary_battles})
            if self.legendary_battle_stages:
                params.update({"stage": self.legendary_battle_stages})
            return params

    def __init__(self, game, mode_name, mode_module, mode_name_formatted=None):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        :param str mode_name: name of mode.
        :param mode_module: class or module of game mode.
        """
        self.game = game
        self.mode_name = mode_name
        self.mode_module = mode_module
        self.mode_name_formatted = mode_name_formatted if mode_name_formatted else mode_name.title()
        self.mode_settings = GameMode.ModeSettings()
        self.item_settings = GameMode.QueueItemSettings()

    def render(self):
        """Render function and settings for game mode."""
        game_mode = self.mode_module(self.game)

        @reset_player_and_logger(game=self.game)
        def do_missions(*args, **kwargs):
            return game_mode.do_missions(*args, **kwargs)

        return do_missions, self.item_settings.render()


class _LegendaryBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "LEGENDARY BATTLE", LegendaryBattle)
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.mission_modes = [LegendaryBattle.MODE.NORMAL, LegendaryBattle.MODE.EXTREME]
        self.mode_settings.legendary_battles = [LegendaryBattle.THOR_RAGNAROK, LegendaryBattle.BLACK_PANTHER,
                                                LegendaryBattle.INFINITY_WAR, LegendaryBattle.ANT_MAN,
                                                LegendaryBattle.CAPTAIN_MARVEL]
        self.mode_settings.legendary_battle_stages = [LegendaryBattle.STAGE.BATTLE_1, LegendaryBattle.STAGE.BATTLE_2,
                                                      LegendaryBattle.STAGE.BATTLE_3]


class _VeiledSecret(GameMode):

    def __init__(self, game):
        super().__init__(game, "VEILED SECRET", VeiledSecret, "Veiled Secret [Feathers/Crystals]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.zero_boosts_stop = True


class _MutualEnemy(GameMode):

    def __init__(self, game):
        super().__init__(game, "MUTUAL ENEMY", MutualEnemy, "Mutual Enemy [Magneto]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _StupidXMen(GameMode):

    def __init__(self, game):
        super().__init__(game, "STUPID X-MEN", StupidXMen, "Stupid X-Men [Colossus]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _TheBigTwin(GameMode):

    def __init__(self, game):
        super().__init__(game, "THE BIG TWIN", TheBigTwin, "The Big Twin [Feathers/Crystals]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.zero_boosts_stop = True


class _BeginningOfTheChaos(GameMode):

    def __init__(self, game):
        super().__init__(game, "BEGINNING OF THE CHAOS", BeginningOfTheChaos, "Beginning Of The Chaos [Psylocke]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _TwistedWorld(GameMode):

    def __init__(self, game):
        super().__init__(game, "TWISTED WORLD", TwistedWorld, "Twisted World [Victorious]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _DoomsDay(GameMode):

    def __init__(self, game):
        super().__init__(game, "DOOM'S DAY", DoomsDay, "Doom's Day [Invisible Woman]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _TheFault(GameMode):

    def __init__(self, game):
        super().__init__(game, "THE FAULT", TheFault, "The Fault [Phyla-Vell]")
        self.mode_settings.all_stages = True
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True
        self.mode_settings.zero_boosts_stop = True


class _FateOfTheUniverse(GameMode):

    def __init__(self, game):
        super().__init__(game, "FATE OF THE UNIVERSE", FateOfTheUniverse, "Fate Of The Universe [Nova]")
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


class _DangerousSisters(GameMode):

    def __init__(self, game):
        super().__init__(game, "DANGEROUS SISTERS", DangerousSisters, "Dangerous Sisters [Nebula]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True


class _CosmicRider(GameMode):

    def __init__(self, game):
        super().__init__(game, "COSMIC RIDER", CosmicRider, "Cosmic Rider [Punisher]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True


class _QuantumPower(GameMode):

    def __init__(self, game):
        super().__init__(game, "QUANTUM POWER", QuantumPower, "Quantum Power [Gamora]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _WingsOfDarkness(GameMode):

    def __init__(self, game):
        super().__init__(game, "WINGS OF DARKNESS", WingsOfDarkness, "Wings Of Darkness [Darkhawk]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _InhumanPrincess(GameMode):

    def __init__(self, game):
        super().__init__(game, "INHUMAN PRINCESS", InhumanPrincess, "Inhuman Princess [Crystal]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True


class _MeanAndGreen(GameMode):

    def __init__(self, game):
        super().__init__(game, "MEAN AND GREEN", MeanAndGreen, "Mean And Green [She-Hulk]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True


class _ClobberinTime(GameMode):

    def __init__(self, game):
        super().__init__(game, "CLOBBERIN TIME", ClobberinTime, "Clobberin Time [Thing]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _Hothead(GameMode):

    def __init__(self, game):
        super().__init__(game, "HOTHEAD", Hothead, "Hothead [Human Torch]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _AwManThisGuy(GameMode):

    def __init__(self, game):
        super().__init__(game, "AW MAN THIS GUY", AwManThisGuy, "Aw, Man. This Guy? [Fantomex]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _DominoFalls(GameMode):

    def __init__(self, game):
        super().__init__(game, "DOMINO FALLS", DominoFalls, "Domino Falls [Domino]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _GoingRogue(GameMode):

    def __init__(self, game):
        super().__init__(game, "GOING ROGUE", GoingRogue, "Going Rogue [Rogue]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _FriendsAndEnemies(GameMode):

    def __init__(self, game):
        super().__init__(game, "FRIENDS AND ENEMIES", FriendsAndEnemies, "Friends And Enemies [Beast]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _WeatheringTheStorm(GameMode):

    def __init__(self, game):
        super().__init__(game, "WEATHERING THE STORM", WeatheringTheStorm, "Weathering The Storm [Storm]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _Blindsided(GameMode):

    def __init__(self, game):
        super().__init__(game, "BLINDSIDED", Blindsided, "Blindsided [Cyclops]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True


class _DarkAdvent(GameMode):

    def __init__(self, game):
        super().__init__(game, "DARK ADVENT", DarkAdvent, "Dark Advent [Satana/Cleo]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.farm_bios = True


class _IncreasingDarkness(GameMode):

    def __init__(self, game):
        super().__init__(game, "INCREASING DARKNESS", IncreasingDarkness, "Increasing Darkness [Hellstorm/Cleo]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True


class _RoadToMonastery(GameMode):

    def __init__(self, game):
        super().__init__(game, "ROAD TO MONASTERY", RoadToMonastery, "Road To Monastery [Baron Mordo]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _MysteriousAmbush(GameMode):

    def __init__(self, game):
        super().__init__(game, "MYSTERIOUS AMBUSH", MysteriousAmbush, "Mysterious Ambush [Wong]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _MonasteryInTrouble(GameMode):

    def __init__(self, game):
        super().__init__(game, "MONASTERY IN TROUBLE", MonasteryInTrouble, "Monastery In Trouble [Ancient One]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True


class _PowerOfTheDark(GameMode):

    def __init__(self, game):
        super().__init__(game, "POWER OF THE DARK", PowerOfTheDark, "Power Of The Dark [Kaecilius]")
        self.mode_settings.all_stages = False
        self.mode_settings.stages = True
        self.mode_settings.difficulty = True
