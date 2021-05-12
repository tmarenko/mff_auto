from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, r_sleep, convert_colors_in_image
import lib.logger as logging

logger = logging.get_logger(__name__)


class CoopPlay(Missions):
    """Class for working with Co-op missions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'COOP_PLAY_LABEL')
        self._gray_color = ([100, 110, 120], [130, 140, 150])

    @property
    def battle_over_conditions(self):
        def coop_total_damage():
            image = self.emulator.get_screen_image(rect=self.ui['COOP_TOTAL_DAMAGE'].rect)
            converted_image = convert_colors_in_image(image=image, colors=[self._gray_color])
            return self.emulator.is_ui_element_on_screen(ui_element=self.ui['COOP_TOTAL_DAMAGE'],
                                                         screen=converted_image)

        def coop_completion():
            return self.emulator.is_ui_element_on_screen(self.ui['COOP_COMPLETION'])

        def coop_home_button():
            if self.emulator.is_image_on_screen(self.ui['COOP_HOME_BUTTON']):
                logger.debug("Found COOP HOME button image on screen.")
                return True

        return [coop_completion, coop_total_damage, coop_home_button]

    def start_missions(self):
        """Start available missions."""
        logger.info(f"{self.stages} stages available.")
        if self.stages > 0:
            self.open_coop_play()
            self.check_rewards()
            if wait_until(self.emulator.is_image_on_screen, timeout=1, ui_element=self.ui['COOP_REPEAT_TOGGLE']):
                logger.debug("Found REPEAT toggle active. Clicking it.")
                self.emulator.click_button(self.ui['COOP_REPEAT_TOGGLE'].button)
            if not wait_until(self.emulator.is_image_on_screen, timeout=1,
                              ui_element=self.ui['COOP_QUICK_MATCH_TOGGLE']):
                logger.debug("Found QUICK MATCH toggle inactive. Clicking it.")
                self.emulator.click_button(self.ui['COOP_QUICK_MATCH_TOGGLE'].button)
            while self.stages > 0:
                if not self._deploy_character():
                    logger.warning("Can't deploy character. Probably you run out of available. Exiting")
                    self.stages *= 0
                    break
                self.press_start_button()
                self.check_rewards()
        logger.info("No more stages.")

    @property
    def stage_percentage(self):
        """Stage percentage of stage's completion."""
        if self.emulator.is_ui_element_on_screen(self.ui['COOP_PLAY_MENU_LABEL']):
            return self.emulator.get_screen_text(self.ui['COOP_STAGE_PERCENTAGE'])

    def open_coop_play(self):
        """Go to Co-op missions stage."""
        self.game.select_mode(self.mode_name)
        return wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_PLAY_MENU_LABEL'])

    def _deploy_character(self):
        """Deploy available character for Co-op mission."""
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['COOP_START_BUTTON_INACTIVE']):
            logger.debug("Found inactive START button. Deploying character.")
            self.emulator.click_button(self.ui['COOP_FIRST_CHAR'].button)
        return wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_START_BUTTON'])

    def press_start_button(self, check_inventory=True):
        """Start Co-op mission stage."""
        self.emulator.click_button(self.ui['COOP_START_BUTTON'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=10,
                      ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
            logger.debug("Waiting for other players.")
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=60, condition=False,
                          ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['DISCONNECT_NEW_OPPONENT']):
                    logger.debug("Got disconnected. Finding new opponent.")
                    self.emulator.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
                    return self.press_start_button(check_inventory=False)
                AutoBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
                r_sleep(2)  # wait progress bar animation
                if self.stages > 0:
                    self.press_repeat_button()
                else:
                    self.press_home_button()
                return
        if check_inventory and wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                                          ui_element=self.ui['INVENTORY_FULL']):
            self.emulator.click_button(self.ui['INVENTORY_FULL'].button)
            self.stages *= 0
            logger.warning("Your inventory is full, cannot start mission.")
            return
        logger.warning("Something went wrong while waiting for other players.")
        self.emulator.click_button(self.ui['WAITING_FOR_OTHER_PLAYERS'].button)

    def press_repeat_button(self, repeat_button_ui='REPEAT_BUTTON', start_button_ui=None):
        """Press repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.emulator.click_button(self.ui[repeat_button_ui].button)
        while not (self.emulator.is_ui_element_on_screen(ui_element=self.ui['COOP_START_BUTTON_INACTIVE']) or
                   self.emulator.is_ui_element_on_screen(ui_element=self.ui['COOP_START_BUTTON']) or
                   self.emulator.is_ui_element_on_screen(ui_element=self.ui['COOP_REWARD']) or
                   self.emulator.is_ui_element_on_screen(self.ui['COOP_DEPLOY_CHARACTER'])):
            self.close_after_mission_notifications(timeout=1)
        return True

    def check_rewards(self):
        """Check and get Co-op mission rewards."""
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_REWARD']):
            logger.debug("Found available rewards button. Trying to acquire reward.")
            self.emulator.click_button(self.ui['COOP_REWARD'].button)
            if self._try_to_acquire_reward():
                self.stages -= 1
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=10,
                              ui_element=self.ui['COOP_REWARD_ACQUIRE']):
                    r_sleep(4)  # Wait for animation
                    self.emulator.click_button(self.ui['COOP_REWARD_ACQUIRE'].button)

    def _try_to_acquire_reward(self):
        """Check if Reward Acquire button is available or press acquire button.

        :return: True or False.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['COOP_REWARD_ACQUIRE_CONFIRM']):
            logger.debug("Acquiring first reward.")
            self.emulator.click_button(self.ui['COOP_REWARD_ACQUIRE_CONFIRM'].button)
            return True
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['COOP_REWARD_ACQUIRE_CONFIRM_TICKETS']):
            logger.debug("Acquiring additional reward using CLEAR TICKETS.")
            self.emulator.click_button(self.ui['COOP_REWARD_ACQUIRE_CONFIRM_TICKETS'].button)
            return True
        return False
