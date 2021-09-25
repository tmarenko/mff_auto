import lib.logger as logging
from lib.functions import wait_until
from lib.game import ui
from lib.game.battle_bot import AutoBattleBot
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)


class Missions(Notifications):
    """Class for working with mission's methods."""

    class _DIFFICULTY_4:
        STAGE_1 = "DIFFICULTY_STAGE_1"
        STAGE_2 = "DIFFICULTY_STAGE_2"
        STAGE_3 = "DIFFICULTY_STAGE_3"
        STAGE_4 = "DIFFICULTY_STAGE_2_6"

    class _DIFFICULTY_6:
        STAGE_1 = "DIFFICULTY_STAGE_1"
        STAGE_2 = "DIFFICULTY_STAGE_2"
        STAGE_3 = "DIFFICULTY_STAGE_3"
        STAGE_4 = "DIFFICULTY_STAGE_2_4"
        STAGE_5 = "DIFFICULTY_STAGE_2_5"
        STAGE_6 = "DIFFICULTY_STAGE_2_6"

    def __init__(self, game, mode_name=""):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        :param str mode_name: mission's game mode label.
        """
        super().__init__(game)
        self.mode_name = mode_name

    @property
    def energy_cost(self):
        """Energy cost of the mission.

        :rtype: int
        """
        cost = self.emulator.get_screen_text(ui.ENERGY_COST)
        return int(cost) if cost.isdigit() else None

    @property
    def boost_cost(self):
        """Boost points cost of the mission.

        :rtype: int
        """
        cost = self.emulator.get_screen_text(ui.BOOST_COST)
        return int(cost) if cost.isdigit() else None

    @property
    def stages_max(self):
        """Maximum stages of the mission.

        :rtype: int
        """
        mode = self.game.get_mode(self.mode_name)
        if mode:
            return mode.max_stages
        return 0

    @property
    def stages(self):
        """Available stages of the mission.

        :rtype: int
        """
        mode = self.game.get_mode(self.mode_name)
        if mode:
            return mode.stages
        return 0

    @stages.setter
    def stages(self, value):
        """Update available stages value.

        :param int value: value to set.
        """
        mode = self.game.get_mode(self.mode_name)
        if mode:
            mode.stages = value
            self.game.update_mode(mode)

    @property
    def battle_over_conditions(self):
        def cannot_enter():
            return self.emulator.is_ui_element_on_screen(ui.CANNOT_ENTER)

        def home_button():
            if self.emulator.is_image_on_screen(ui.HOME_BUTTON) or \
                    self.emulator.is_image_on_screen(ui.HOME_BUTTON_POSITION_2) or \
                    self.emulator.is_image_on_screen(ui.HOME_BUTTON_POSITION_3):
                return True

        return [cannot_enter, home_button, self.close_lvl_up_notification,
                self.close_stages_done_notification, self.close_items_def_notification, self.close_rank_up_notification,
                self.close_shield_lvl_up_notification, self.close_recruit_character_notification]

    @property
    def disconnect_conditions(self):
        def disconnect():
            if self.emulator.is_ui_element_on_screen(ui.DISCONNECT_FROM_SERVER):
                self.emulator.click_button(ui.DISCONNECT_FROM_SERVER)
                return True

        def new_opponent():
            if self.emulator.is_ui_element_on_screen(ui.DISCONNECT_NEW_OPPONENT):
                self.emulator.click_button(ui.DISCONNECT_NEW_OPPONENT)
                return True

        def kicked():
            if self.emulator.is_ui_element_on_screen(ui.KICKED_FROM_THE_SYSTEM):
                self.emulator.click_button(ui.KICKED_FROM_THE_SYSTEM)
                return True

        return [disconnect, new_opponent, kicked]

    def start_missions(self):
        """Starts missions."""
        pass

    def end_missions(self):
        """Ends missions."""
        self.game.clear_modes()
        if not self.game.is_main_menu():
            self.game.emulator.click_button(ui.HOME)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def do_missions(self, times=None):
        """Does missions."""
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions()
            self.end_missions()

    def select_team(self):
        """Selects team for missions."""
        team_element = ui.get_by_name(f'SELECT_TEAM_{self.game.mission_team}')
        logger.debug(f"Selecting team: {team_element.name}")
        self.emulator.click_button(team_element)

    def repeat_mission(self, times):
        """Repeats missions.

        :param int times: how many times to repeat.
        """
        for _ in range(times):
            if not self.press_start_button():
                return logger.error("Can't start missions while repeating them, exiting.")
            AutoBattleBot(self.game, self.battle_over_conditions).fight()
            self.close_mission_notifications()
            repeat_button_ui = None
            if wait_until(self.emulator.is_image_on_screen, timeout=2,
                          ui_element=ui.REPEAT_BUTTON_IMAGE_POSITION_2):
                repeat_button_ui = ui.REPEAT_BUTTON_IMAGE_POSITION_2
            else:
                if wait_until(self.emulator.is_image_on_screen, timeout=2,
                              ui_element=ui.REPEAT_BUTTON_IMAGE_POSITION_1):
                    repeat_button_ui = ui.REPEAT_BUTTON_IMAGE_POSITION_1
            if repeat_button_ui:
                self.press_repeat_button(repeat_button_ui)

    def press_start_button(self, start_button_ui=ui.START_BUTTON):
        """Presses start button of the mission."""
        if self.emulator.is_ui_element_on_screen(start_button_ui):
            self.select_team()
            self.emulator.click_button(start_button_ui)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2, ui_element=ui.NOT_ENOUGH_ENERGY):
                self.emulator.click_button(ui.NOT_ENOUGH_ENERGY)
                logger.warning(f"Not enough energy for starting mission, current energy: {self.game.energy}")
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2, ui_element=ui.INVENTORY_FULL):
                self.emulator.click_button(ui.INVENTORY_FULL)
                logger.warning("Your inventory is full, cannot start mission.")
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                          ui_element=ui.ITEM_MAX_LIMIT_NOTIFICATION):
                self.emulator.click_button(ui.ITEM_MAX_LIMIT_NOTIFICATION)
            return True
        logger.error(f"Unable to press {start_button_ui} button.")
        return False

    def press_repeat_button(self, repeat_button_ui=ui.REPEAT_BUTTON, start_button_ui=ui.START_BUTTON):
        """Presses repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.emulator.click_button(repeat_button_ui)
        while not self.emulator.is_ui_element_on_screen(ui_element=start_button_ui):
            self.close_after_mission_notifications(timeout=1)
        return True

    def press_home_button(self, home_button=ui.HOME_BUTTON):
        """Presses home button of the mission."""
        logger.debug(f"Clicking HOME button with UI Element: {home_button}.")
        self.emulator.click_button(home_button)
        while not self.game.is_main_menu():
            self.close_after_mission_notifications(timeout=1)
        return True

    def is_stage_startable(self):
        """Checks if you can start stage safely.

        :rtype: bool
        """
        return bool(self.boost_cost)
