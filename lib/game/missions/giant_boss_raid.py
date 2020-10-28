from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until
import lib.logger as logging

logger = logging.get_logger(__name__)


class GiantBossRaid(Missions):
    """Class for working with Giant Boss Raids."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'GBR_MENU_LABEL')

    @property
    def battle_over_conditions(self):
        def damage_list():
            return self.player.is_ui_element_on_screen(self.ui['GBR_DAMAGE_LIST'])

        def rewards_list():
            return self.player.is_ui_element_on_screen(self.ui['GBR_REWARDS_LIST'])

        return [damage_list, rewards_list]

    def do_missions(self, times=None, max_rewards=None):
        """Do missions."""
        self.start_missions(times=times, max_rewards=max_rewards)
        self.end_missions()

    def start_missions(self, times=None, max_rewards=None):
        """Start Giant Boss Raid."""
        if self.go_to_gbr():
            logger.info(f"Giant Boss Raid: starting {times} raids.")
            while times > 0:
                if not self.press_start_button(max_rewards=max_rewards):
                    return
                ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
                times -= 1
                if times > 0:
                    self.press_repeat_button(repeat_button_ui="GBR_REPEAT_BUTTON", start_button_ui="GBR_QUICK_START")
                else:
                    self.press_home_button(home_button="GBR_HOME_BUTTON")
        logger.info("No more stages for Giant Boss Raid.")

    def end_missions(self):
        """End missions."""
        if not self.game.is_main_menu():
            self.game.player.click_button(self.ui['HOME'].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def go_to_gbr(self):
        """Go to Giant Boss Raid missions.

        :return: True or False: is GBR missions open.
        """
        self.game.go_to_coop()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_LABEL']):
            self.player.click_button(self.ui['GBR_LABEL'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_MENU_LABEL']):
                return wait_until(self.player.is_ui_element_on_screen, timeout=10,
                                  ui_element=self.ui['GBR_QUICK_START'])
        return False

    def press_start_button(self, start_button_ui='GBR_QUICK_START', max_rewards=None):
        """Press start button of the mission.

        :return: was button clicked successfully.
        """
        logger.debug(f"Pressing START button.")
        self.player.click_button(self.ui[start_button_ui].button)
        # TODO: GBR_SEARCHING_LOBBY
        if wait_until(self.player.is_ui_element_on_screen, timeout=30, ui_element=self.ui['GBR_SELECT_CHARACTERS']):
            self.deploy_characters()
            self.player.click_button(self.ui['GBR_SELECT_CHARACTERS_OK'].button)
            if max_rewards:
                logger.debug(f"Giant Boss Raid: maxing out rewards via boost points.")
                while not self.player.is_ui_element_on_screen(self.ui['GBR_BOOST_POINTS_NO_MORE']):
                    self.player.click_button(self.ui['GBR_BOOST_POINTS_PLUS'].button)
                self.player.click_button(self.ui['GBR_BOOST_POINTS_NO_MORE'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['GBR_READY_BUTTON']):
                self.player.click_button(self.ui['GBR_READY_BUTTON'].button)
                return True
        logger.warning("Unable to press START button.")
        return False

    def deploy_characters(self):
        """Deploy 3 characters to battle."""
        no_main = self.player.is_image_on_screen(ui_element=self.ui['GBR_NO_CHARACTER_MAIN'])
        no_left = self.player.is_image_on_screen(ui_element=self.ui['GBR_NO_CHARACTER_LEFT'])
        no_right = self.player.is_image_on_screen(ui_element=self.ui['GBR_NO_CHARACTER_RIGHT'])
        if no_main:
            self.player.click_button(self.ui['GBR_CHARACTER_1'].button)
        if no_left:
            self.player.click_button(self.ui['GBR_CHARACTER_2'].button)
        if no_right:
            self.player.click_button(self.ui['GBR_CHARACTER_3'].button)
