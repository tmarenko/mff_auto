import lib.logger as logging
from lib.functions import wait_until, r_sleep
from lib.game import ui
from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class DimensionMission(Missions):
    """Class for working with Dimension Missions."""

    MISSION_MULTIPLIER = 5  # How many missions needs to complete for one reward

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='DIMENSION MISSION')

    def open_dimension_mission(self):
        """Opens Dimension Missions lobby.

        :return: is Dimension Missions open or not.
        :rtype: bool
        """
        self.game.select_mode(self.mode_name)
        self.game.close_ads(timeout=5)
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DM_LABEL)

    @property
    def stage_level(self):
        """Gets current stage level.

        :rtype: int
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DM_LABEL):
            stage_str = self.emulator.get_screen_text(ui_element=ui.DM_LEVEL)
            try:
                stage_int = int(stage_str)
            except ValueError:
                logger.critical(f"Cannot convert stage to integer: {stage_str}")
                stage_int = 0
            return stage_int
        return 0

    def _increase_stage_level(self):
        """Increases current stage level"""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DM_LEVEL_READY):
            logger.info("Increasing stage difficulty level.")
            self.emulator.click_button(ui.DM_LEVEL_PLUS, min_duration=0.01, max_duration=0.01)

    def _decrease_stage_level(self):
        """Decreases current stage level"""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DM_LEVEL_READY):
            logger.info("Decreasing stage difficulty level.")
            self.emulator.click_button(ui.DM_LEVEL_MINUS, min_duration=0.01, max_duration=0.01)

    def _select_stage_level(self, level_num=15):
        """Selects stage level.

        :param int level_num: level to select.
        """
        if level_num > 15 or level_num <= 0:
            return logger.error(f"Stage level should be between 1 and 15, got {level_num} instead.")
        if self.stage_level == 0:
            return logger.error("Something went wrong with stage level acquiring.")
        safe_counter = 0
        diff = abs(level_num - self.stage_level)
        while self.stage_level != level_num:
            if safe_counter > diff:
                logger.warning(f"Stage level was changed more than {safe_counter}. "
                               f"Your max stage level probably lesser than {level_num}.")
                break
            safe_counter += 1
            if self.stage_level > level_num:
                self._decrease_stage_level()
            if self.stage_level < level_num:
                self._increase_stage_level()
            logger.debug(f"Current stage level is {self.stage_level}")

    def select_team(self):
        """Selects team for missions."""
        team_element = ui.get_by_name(f'DM_SELECT_TEAM_{self.game.mission_team}')
        logger.debug(f"Selecting team: {team_element.name}")
        self.emulator.click_button(team_element)

    def _get_ready_for_mission(self):
        """Gets ready for mission.

        :return: is mission menu opened or not.
        :rtype: bool
        """
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DM_LEVEL_READY):
            logger.info("Clicking READY button.")
            self.emulator.click_button(ui.DM_LEVEL_READY)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DM_START_BUTTON)

    def do_missions(self, times=0, difficulty=15, use_hidden_tickets=False, acquire_rewards=False):
        """Does missions."""
        if times == 0:
            times = self.MISSION_MULTIPLIER * self.stages
        if times != 0:
            self.start_missions(times=times, difficulty=difficulty, use_hidden_tickets=use_hidden_tickets)
        if acquire_rewards:
            self.acquire_rewards()
        self.end_missions()

    def start_missions(self, times=0, difficulty=15, use_hidden_tickets=False):
        """Starts Dimension Missions.

        :param int times: how many times to complete missions.
        :param int difficulty: name of UI element that contains info about difficulty of stage.
        :param bool use_hidden_tickets: use Hidden Tickets or not.
        """
        logger.info(f"Starting Dimensions Missions for {times} times.")
        if not self.open_dimension_mission():
            return logger.error("Can't get in mission lobby.")
        self._select_stage_level(level_num=difficulty)
        if self._get_ready_for_mission():
            r_sleep(1)
            if not self.is_stage_startable():
                return logger.error("Cannot start Dimension Mission battle, not enough boost points.")
        while times > 0:
            if not self.press_start_button(start_button_ui=ui.DM_START_BUTTON,
                                           use_hidden_tickets=use_hidden_tickets):
                return logger.error("Cannot start Dimension Mission battle, exiting.")
            AutoBattleBot(self.game, self.battle_over_conditions).fight()
            times -= 1
            self.close_mission_notifications()
            logger.debug(f"{times} stages left to complete.")
            if times > 0:
                self.press_repeat_button()
            else:
                self.press_home_button()
                self.close_after_mission_notifications()
        logger.info("No more stages.")

    def press_start_button(self, start_button_ui=ui.DM_START_BUTTON, use_hidden_tickets=False):
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
            if use_hidden_tickets and wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                                                 ui_element=ui.DM_TICKET_NOTIFICATION_USE):
                logger.debug("Clicked USE hidden tickets.")
                self.emulator.click_button(ui.DM_TICKET_NOTIFICATION_USE)
            if not use_hidden_tickets and wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                                                     ui_element=ui.DM_TICKET_NOTIFICATION_DONT_USE):
                logger.debug("Clicked DON'T USE hidden tickets.")
                self.emulator.click_button(ui.DM_TICKET_NOTIFICATION_DONT_USE)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                          ui_element=ui.ITEM_MAX_LIMIT_NOTIFICATION):
                self.emulator.click_button(ui.ITEM_MAX_LIMIT_NOTIFICATION)
            return True
        logger.error(f"Unable to press START button with UI element: {start_button_ui}.")
        return False

    def press_repeat_button(self, repeat_button_ui=ui.REPEAT_BUTTON, start_button_ui=ui.DM_START_BUTTON):
        """Presses repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.emulator.click_button(repeat_button_ui, min_duration=1, max_duration=2)
        while not self.emulator.is_ui_element_on_screen(ui_element=start_button_ui):
            self.close_after_mission_notifications(timeout=1)
        return True

    def acquire_rewards(self):
        """Acquires all Dimension rewards."""

        def is_reward_to_acquire_exists():
            if self.emulator.is_ui_element_on_screen(ui_element=ui.INVENTORY_FULL):
                logger.warning("Stopping acquiring rewards because inventory is full.")
                self.emulator.click_button(ui.INVENTORY_FULL)
            return self.emulator.is_ui_element_on_screen(ui_element=ui.DM_ACQUIRE_NEXT_REWARD) or \
                   self.emulator.is_ui_element_on_screen(ui_element=ui.DM_REWARD_ACQUIRED_OK)

        logger.info("Acquiring rewards.")
        if not self.open_dimension_mission():
            return logger.error("Can't get in mission lobby.")
        self.emulator.click_button(ui.DM_ACQUIRE_REWARD)
        while wait_until(is_reward_to_acquire_exists):
            self._acquire_reward()
        logger.info("No more rewards to acquire.")

    def _acquire_reward(self):
        """Acquires one reward."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DM_ACQUIRE_NEXT_REWARD):
            self.emulator.click_button(ui.DM_ACQUIRE_NEXT_REWARD)
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DM_REWARD_ACQUIRED_OK):
            self.emulator.click_button(ui.DM_REWARD_ACQUIRED_OK)

    @property
    def energy_cost(self):
        """Energy cost of the mission.

        :rtype: int
        """
        cost = self.emulator.get_screen_text(ui.DM_ENERGY_COST)
        return int(cost) if cost.isdigit() else None

    @property
    def boost_cost(self):
        """Boost points cost of the mission.

        :rtype: int
        """
        cost = self.emulator.get_screen_text(ui.DM_BOOST_COST)
        return int(cost) if cost.isdigit() else None
