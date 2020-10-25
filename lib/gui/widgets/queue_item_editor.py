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
from lib.game.missions.world_boss_invasion import WorldBossInvasion
from lib.game.missions.squad_battles import SquadBattles
from lib.game.missions.world_bosses import WorldBosses
from lib.game.routines import DailyTrivia, ComicCards, CustomGear, ShieldLab, WaitUntil
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
        self.execution_parameters = self.clear_parameters()
        self.mode_name = mode_name
        self.mode_name_formatted = mode_name_formatted if mode_name_formatted else mode_name.title()
        self.setText(self.name)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Checked)
        self.setToolTip(self.name)

    def clear_parameters(self):
        parameters = self.parameters.copy()
        if "all_stages" in parameters.keys():
            if parameters["all_stages"] is True:
                parameters.pop("times")  # Remove `times` kwarg if doing All stages
            parameters.pop("all_stages")  # Remove `all_stages` kwarg anyway
        if "action" in parameters.keys():
            parameters.pop("action")
        return parameters

    def get_executor(self):
        """Get function with parameters to execute."""
        if self.is_checked:
            return self.func, self.execution_parameters
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
        if self.parameters.get("action"):
            return f"[Action] {self.mode_name.title()}"
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
        if times and not self.parameters.get("all_stages"):
            additional_text += f" [{times} stages]"
        else:
            additional_text += " [All stages]"
        return f"{self.mode_name.title()} -{additional_text}"


