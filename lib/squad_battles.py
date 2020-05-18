from lib.functions import wait_until
from lib.missions import Missions
from lib.battle_bot import AutoBattleBot
import logging
import random
import time

logger = logging.getLogger(__name__)


class SquadBattles(Missions):
    """Class for working with Squad Battles."""

    class MODE:

        ALL_BATTLES = "ALL_BATTLES"
        DAILY_RANDOM = "DAILY_RANDOM"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'SB_LABEL')

    def go_to_sb(self):
        """Go to Squad Battles.

        :return: True or False: is Squad Battles open.
        """
        self.game.go_to_challenge_selection()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['SQUAD_BATTLE']):
            self.player.click_button(self.ui['SQUAD_BATTLE'].button)
            self.game.close_ads(timeout=5)
            self.close_after_battle_notifications()
            return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['SB_LABEL'])
        return False

    def close_rank_change_notification(self):
        """Close rank change notification."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['SB_RANK_CHANGED']):
            logger.info("Squad Battles: closing rank change notification.")
            self.player.click_button(self.ui['SB_RANK_CHANGED'].button)
            return True
        return False

    def close_after_battle_notifications(self, timeout=5):
        """Close after battle notifications at the end of the battle.

        :param timeout: timeout of waiting for notifications.
        """
        for _ in range(timeout):
            notification_closed = wait_until(self.close_rank_change_notification, timeout=1)
            logger.debug(f"After mission notifications was closed: {notification_closed}")

    def do_missions(self, mode=MODE.DAILY_RANDOM):
        """Do missions."""
        self.start_missions(mode=mode)
        self.end_missions(home_button="SB_HOME_BUTTON" if mode == self.MODE.DAILY_RANDOM else "HOME")

    def start_missions(self, mode=MODE.DAILY_RANDOM):
        """Start Squad Battles missions.

        :param mode: mode of battles to start (all or one random).
        """
        if mode != self.MODE.ALL_BATTLES and mode != self.MODE.DAILY_RANDOM:
            logger.error(f"Squad Battles: got wrong mode for battles: {mode}.")
            return
        if not self.go_to_sb():
            logger.warning("Squad Battles: can't get in battles lobby.")
            return
        if mode == self.MODE.DAILY_RANDOM:
            battle_num = random.randint(1, 6)
            logger.info(f"Squad Battles: starting daily random battle with number: {battle_num}.")
            self.start_squad_battle(battle_num=f"SB_BATTLE_{battle_num}")
        if mode == self.MODE.ALL_BATTLES:
            logger.info(f"Squad Battles: starting all squad battles.")
            for battle_num in range(1, 7):
                logger.info(f"Squad Battles: starting battle with number: {battle_num}.")
                self.start_squad_battle(battle_num=f"SB_BATTLE_{battle_num}")
                if not self.press_repeat_button():
                    logger.error("Squad Battles: Something went wrong after clicking REPEAT button.")

    def end_missions(self, home_button="HOME"):
        """End missions."""
        if not self.game.is_main_menu():
            self.game.player.click_button(self.ui[home_button].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def start_squad_battle(self, battle_num):
        """Start selected squad battle.

        :param battle_num: number of the battle.
        """
        if self.select_squad_battle(squad_battle_ui=self.ui[battle_num]):
            self.press_start_button()
            AutoBattleBot(self.game).fight()
            self.close_after_battle_notifications()

    def select_squad_battle(self, squad_battle_ui):
        """Select squad battle.

        :param lib.ui.UIElement squad_battle_ui: battle UI to select.
        """
        self.player.click_button(squad_battle_ui.button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['SB_START_BUTTON'])

    def press_start_button(self, start_button_ui='SB_START_BUTTON'):
        """Press start button of the mission.

        :return: was button clicked.
        """
        self.player.click_button(self.ui[start_button_ui].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['SB_EMPTY_TEAM_NOTIFICATION']):
            logger.warning("Squad Battles: empty team notification. Deploying characters.")
            self.player.click_button(self.ui['SB_EMPTY_TEAM_NOTIFICATION'].button)
            time.sleep(2)
            self.deploy_characters()
            self.player.click_button(self.ui[start_button_ui].button)

    def press_repeat_button(self, repeat_button_ui='SB_REPEAT_BUTTON', start_button_ui=None):
        """Press repeat button of the mission."""
        self.player.click_button(self.ui[repeat_button_ui].button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=10, ui_element=self.ui['SB_LABEL'])

    def deploy_characters(self):
        """Deploy 3 characters to battle."""
        self.player.click_button(self.ui['SB_CHARACTER_1'].button)
        self.player.click_button(self.ui['SB_CHARACTER_2'].button)
        self.player.click_button(self.ui['SB_CHARACTER_3'].button)
