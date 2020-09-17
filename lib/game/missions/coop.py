from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, r_sleep
import lib.logger as logging

logger = logging.get_logger(__name__)


class CoopPlay(Missions):
    """Class for working with Co-op missions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'COOP_PLAY_LABEL')

    @property
    def battle_over_conditions(self):
        def coop_completion():
            return self.player.is_ui_element_on_screen(self.ui['COOP_COMPLETION'])

        return [coop_completion]

    def calculate_username_length(self):
        """Calculate position of username in Co-op."""
        self.game.ui['COOP_USER_NAME'].text = self.game.user_name
        new_width = self.game.ui['COOP_USER_NAME_ONE_LETTER'].rect.width * len(self.game.ui['COOP_USER_NAME'].text)
        self.game.ui['COOP_USER_NAME'].rect.x2 = self.game.ui['COOP_USER_NAME'].rect.x1 + new_width

    def start_missions(self):
        """Start available missions."""
        logger.info(f"Coop play: {self.stages} stages available")
        if self.stages > 0:
            self.calculate_username_length()
            self.go_to_stages()
            self.check_rewards()
            if wait_until(self.player.is_image_on_screen, timeout=1, ui_element=self.ui['COOP_REPEAT_TOGGLE']):
                logger.debug("Found REPEAT toggle active. Clicking it.")
                self.player.click_button(self.ui['COOP_REPEAT_TOGGLE'].button)
            if not wait_until(self.player.is_image_on_screen, timeout=1, ui_element=self.ui['COOP_QUICK_MATCH_TOGGLE']):
                logger.debug("Found QUICK MATCH toggle inactive. Clicking it.")
                self.player.click_button(self.ui['COOP_QUICK_MATCH_TOGGLE'].button)
            while self.stages > 0:
                if not self.deploy_character():
                    logger.warning("Can't deploy character for COOP. Probably you run out of available. Exiting")
                    self.stages *= 0
                    break
                self.press_start_button()
                self.check_rewards()
        logger.info("No more stages for coop play.")

    @property
    def stage_percentage(self):
        """Stage percentage of stage's completion."""
        if self.player.is_ui_element_on_screen(self.ui['COOP_PLAY_MENU_LABEL']):
            percentage = self.player.get_screen_text(self.ui['COOP_STAGE_PERCENTAGE'])
            return percentage

    def go_to_stages(self):
        """Go to Co-op missions stage."""
        self.game.select_mode(self.mode_name)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_PLAY_MENU_LABEL'])

    def deploy_character(self):
        """Deploy available character for Co-op mission."""
        def is_not_deployed():
            return self.player.is_ui_element_on_screen(
                self.ui['COOP_DEPLOY_CHARACTER']) or not self.player.is_ui_element_on_screen(self.ui['COOP_USER_NAME'])

        if wait_until(is_not_deployed, timeout=3):
            self.player.click_button(self.ui['COOP_FIRST_CHAR'].button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_USER_NAME'])

    def press_start_button(self, check_inventory=True):
        """Start Co-op mission stage."""
        self.player.click_button(self.ui['COOP_START_BUTTON'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=10, ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
            logger.debug("Waiting for other players.")
            if wait_until(self.player.is_ui_element_on_screen, timeout=60, condition=False,
                          ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['DISCONNECT_NEW_OPPONENT']):
                    logger.debug("Got disconnected. Finding new opponent.")
                    self.player.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
                    return self.press_start_button(check_inventory=False)
                AutoBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
                r_sleep(2)   # wait progress bar animation
                if self.stages > 0:
                    self.press_repeat_button()
                else:
                    self.press_home_button()
                return
        if check_inventory and wait_until(self.player.is_ui_element_on_screen, timeout=2,
                                          ui_element=self.ui['INVENTORY_FULL']):
            self.player.click_button(self.ui['INVENTORY_FULL'].button)
            self.stages *= 0
            return
        logger.warning("Something went wrong while waiting for other players.")
        self.player.click_button(self.ui['WAITING_FOR_OTHER_PLAYERS'].button)

    def press_repeat_button(self, repeat_button_ui='REPEAT_BUTTON', start_button_ui=None):
        """Press repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.player.click_button(self.ui[repeat_button_ui].button)
        while not (self.player.is_ui_element_on_screen(ui_element=self.ui['COOP_START_BUTTON']) or
                   self.player.is_ui_element_on_screen(ui_element=self.ui['COOP_REWARD']) or
                   self.player.is_ui_element_on_screen(self.ui['COOP_DEPLOY_CHARACTER'])):
            self.close_after_mission_notifications(timeout=1)
        return True

    def check_rewards(self):
        """Check and get Co-op mission rewards."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_REWARD']):
            self.player.click_button(self.ui['COOP_REWARD'].button)
            if self._check_or_acquire_rewards():
                self.stages -= 1
                if wait_until(self.player.is_ui_element_on_screen, timeout=10,
                              ui_element=self.ui['COOP_REWARD_ACQUIRE']):
                    r_sleep(4)
                    self.player.click_button(self.ui['COOP_REWARD_ACQUIRE'].button)

    def _check_or_acquire_rewards(self):
        """Check if Reward Acquire button is available or press acquire button.

        :return: True or False.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['COOP_REWARD_ACQUIRE_CONFIRM']):
            self.player.click_button(self.ui['COOP_REWARD_ACQUIRE_CONFIRM'].button)
            return True
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['COOP_REWARD_ACQUIRE_CONFIRM_TICKETS']):
            self.player.click_button(self.ui['COOP_REWARD_ACQUIRE_CONFIRM_TICKETS'].button)
            return True
        return False
