from lib.functions import wait_until, r_sleep
from lib.game.missions.missions import Missions
from lib.game.battle_bot import AutoBattleBot
from lib.game import ui
import lib.logger as logging
import random

logger = logging.get_logger(__name__)


class SquadBattle(Missions):
    """Class for working with Squad Battle missions."""

    class MODE:

        ALL_BATTLES = "ALL_BATTLES"
        DAILY_RANDOM = "DAILY_RANDOM"

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='SQUAD BATTLE')

    @property
    def battle_over_conditions(self):
        def rank():
            return self.emulator.is_ui_element_on_screen(ui.SB_RANK_CHANGED_1)

        def points():
            return self.emulator.is_ui_element_on_screen(ui.SB_BATTLE_POINTS)

        return [rank, points]

    def open_squad_battle(self):
        """Opens Squad Battles mission lobby.

        :return: is Squad Battle open or not.
        :rtype: bool
        """
        self.game.find_mode_on_content_status_board(self.mode_name)
        self.game.select_mode(self.mode_name)
        self.game.close_ads(timeout=5)
        self.close_squad_battle_after_battle_notifications()
        if not self.emulator.is_ui_element_on_screen(ui_element=ui.SB_LABEL):
            self.emulator.click_button(ui.SB_RANK_CHANGED_2)
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SB_LABEL)

    def do_missions(self, mode=MODE.DAILY_RANDOM):
        """Does missions."""
        self.start_missions(mode=mode)
        self.end_missions(home_button=ui.SB_HOME_BUTTON if mode == self.MODE.DAILY_RANDOM else ui.HOME)

    def start_missions(self, mode=MODE.DAILY_RANDOM):
        """Starts Squad Battles missions.

        :param str mode: mode of battles to start (all or one random).
        """
        if mode != self.MODE.ALL_BATTLES and mode != self.MODE.DAILY_RANDOM:
            return logger.error(f"Got wrong mode for battles: {mode}.")
        if not self.open_squad_battle():
            return logger.error("Can't get in battles lobby.")
        if mode == self.MODE.DAILY_RANDOM:
            battle_num = random.randint(1, 6)
            logger.info(f"Starting daily random battle with number: {battle_num}.")
            self._start_squad_battle(battle_name=f"SB_BATTLE_{battle_num}")
        if mode == self.MODE.ALL_BATTLES:
            logger.info("Starting all squad battles.")
            for battle_num in range(1, 7):
                logger.info(f"Starting battle with number: {battle_num}.")
                self._start_squad_battle(battle_name=f"SB_BATTLE_{battle_num}")
                self.press_repeat_button()

    def end_missions(self, home_button=ui.HOME):
        """Ends missions."""
        if not self.game.is_main_menu():
            self.game.emulator.click_button(home_button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def _start_squad_battle(self, battle_name):
        """Starts selected squad battle.

        :param str battle_name: number of the battle.
        """
        battle_ui = ui.get_by_name(battle_name)
        if self._select_squad_battle(squad_battle_ui=battle_ui):
            if not self.press_start_button():
                return self.end_missions()
            AutoBattleBot(self.game, self.battle_over_conditions).fight()
            self.close_squad_battle_after_battle_notifications()

    def _select_squad_battle(self, squad_battle_ui):
        """Selects squad battle.

        :param ui.UIElement squad_battle_ui: battle UI to select.
        """
        self.emulator.click_button(squad_battle_ui)
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SB_START_BUTTON)

    def press_start_button(self, start_button_ui=ui.SB_START_BUTTON):
        """Presss start button of the mission."""
        self.emulator.click_button(start_button_ui)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SB_EMPTY_TEAM_NOTIFICATION):
            logger.warning("Empty team notification. Deploying characters.")
            self.emulator.click_button(ui.SB_EMPTY_TEAM_NOTIFICATION)
            r_sleep(2)
            self._deploy_characters()
            self.emulator.click_button(start_button_ui)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SB_EMPTY_TEAM_NOTIFICATION):
                logger.warning("Empty team notification again. Not enough characters for battle.")
                self.emulator.click_button(ui.SB_EMPTY_TEAM_NOTIFICATION)
                self.emulator.click_button(ui.SB_CLOSE_SET_SQUAD)
                return False
        return True

    def press_repeat_button(self, repeat_button_ui=ui.SB_REPEAT_BUTTON, start_button_ui=None):
        """Presses repeat button of the mission."""
        self.emulator.click_button(repeat_button_ui)
        while any([condition() for condition in self.battle_over_conditions]):
            self.emulator.click_button(repeat_button_ui, min_duration=1, max_duration=1)
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=10, ui_element=ui.SB_LABEL):
            logger.error(f"Something went wrong after clicking REPEAT button with UI element: {repeat_button_ui}.")

    def _deploy_characters(self):
        """Deploys 3 characters to battle."""
        no_main = self.emulator.is_image_on_screen(ui_element=ui.SB_NO_CHARACTER_MAIN)
        no_left = self.emulator.is_image_on_screen(ui_element=ui.SB_NO_CHARACTER_LEFT)
        no_right = self.emulator.is_image_on_screen(ui_element=ui.SB_NO_CHARACTER_RIGHT)
        if no_main:
            self.emulator.click_button(ui.SB_CHARACTER_1)
        if no_left:
            self.emulator.click_button(ui.SB_CHARACTER_2)
        if no_right:
            self.emulator.click_button(ui.SB_CHARACTER_3)
