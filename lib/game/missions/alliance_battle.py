from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.game import ui
from lib.functions import wait_until, r_sleep
import lib.logger as logging

logger = logging.get_logger(__name__)


class AllianceBattle(Missions):
    """Class for working with Alliance Battle."""

    class MODE:

        NORMAL = "NORMAL"
        ALL_BATTLES = "ALL_BATTLES"

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name="ALLIANCE BATTLE")

    @property
    def battle_over_conditions(self):
        def score():
            return self.emulator.is_ui_element_on_screen(ui.AB_YOUR_SCORE)

        def restart():
            if self.emulator.is_ui_element_on_screen(ui.AB_RESTART_CANCEL_BUTTON):
                logger.info("Lost battle.")
                self.emulator.click_button(ui.AB_RESTART_CANCEL_BUTTON)
                return True
            return False

        return [score, restart]

    def do_missions(self, mode=MODE.ALL_BATTLES):
        """Does missions."""
        if self.stages > 0:
            self.start_missions(mode=mode)
            self.end_missions()

    def start_missions(self, mode=MODE.ALL_BATTLES):
        """Starts Alliance Battles missions.

        :param str mode: mode of battles to start (all or normal).
        """
        if mode != self.MODE.ALL_BATTLES and mode != self.MODE.NORMAL:
            return logger.error(f"Got wrong mode for battles: {mode}.")
        if not self.open_alliance_battle():
            return logger.error("Can't get in battles lobby.")
        if mode == self.MODE.NORMAL:
            logger.info("Starting only NORMAL battle.")
            self._start_alliance_battle(start_button=ui.AB_NORMAL_START_BUTTON, home_or_next_button=ui.AB_HOME)
        if mode == self.MODE.ALL_BATTLES:
            logger.info("Starting ALL battles.")
            self._start_alliance_battle(start_button=ui.AB_NORMAL_START_BUTTON, home_or_next_button=ui.AB_NEXT_EXTREME)
            self.close_after_mission_notifications(timeout=7)
            self._start_alliance_battle(start_button=ui.AB_EXTREME_START_BUTTON, home_or_next_button=ui.AB_HOME)

    def open_alliance_battle(self):
        """Opens Alliance battle screen and select battle."""
        self.game.select_mode(self.mode_name)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.AB_NORMAL_READY_BUTTON):
            logger.debug("Found Normal Ready button, selecting.")
            self.emulator.click_button(ui.AB_NORMAL_READY_BUTTON)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.AB_NORMAL_START_BUTTON)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.AB_EXTREME_READY_BUTTON):
            logger.debug("Found Extreme Ready button, selecting.")
            self.emulator.click_button(ui.AB_EXTREME_READY_BUTTON)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.AB_EXTREME_START_BUTTON)
        return False

    def _start_alliance_battle(self, start_button, home_or_next_button):
        """Starts alliance battle.

        :param ui.UIElement start_button: start button UI.
        :param ui.UIElement home_or_next_button: next to extreme button or home button UI.
        """
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=10, ui_element=start_button):
            return logger.error(f"Cannot find START battle button: {start_button}")
        r_sleep(2)
        self._deploy_characters()
        self.emulator.click_button(start_button)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.AB_NO_CHARACTERS):
            logger.warning("No available 3 characters were found. Exiting.")
            return self.emulator.click_button(ui.AB_NO_CHARACTERS)
        ManualBattleBot(self.game, self.battle_over_conditions).fight()
        self.close_mission_notifications()
        self.emulator.click_button(home_or_next_button)

    def _deploy_characters(self):
        """Deploys 3 characters to battle."""

        def deploy_character(character_slot, character, additional_character):
            if self.emulator.is_image_on_screen(ui_element=character_slot):
                logger.debug(f"Deploying character {character}.")
                self.emulator.click_button(character)
                if self.emulator.is_image_on_screen(ui_element=character_slot):
                    logger.debug(f"Deploying additional character {additional_character}.")
                    self.emulator.click_button(additional_character)

        deploy_character(character_slot=ui.AB_NO_CHARACTER_MAIN, character=ui.AB_CHARACTER_1,
                         additional_character=ui.AB_CHARACTER_4)
        deploy_character(character_slot=ui.AB_NO_CHARACTER_LEFT, character=ui.AB_CHARACTER_2,
                         additional_character=ui.AB_CHARACTER_5)
        deploy_character(character_slot=ui.AB_NO_CHARACTER_RIGHT, character=ui.AB_CHARACTER_3,
                         additional_character=ui.AB_CHARACTER_6)
