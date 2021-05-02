from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, r_sleep
import lib.logger as logging

logger = logging.get_logger(__name__)


class GiantBossRaid(Missions):
    """Class for working with Giant Boss Raid missions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'GBR_MENU_LABEL')

    @property
    def battle_over_conditions(self):
        def damage_list():
            return self.emulator.is_ui_element_on_screen(self.ui['GBR_DAMAGE_LIST'])

        def damage_list_failure():
            on_screen = self.emulator.is_ui_element_on_screen(self.ui['GBR_FAILURE_DAMAGE_LIST'])
            if on_screen:
                logger.info("Giant Boss Raid: you've lost the raid.")
            return on_screen

        def rewards_list():
            return self.emulator.is_ui_element_on_screen(self.ui['GBR_REWARDS_LIST'])

        return [damage_list, rewards_list, damage_list_failure]

    def do_missions(self, times=None, max_rewards=None):
        """Do missions."""
        self.start_missions(times=times, max_rewards=max_rewards)
        self.end_missions()

    def start_missions(self, times=0, max_rewards=None):
        """Start Giant Boss Raid."""
        if self.open_giant_boss_raid():
            logger.info(f"Starting {times} raid(s).")
            while times > 0:
                if not self.press_start_button(max_rewards=max_rewards):
                    return
                ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
                times -= 1
                r_sleep(5)  # Animation for rewards
                if times > 0:
                    self.press_repeat_button(repeat_button_ui="GBR_REPEAT_BUTTON", start_button_ui="GBR_QUICK_START")
                else:
                    self.press_home_button(home_button="GBR_HOME_BUTTON")
        logger.info("No more stages.")

    def end_missions(self):
        """End missions."""
        if not self.game.is_main_menu():
            self.game.emulator.click_button(self.ui['HOME'].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def open_giant_boss_raid(self):
        """Open Giant Boss Raid mission lobby.

        :return: True or False: is GBR missions open.
        """
        self.game.go_to_coop()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_LABEL']):
            self.emulator.click_button(self.ui['GBR_LABEL'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_MENU_LABEL']):
                return wait_until(self.emulator.is_ui_element_on_screen, timeout=10,
                                  ui_element=self.ui['GBR_QUICK_START'])
        return False

    def press_start_button(self, start_button_ui='GBR_CREATE_LOBBY', max_rewards=None):
        """Press start button of the mission.

        :return: was button clicked successfully.
        """
        logger.debug(f"Pressing START button with UI element: {start_button_ui}.")
        self.emulator.click_button(self.ui[start_button_ui].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_NOT_ENOUGH_ENERGY']):
            logger.debug("Not enough energy.")
            self.emulator.click_button(self.ui['GBR_NOT_ENOUGH_ENERGY'].button)
            return False
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=30, ui_element=self.ui['GBR_SELECT_CHARACTERS']):
            self._deploy_characters()
            self.emulator.click_button(self.ui['GBR_SELECT_CHARACTERS_OK'].button)
            if max_rewards:
                logger.debug("Maxing out rewards via boost points.")
                while not self.emulator.is_ui_element_on_screen(self.ui['GBR_BOOST_POINTS_NO_MORE']):
                    self.emulator.click_button(self.ui['GBR_BOOST_POINTS_PLUS'].button)
                self.emulator.click_button(self.ui['GBR_BOOST_POINTS_NO_MORE'].button)
            if not wait_until(self.emulator.is_image_on_screen, timeout=1,
                              ui_element=self.ui['GBR_PUBLIC_LOBBY_TOGGLE']):
                logger.debug("Found PUBLIC LOBBY toggle inactive. Clicking it.")
                self.emulator.click_button(self.ui['GBR_PUBLIC_LOBBY_TOGGLE'].button)

            logger.debug("Waiting for players in lobby.")
            waiting_time, timeout_to_kick = 1, 120
            while not self.emulator.is_ui_element_on_screen(ui_element=self.ui['GBR_START_BUTTON']):
                if waiting_time % timeout_to_kick == 0:
                    logger.debug(f"Too long, kicking all players. Wait time is {waiting_time} secs.")
                    if self.emulator.is_ui_element_on_screen(ui_element=self.ui['GBR_KICK_PLAYER_2']):
                        logger.debug("Kicking emulator #2.")
                        self.emulator.click_button(self.ui['GBR_KICK_PLAYER_2'].button)
                    if self.emulator.is_ui_element_on_screen(ui_element=self.ui['GBR_KICK_PLAYER_3']):
                        logger.debug("Kicking emulator #3.")
                        self.emulator.click_button(self.ui['GBR_KICK_PLAYER_3'].button)
                r_sleep(1)
                waiting_time += 1
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_START_BUTTON']):
                logger.debug("All players are ready. Starting the raid.")
                self.emulator.click_button(self.ui['GBR_START_BUTTON'].button)
                return True
        logger.warning("Unable to press START button.")
        return False

    def _deploy_characters(self):
        """Deploy 3 characters to battle."""
        no_main = self.emulator.is_image_on_screen(ui_element=self.ui['GBR_NO_CHARACTER_MAIN'])
        no_left = self.emulator.is_image_on_screen(ui_element=self.ui['GBR_NO_CHARACTER_LEFT'])
        no_right = self.emulator.is_image_on_screen(ui_element=self.ui['GBR_NO_CHARACTER_RIGHT'])
        if no_main:
            self.emulator.click_button(self.ui['GBR_CHARACTER_1'].button)
        if no_left:
            self.emulator.click_button(self.ui['GBR_CHARACTER_2'].button)
        if no_right:
            self.emulator.click_button(self.ui['GBR_CHARACTER_3'].button)