class QueueItemEditor(QDialog, design.Ui_Dialog):
    """Class for working with editing elements of queue list."""

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
        restart_game = _RestartGame(game)
        daily_trivia = _DailyTrivia(game)
        comic_cards = _ComicCards(game)
        custom_gear = _CustomGear(game)
        collect_antimatter = _CollectAntiMatter(game)
        wait_boost_points = _WaitBoostPoints(game)
        wait_max_energy = _WaitMaxEnergy(game)
        wait_daily_reset = _WaitDailyReset(game)
        self.actions = [restart_game, daily_trivia, comic_cards, custom_gear, collect_antimatter, wait_boost_points,
                        wait_max_energy, wait_daily_reset]
        self.modes = [dooms_day, beginning_of_the_chaos, mutual_enemy, fate_of_the_universe,
                      twisted_world, stupid_x_men, the_big_twin, veiled_secret, the_fault,
                      coop_play, timeline_battle, legendary_battles, squad_battles,
                      alliance_battle, world_boss, dimensions_missions, world_boss_invastion,
                      danger_room, dangerous_sisters, cosmic_rider, quantum_power, wings_of_darkness, inhuman_princess,
                      mean_and_green, clobbering_time, hothead, aw_man_this_guy, domino_falls, going_rogue,
                      friends_and_enemies, weathering_the_storm, blindsided, dark_advent, increasing_darkness,
                      road_to_monastery, mysterious_ambush, monastery_in_trouble, power_of_the_dark,
                      *self.actions]
        self.mode_names = [mode.mode_name for mode in self.modes]
        self.queue_item = None
        self.current_mode = None
        self.editor_button_box.accepted.connect(self.render_queue_item)

        menu_dict = {
            "[ACTIONS]": self.actions,
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

    def clear_form_layout(self):
        """Clear Form Layout from mode's GUI elements."""
        for i in range(self.formLayout.count()):
            from PyQt5.QtWidgets import QWidgetItem
            item = self.formLayout.itemAt(0)
            if isinstance(item, QWidgetItem):
                widget = item.widget()
                self.formLayout.removeWidget(widget)
                widget.setParent(None)

    def select_mode(self, mode):
        """Select GameMode from Tool Button Selector."""
        self.select_mode_tool_button.setText(mode.mode_name)
        self.current_mode = mode
        self.clear_form_layout()
        self.current_mode.render_gui_elements(parent_layout=self.formLayout)

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
            editor.select_mode(editor.current_mode)
            editor.current_mode.apply_params(queue_item.parameters)
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
            editor.current_mode.apply_params(settings)
            return editor
        logger.error(f"Error during creating Item Editor from item instance with settings: {settings}.")

    def render_queue_item(self):
        """Render queue item."""
        if self.current_mode:
            function, parameters = self.current_mode.render_executable()
            self.queue_item = QueueItem(func=function, parameters=parameters, mode_name=self.current_mode.mode_name,
                                        mode_name_formatted=self.current_mode.mode_name_formatted)
            return self.queue_item


class GameMode:
    """Class for working with game mode settings."""

    class ModeSetting:
        """Class for working with available settings for a game mode."""

        class Checkbox:

            def __init__(self, text, initial_state=True):
                from PyQt5.QtWidgets import QCheckBox
                self.widget = QCheckBox(text=text)
                self.widget.setCheckState(Qt.Checked if initial_state else Qt.Unchecked)

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                row_index = layout.rowCount()
                layout.setWidget(row_index, QFormLayout.LabelRole, self.widget)

            @property
            def value(self):
                return self.widget.isChecked()

            @value.setter
            def value(self, val):
                self.widget.setCheckState(Qt.Checked if val else Qt.Unchecked)

        class Spinbox:

            def __init__(self, text, initial_value=1, min=1, max=99):
                from PyQt5.QtWidgets import QSpinBox, QLabel
                self.widget_spinbox = QSpinBox()
                self.widget_label = QLabel(text=text)
                self.widget_spinbox.setMinimum(min)
                self.widget_spinbox.setMaximum(max)
                self.widget_spinbox.setValue(initial_value)

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                row_index = layout.rowCount()
                layout.setWidget(row_index, QFormLayout.LabelRole, self.widget_label)
                layout.setWidget(row_index, QFormLayout.SpanningRole, self.widget_spinbox)

            @property
            def value(self):
                return self.widget_spinbox.value()

            @value.setter
            def value(self, val):
                self.widget_spinbox.setValue(val)

        class Combobox:

            def __init__(self, text, values_dict):
                from PyQt5.QtWidgets import QComboBox, QLabel
                self.widget_combobox = QComboBox()
                self.widget_combobox.addItems(values_dict.keys())
                self.widget_label = QLabel(text=text)
                self.values_dict = values_dict

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                row_index = layout.rowCount()
                layout.setWidget(row_index, QFormLayout.LabelRole, self.widget_label)
                layout.setWidget(row_index, QFormLayout.SpanningRole, self.widget_combobox)

            @property
            def value(self):
                return self.values_dict[self.widget_combobox.currentText()]

            @value.setter
            def value(self, val):
                key = [k for k, v in self.values_dict.items() if v == val]
                self.widget_combobox.setCurrentText(key[0])

        def __init__(self, setting_type, setting_key, **kwargs):
            """Class initialization.

            :param setting_type: type of GUI element of setting.
            :param setting_key: setting's key (kwarg for game mode).
            :param kwargs: possible kwargs for GUI element of setting.
            """
            self.setting_type = setting_type
            self.setting_key = setting_key
            self.kwargs = kwargs
            self.gui_element = None
            self._value = None

        def render_gui(self):
            """Render GUI element of setting."""
            self.gui_element = self.setting_type(**self.kwargs)
            return self.gui_element

        @property
        def value(self):
            """Value of setting."""
            if self.gui_element:
                self._value = self.gui_element.value
            return {self.setting_key: self._value}

        @value.setter
        def value(self, value):
            """Set value of setting."""
            if not self.gui_element:
                self.render_gui()
            if value is not None:
                self._value = value
                self.gui_element.value = value

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
        self.mode_settings = []

    def render_executable(self):
        """Render function and settings for game mode."""
        game_mode = self.mode_module(self.game)

        @reset_player_and_logger(game=self.game)
        def do_missions(*args, **kwargs):
            return game_mode.do_missions(*args, **kwargs)

        return do_missions, self.render_execution_params()

    def render_gui_elements(self, parent_layout):
        """Render all GUI elements of all mode settings.

        :param parent_layout: parent layout for new created elements.
        """
        for setting in self.mode_settings:
            gui_element = setting.render_gui()
            gui_element.add_to_layout(layout=parent_layout)
            if setting.setting_key == "farm_shifter_bios" and not self.game.player.restartable:
                gui_element.widget.setEnabled(False)

        # Make "All stages" checkbox and "Stages" spinbox relatable
        all_stages = [setting.gui_element.widget for setting in self.mode_settings if
                      setting.setting_key == "all_stages"]
        stages = [(setting.gui_element.widget_label, setting.gui_element.widget_spinbox) for setting in
                  self.mode_settings if setting.setting_key == "times"]
        if all_stages and stages:
            all_stages_check_box, stages_label, stages_spin_box = all_stages[0], stages[0][0], stages[0][1]

            def all_stages_changed():
                """'All stages' checkbox event when value is changed"""
                checked = all_stages_check_box.isChecked()
                stages_label.setEnabled(not checked)
                stages_spin_box.setEnabled(not checked)

            all_stages_changed()
            all_stages_check_box.stateChanged.connect(all_stages_changed)

    def render_execution_params(self):
        """Returns execution parameters for game mode."""
        params = {}
        for setting in self.mode_settings:
            params.update(setting.value)
        return params

    def apply_params(self, params):
        """Apply parameters to mode's settings.

        :param params: dictionary of parameters.
        """
        for setting in self.mode_settings:
            if setting.setting_key in params.keys():
                setting.value = params[setting.setting_key]


class Action(GameMode):
    """Class for working with non-mission actions."""

    def __init__(self, game, action_name, action_executable):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        :param str action_name: name of action.
        :param action_executable: function to execute.
        """
        super().__init__(game, action_name, None)
        self.action_executable = action_executable

    def render_executable(self):
        """Render function and settings for action."""
        action_executable = self.action_executable  # Only function without class reference (GUI cannot be pickled)

        @reset_player_and_logger(game=self.game)
        def action(*args, **kwargs):
            return action_executable(*args, **kwargs)

        return action, {**self.render_execution_params(), "action": True}


class _RestartGame(Action):

    def __init__(self, game):
        super().__init__(game, "RESTART GAME", game.restart_game)


class _DailyTrivia(Action):

    def __init__(self, game):
        self.daily_trivia = DailyTrivia(game)
        super().__init__(game, "DAILY TRIVIA", self.daily_trivia.do_trivia)


class _ComicCards(Action):

    def __init__(self, game):
        self.comic_cards = ComicCards(game)
        super().__init__(game, "COMIC CARDS: UPGRADE ALL", self.comic_cards.upgrade_all_cards)


class _CustomGear(Action):

    def __init__(self, game):
        self.custom_gear = CustomGear(game)
        super().__init__(game, "CUSTOM GEAR: UPGRADE", self.custom_gear.quick_upgrade_gear)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many time to upgrade"))


class _CollectAntiMatter(Action):

    def __init__(self, game):
        self.shield_lab = ShieldLab(game)
        super().__init__(game, "SHIELD LAB: COLLECT ANTI-MATTER", self.shield_lab.collect_antimatter)


class _WaitBoostPoints(Action):

    def __init__(self, game):
        self.wait_until = WaitUntil(game)
        super().__init__(game, "WAIT FOR BOOST POINTS", self.wait_until.wait_until_boost_points)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="value",
                                                       text="Wait until boost points value is equal or greater than",
                                                       initial_value=100,
                                                       max=9999))


class _WaitMaxEnergy(Action):

    def __init__(self, game):
        self.wait_until = WaitUntil(game)
        super().__init__(game, "WAIT FOR MAX ENERGY", self.wait_until.wait_until_max_energy)


class _WaitDailyReset(Action):

    def __init__(self, game):
        self.wait_until = WaitUntil(game)
        super().__init__(game, "WAIT DAILY RESET", self.wait_until.wait_until_daily_reset)


class _LegendaryBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "LEGENDARY BATTLE", LegendaryBattle)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       setting_key="mode",
                                                       text="Select Legendary Battle mode",
                                                       values_dict={"Normal": LegendaryBattle.MODE.NORMAL,
                                                                    "Extreme": LegendaryBattle.MODE.EXTREME}))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       text="Select Legendary Battle",
                                                       setting_key="battle",
                                                       values_dict={"Thor: Ragnarok": LegendaryBattle.THOR_RAGNAROK,
                                                                    "Black Panther": LegendaryBattle.BLACK_PANTHER,
                                                                    "Infinity War": LegendaryBattle.INFINITY_WAR,
                                                                    "Ant-Man & The Wasp": LegendaryBattle.ANT_MAN,
                                                                    "Captain Marvel": LegendaryBattle.CAPTAIN_MARVEL}))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       text="Select Legendary Battle mission",
                                                       setting_key="stage",
                                                       values_dict={
                                                           "Battle #1": LegendaryBattle.STAGE.BATTLE_1,
                                                           "Battle #2": LegendaryBattle.STAGE.BATTLE_2,
                                                           "Battle #3": LegendaryBattle.STAGE.BATTLE_3
                                                       }))


class _VeiledSecret(GameMode):

    def __init__(self, game):
        super().__init__(game, "VEILED SECRET", VeiledSecret, "Veiled Secret [Feathers/Crystals]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=4))


class _MutualEnemy(GameMode):

    def __init__(self, game):
        super().__init__(game, "MUTUAL ENEMY", MutualEnemy, "Mutual Enemy [Magneto]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=2))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _StupidXMen(GameMode):

    def __init__(self, game):
        super().__init__(game, "STUPID X-MEN", StupidXMen, "Stupid X-Men [Colossus]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=6))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _TheBigTwin(GameMode):

    def __init__(self, game):
        super().__init__(game, "THE BIG TWIN", TheBigTwin, "The Big Twin [Feathers/Crystals]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=6))


class _BeginningOfTheChaos(GameMode):

    def __init__(self, game):
        super().__init__(game, "BEGINNING OF THE CHAOS", BeginningOfTheChaos, "Beginning Of The Chaos [Psylocke]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=2))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _TwistedWorld(GameMode):

    def __init__(self, game):
        super().__init__(game, "TWISTED WORLD", TwistedWorld, "Twisted World [Victorious]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=6))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _DoomsDay(GameMode):

    def __init__(self, game):
        super().__init__(game, "DOOM'S DAY", DoomsDay, "Doom's Day [Invisible Woman]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=2))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _TheFault(GameMode):

    def __init__(self, game):
        super().__init__(game, "THE FAULT", TheFault, "The Fault [Phyla-Vell]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=6))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _FateOfTheUniverse(GameMode):

    def __init__(self, game):
        super().__init__(game, "FATE OF THE UNIVERSE", FateOfTheUniverse, "Fate Of The Universe [Nova]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=2))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _CoopPlay(GameMode):

    def __init__(self, game):
        super().__init__(game, "CO-OP PLAY", CoopPlay)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=5))


class _AllianceBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "ALLIANCE BATTLE", AllianceBattles)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       setting_key="mode",
                                                       text="Select Alliance Battle mode",
                                                       values_dict={"All battles (Normal and Extreme)": AllianceBattles.MODE.ALL_BATTLES,
                                                                    "Only Normal battle": AllianceBattles.MODE.NORMAL}))


class _TimelineBattle(GameMode):

    def __init__(self, game):
        super().__init__(game, "TIMELINE BATTLE", TimelineBattle)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=10))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="skip_opponent_count",
                                                       text="Select how many opponents to skip before each battle",
                                                       min=0))


class _WorldBosses(GameMode):

    def __init__(self, game):
        super().__init__(game, "WORLD BOSS", WorldBosses)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All stages"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete",
                                                       min=1, max=5))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       setting_key="mode",
                                                       text="Select World Boss mode",
                                                       values_dict={"Beginner": WorldBosses.MODE.BEGINNER,
                                                                    "Normal": WorldBosses.MODE.NORMAL,
                                                                    "Ultimate": WorldBosses.MODE.ULTIMATE}))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       setting_key="boss",
                                                       text="Select World Boss",
                                                       values_dict={"Today's Boss": WorldBosses.BOSS.TODAYS_BOSS,
                                                                    "Proxima Midnight": WorldBosses.BOSS.PROXIMA_MIDNIGHT,
                                                                    "Black Dwarf": WorldBosses.BOSS.BLACK_DWARF,
                                                                    "Corvus Glaive": WorldBosses.BOSS.CORVUS_GLAIVE,
                                                                    "Supergiant": WorldBosses.BOSS.SUPERGIANT,
                                                                    "Ebony Maw": WorldBosses.BOSS.EBONY_MAW,
                                                                    "Thanos": WorldBosses.BOSS.THANOS,
                                                                    "Quicksilver": WorldBosses.BOSS.QUICKSILVER,
                                                                    "Cable": WorldBosses.BOSS.CABLE,
                                                                    "Scarlet Witch": WorldBosses.BOSS.SCARLET_WITCH,
                                                                    "Apocalypse": WorldBosses.BOSS.APOCALYPSE,
                                                                    }))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select World Boss stage difficulty",
                                                       min=1, max=99))


class _DimensionMissions(GameMode):

    def __init__(self, game):
        super().__init__(game, "DIMENSION MISSION", DimensionMissions)

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select Dimension Mission stage difficulty",
                                                       min=1, max=15))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="use_hidden_tickets",
                                                       text="Use Hidden Tickets for battle"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="acquire_rewards",
                                                       text="Acquire all contribution rewards at the end"))


class _SquadBattles(GameMode):

    def __init__(self, game):
        super().__init__(game, "SQUAD BATTLE", SquadBattles)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       setting_key="mode",
                                                       text="Select Squad Battle mode",
                                                       values_dict={"All battles": SquadBattles.MODE.ALL_BATTLES,
                                                                    "One daily (random)": SquadBattles.MODE.DAILY_RANDOM}))


class _WorldBossInvasion(GameMode):

    def __init__(self, game):
        super().__init__(game, "WORLD BOSS INVASION", WorldBossInvasion)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All available"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many times to complete",
                                                       min=1, max=5))


class _DangerRoom(GameMode):

    def __init__(self, game):
        super().__init__(game, "DANGER ROOM", DangerRoom)
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="all_stages",
                                                       text="All available daily entries"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Combobox,
                                                       setting_key="mode",
                                                       text="Select Danger Room mode",
                                                       values_dict={"Normal": DangerRoom.MODE.NORMAL,
                                                                    "Extreme": DangerRoom.MODE.EXTREME}))


class _DangerousSisters(GameMode):

    def __init__(self, game):
        super().__init__(game, "DANGEROUS SISTERS", DangerousSisters, "Dangerous Sisters [Nebula]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))


class _CosmicRider(GameMode):

    def __init__(self, game):
        super().__init__(game, "COSMIC RIDER", CosmicRider, "Cosmic Rider [Punisher]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))


class _QuantumPower(GameMode):

    def __init__(self, game):
        super().__init__(game, "QUANTUM POWER", QuantumPower, "Quantum Power [Gamora]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _WingsOfDarkness(GameMode):

    def __init__(self, game):
        super().__init__(game, "WINGS OF DARKNESS", WingsOfDarkness, "Wings Of Darkness [Darkhawk]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _InhumanPrincess(GameMode):

    def __init__(self, game):
        super().__init__(game, "INHUMAN PRINCESS", InhumanPrincess, "Inhuman Princess [Crystal]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))


class _MeanAndGreen(GameMode):

    def __init__(self, game):
        super().__init__(game, "MEAN AND GREEN", MeanAndGreen, "Mean And Green [She-Hulk]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))


class _ClobberinTime(GameMode):

    def __init__(self, game):
        super().__init__(game, "CLOBBERIN TIME", ClobberinTime, "Clobberin Time [Thing]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _Hothead(GameMode):

    def __init__(self, game):
        super().__init__(game, "HOTHEAD", Hothead, "Hothead [Human Torch]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _AwManThisGuy(GameMode):

    def __init__(self, game):
        super().__init__(game, "AW MAN THIS GUY", AwManThisGuy, "Aw, Man. This Guy? [Fantomex]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _DominoFalls(GameMode):

    def __init__(self, game):
        super().__init__(game, "DOMINO FALLS", DominoFalls, "Domino Falls [Domino]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _GoingRogue(GameMode):

    def __init__(self, game):
        super().__init__(game, "GOING ROGUE", GoingRogue, "Going Rogue [Rogue]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _FriendsAndEnemies(GameMode):

    def __init__(self, game):
        super().__init__(game, "FRIENDS AND ENEMIES", FriendsAndEnemies, "Friends And Enemies [Beast]")

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _WeatheringTheStorm(GameMode):

    def __init__(self, game):
        super().__init__(game, "WEATHERING THE STORM", WeatheringTheStorm, "Weathering The Storm [Storm]")

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=4))


class _Blindsided(GameMode):

    def __init__(self, game):
        super().__init__(game, "BLINDSIDED", Blindsided, "Blindsided [Cyclops]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))


class _DarkAdvent(GameMode):

    def __init__(self, game):
        super().__init__(game, "DARK ADVENT", DarkAdvent, "Dark Advent [Satana/Cleo]")

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _IncreasingDarkness(GameMode):

    def __init__(self, game):
        super().__init__(game, "INCREASING DARKNESS", IncreasingDarkness, "Increasing Darkness [Hellstorm/Cleo]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Checkbox,
                                                       setting_key="farm_shifter_bios",
                                                       initial_state=False,
                                                       text="Farm shifter's biometrics (requires restartable emulator)")
                                  )


class _RoadToMonastery(GameMode):

    def __init__(self, game):
        super().__init__(game, "ROAD TO MONASTERY", RoadToMonastery, "Road To Monastery [Baron Mordo]")
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=6))


class _MysteriousAmbush(GameMode):

    def __init__(self, game):
        super().__init__(game, "MYSTERIOUS AMBUSH", MysteriousAmbush, "Mysterious Ambush [Wong]")

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=6))


class _MonasteryInTrouble(GameMode):

    def __init__(self, game):
        super().__init__(game, "MONASTERY IN TROUBLE", MonasteryInTrouble, "Monastery In Trouble [Ancient One]")

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=6))


class _PowerOfTheDark(GameMode):

    def __init__(self, game):
        super().__init__(game, "POWER OF THE DARK", PowerOfTheDark, "Power Of The Dark [Kaecilius]")

        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="times",
                                                       text="Select how many stages to complete"))
        self.mode_settings.append(GameMode.ModeSetting(setting_type=GameMode.ModeSetting.Spinbox,
                                                       setting_key="difficulty",
                                                       text="Select stage difficulty",
                                                       min=1, max=6))
