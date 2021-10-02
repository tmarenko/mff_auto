import lib.logger as logging
from lib.functions import wait_until, r_sleep
from lib.game import ui
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class GiantBossRaid(Missions):
    """Class for working with Giant Boss Raid missions."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='GIANT BOSS RAID')

    @property
    def battle_over_conditions(self):
        def damage_list():
            return self.emulator.is_ui_element_on_screen(ui.GBR_DAMAGE_LIST)

        def damage_list_failure():
            on_screen = self.emulator.is_ui_element_on_screen(ui.GBR_FAILURE_DAMAGE_LIST)
            if on_screen:
                logger.info("Giant Boss Raid: you've lost the raid.")
            return on_screen

        def rewards_list():
            return self.emulator.is_ui_element_on_screen(ui.GBR_REWARDS_LIST)

        return [damage_list, rewards_list, damage_list_failure]

    def do_missions(self, times=None, max_rewards=None):
        """Does missions."""
        self.start_missions(times=times, max_rewards=max_rewards)
        self.end_missions()

    def start_missions(self, times=0, max_rewards=None):
        """Starts Giant Boss Raid."""
        if self.open_giant_boss_raid():
            logger.info(f"Starting {times} raid(s).")
            while times > 0:
                if not self.press_start_button(max_rewards=max_rewards):
                    return
                ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
                times -= 1
                r_sleep(5)  # Animation for rewards
                if times > 0:
                    self.press_repeat_button(repeat_button_ui=ui.GBR_REPEAT_BUTTON, start_button_ui=ui.GBR_QUICK_START)
                else:
                    self.press_home_button(home_button=ui.GBR_HOME_BUTTON)
        logger.info("No more stages.")

    def end_missions(self):
        """Ends missions."""
        if not self.game.is_main_menu():
            if self.emulator.is_image_on_screen(ui.HOME):
                self.emulator.click_button(ui.HOME)
                self.close_after_mission_notifications()
                self.game.close_ads()
            else:
                logger.error("Can't return to main menu, HOME button is missing.")

    def open_giant_boss_raid(self):
        """Opens Giant Boss Raid mission lobby.

        :return: is Giant Boss Raid missions open or not.
        :rtype: bool
        """
        self.game.go_to_coop()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.GBR_LABEL):
            self.emulator.click_button(ui.GBR_LABEL)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.GBR_MENU_LABEL):
                return wait_until(self.emulator.is_ui_element_on_screen, timeout=10,
                                  ui_element=ui.GBR_QUICK_START)
        return False

    def press_start_button(self, start_button_ui=ui.GBR_CREATE_LOBBY, max_rewards=None):
        """Presses start button of the mission."""
        logger.debug(f"Pressing START button with UI element: {start_button_ui}.")
        self.emulator.click_button(start_button_ui)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.GBR_NOT_ENOUGH_ENERGY):
            logger.debug("Not enough energy.")
            self.emulator.click_button(ui.GBR_NOT_ENOUGH_ENERGY)
            return False
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=30, ui_element=ui.GBR_SELECT_CHARACTERS):
            self._deploy_characters()
            self.emulator.click_button(ui.GBR_SELECT_CHARACTERS_OK)
            if max_rewards:
                logger.debug("Maxing out rewards via boost points.")
                while not self.emulator.is_ui_element_on_screen(ui.GBR_BOOST_POINTS_NO_MORE):
                    self.emulator.click_button(ui.GBR_BOOST_POINTS_PLUS)
                self.emulator.click_button(ui.GBR_BOOST_POINTS_NO_MORE)
            if not wait_until(self.emulator.is_image_on_screen, timeout=1,
                              ui_element=ui.GBR_PUBLIC_LOBBY_TOGGLE):
                logger.debug("Found PUBLIC LOBBY toggle inactive. Clicking it.")
                self.emulator.click_button(ui.GBR_PUBLIC_LOBBY_TOGGLE)

            logger.debug("Waiting for players in lobby.")
            waiting_time, timeout_to_kick = 1, 120
            while not self.emulator.is_ui_element_on_screen(ui_element=ui.GBR_START_BUTTON):
                if waiting_time % timeout_to_kick == 0:
                    logger.debug(f"Too long, kicking all players. Wait time is {waiting_time} secs.")
                    if self.emulator.is_ui_element_on_screen(ui_element=ui.GBR_KICK_PLAYER_2):
                        logger.debug("Kicking emulator #2.")
                        self.emulator.click_button(ui.GBR_KICK_PLAYER_2)
                        if self.emulator.is_ui_element_on_screen(ui_element=ui.GBR_KICK_PLAYER_OK):
                            self.emulator.click_button(ui.GBR_KICK_PLAYER_OK)
                    if self.emulator.is_ui_element_on_screen(ui_element=ui.GBR_KICK_PLAYER_3):
                        logger.debug("Kicking emulator #3.")
                        self.emulator.click_button(ui.GBR_KICK_PLAYER_3)
                        if self.emulator.is_ui_element_on_screen(ui_element=ui.GBR_KICK_PLAYER_OK):
                            self.emulator.click_button(ui.GBR_KICK_PLAYER_OK)
                r_sleep(1)
                waiting_time += 1
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.GBR_START_BUTTON):
                logger.debug("All players are ready. Starting the raid.")
                self.emulator.click_button(ui.GBR_START_BUTTON)
                return True
        logger.error(f"Unable to press {start_button_ui} button.")
        return False

    def _deploy_characters(self):
        """Deploys 3 characters to battle."""
        no_main = self.emulator.is_image_on_screen(ui_element=ui.GBR_NO_CHARACTER_MAIN)
        no_left = self.emulator.is_image_on_screen(ui_element=ui.GBR_NO_CHARACTER_LEFT)
        no_right = self.emulator.is_image_on_screen(ui_element=ui.GBR_NO_CHARACTER_RIGHT)
        if no_main:
            self.emulator.click_button(ui.GBR_CHARACTER_1)
        if no_left:
            self.emulator.click_button(ui.GBR_CHARACTER_2)
        if no_right:
            self.emulator.click_button(ui.GBR_CHARACTER_3)
