from lib.functions import wait_until, r_sleep
from lib.game.missions.missions import Missions
from lib.game.battle_bot import AutoBattleBot
import lib.logger as logging

logger = logging.get_logger(__name__)


class DimensionMissions(Missions):
    """Class for working with Dimension Missions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'DM_LABEL')

    def go_to_dm(self):
        """Go to Dimension Missions.

        :return: True or False: is Dimension Missions open.
        """
        self.game.go_to_mission_selection()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DM_MISSION']):
            self.player.click_button(self.ui['DM_MISSION'].button)
            self.game.close_ads(timeout=5)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DM_LABEL'])
        return False

    @property
    def stage_level(self):
        """Get current stage level.

        :return: current stage level.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DM_LABEL']):
            stage_str = self.player.get_screen_text(ui_element=self.ui['DM_LEVEL'])
            try:
                stage_int = int(stage_str)
            except ValueError:
                logger.critical(f"Dimension Missions: cannot convert stage to integer: {stage_str}")
                stage_int = 0
            return stage_int
        return 0

    def increase_stage_level(self):
        """Increase current stage level"""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['DM_LEVEL_READY']):
            logger.info("Dimension Missions: increasing stage difficulty level.")
            self.player.click_button(self.ui['DM_LEVEL_PLUS'].button, min_duration=0.01, max_duration=0.01)

    def decrease_stage_level(self):
        """Decrease current stage level"""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['DM_LEVEL_READY']):
            logger.info("Dimension Missions: decreasing stage difficulty level.")
            self.player.click_button(self.ui['DM_LEVEL_MINUS'].button, min_duration=0.01, max_duration=0.01)

    def select_stage_level(self, level_num=15):
        """Select stage level.

        :param level_num: level to select.
        """
        if level_num > 15 or level_num <= 0:
            logger.error(f"Dimension Missions: stage level should be between 1 and 15, got {level_num} instead.")
            return
        if self.stage_level == 0:
            logger.critical("Dimensions Missions: something went wrong with stage level acquiring.")
            return
        safe_counter = 0
        diff = abs(level_num - self.stage_level)
        while self.stage_level != level_num:
            if safe_counter > diff:
                logger.warning(f"Dimensions Missions: stage level was changed more than {safe_counter}. "
                               f"Your max stage level probably lesser than {level_num}.")
                break
            safe_counter += 1
            if self.stage_level > level_num:
                self.decrease_stage_level()
            if self.stage_level < level_num:
                self.increase_stage_level()
            logger.debug(f"Dimensions Missions: current stage level is {self.stage_level}")

    def select_team(self):
        """Select team for missions."""
        team_element = self.ui[f'DM_SELECT_TEAM_{self.game.mission_team}']
        logger.debug(f"Selecting team: {team_element.name}")
        self.player.click_button(team_element.button)

    def get_ready(self):
        """Get ready for mission.

        :return: (bool) is mission menu is opened.
        """
        if self.player.is_ui_element_on_screen(ui_element=self.ui['DM_LEVEL_READY']):
            logger.info("Dimension Missions: clicking READY to mission button.")
            self.player.click_button(self.ui['DM_LEVEL_READY'].button)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DM_START_BUTTON'])

    def do_missions(self, times=0, difficulty=15, use_hidden_tickets=False, acquire_rewards=False):
        """Do missions."""
        self.start_missions(times=times, difficulty=difficulty, use_hidden_tickets=use_hidden_tickets)
        if acquire_rewards:
            self.acquire_rewards()
        self.end_missions()

    def end_missions(self):
        """End missions."""
        if not self.game.is_main_menu():
            self.game.player.click_button(self.ui['HOME'].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def start_missions(self, times=0, difficulty=15, use_hidden_tickets=False):
        """Start Dimension Missions.

        :param times: how many times to complete missions.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        :param use_hidden_tickets: use Hidden Tickets or not.
        """
        logger.info(f"Starting Dimensions Missions for {times} times.")
        if not self.go_to_dm():
            logger.warning("Dimension Mission: can't get in mission lobby.")
            return
        self.select_stage_level(level_num=difficulty)
        while times > 0:
            if self.get_ready():
                r_sleep(1)
                if not self.is_stage_startable():
                    logger.error("Cannot start Dimension Mission battle, not enough boost points.")
                    return
                if not self.press_start_button(start_button_ui='DM_START_BUTTON',
                                               use_hidden_tickets=use_hidden_tickets):
                    logger.error("Cannot start Dimension Mission battle, exiting.")
                    return
                AutoBattleBot(self.game, self.battle_over_conditions).fight()
                times -= 1
                self.close_mission_notifications()
                if times > 0:
                    self.press_repeat_button()
                else:
                    self.press_home_button()
                    self.close_after_mission_notifications()
        logger.info("No more stages for Dimension Missions.")

    def press_start_button(self, start_button_ui='START_BUTTON', use_hidden_tickets=False):
        """Press start button of the mission."""
        if super().press_start_button(start_button_ui=start_button_ui):
            if use_hidden_tickets and wait_until(self.player.is_ui_element_on_screen, timeout=2,
                                                 ui_element=self.ui['DM_TICKET_NOTIFICATION_USE']):
                logger.debug("Dimension Missions: clicked USE hidden tickets.")
                self.player.click_button(self.ui['DM_TICKET_NOTIFICATION_USE'].button)
            if not use_hidden_tickets and wait_until(self.player.is_ui_element_on_screen, timeout=2,
                                                     ui_element=self.ui['DM_TICKET_NOTIFICATION_DONT_USE']):
                logger.debug("Dimension Missions: clicked DON'T USE hidden tickets.")
                self.player.click_button(self.ui['DM_TICKET_NOTIFICATION_DONT_USE'].button)
            return True
        return False

    def press_repeat_button(self, repeat_button_ui='REPEAT_BUTTON', start_button_ui=None):
        """Press repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.player.click_button(self.ui[repeat_button_ui].button)
        while not self.player.is_ui_element_on_screen(ui_element=self.ui['DM_LEVEL_READY']):
            self.close_after_mission_notifications(timeout=1)
            self.game.close_ads(timeout=1)
        return True

    def acquire_rewards(self):
        """Acquire all Dimension rewards."""
        def is_reward_to_acquire_exists():
            return self.player.is_ui_element_on_screen(ui_element=self.ui['DM_ACQUIRE_NEXT_REWARD']) or \
                   self.player.is_ui_element_on_screen(ui_element=self.ui['DM_REWARD_ACQUIRED_OK'])

        # TODO: inventory full check
        logger.info("Dimension Missions: acquiring rewards.")
        if not self.go_to_dm():
            logger.warning("Dimension Mission: can't get in mission lobby.")
            return
        self.player.click_button(self.ui['DM_ACQUIRE_REWARD'].button)
        while wait_until(is_reward_to_acquire_exists, timeout=3):
            self.acquire_reward()
        logger.info("Dimension Missions: no more rewards to acquire.")

    def acquire_reward(self):
        """Acquire one reward."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['DM_ACQUIRE_NEXT_REWARD']):
            self.player.click_button(self.ui['DM_ACQUIRE_NEXT_REWARD'].button)
        if self.player.is_ui_element_on_screen(ui_element=self.ui['DM_REWARD_ACQUIRED_OK']):
            self.player.click_button(self.ui['DM_REWARD_ACQUIRED_OK'].button)

    @property
    def energy_cost(self):
        """Energy cost of the mission.

        :return: energy cost.
        """
        cost = self.player.get_screen_text(self.ui['DM_ENERGY_COST'])
        return int(cost) if cost.isdigit() else None

    @property
    def boost_cost(self):
        """Boost points cost of the mission.

        :return: boost points cost.
        """
        cost = self.player.get_screen_text(self.ui['DM_BOOST_COST'])
        return int(cost) if cost.isdigit() else None
