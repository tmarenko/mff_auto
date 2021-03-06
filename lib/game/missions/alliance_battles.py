from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, r_sleep
import lib.logger as logging

logger = logging.get_logger(__name__)


class AllianceBattles(Missions):
    """Class for working with Alliance Battles."""

    class MODE:

        NORMAL = "NORMAL"
        ALL_BATTLES = "ALL_BATTLES"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'AB_LABEL')

    @property
    def battle_over_conditions(self):
        def score():
            return self.player.is_ui_element_on_screen(self.ui['AB_YOUR_SCORE'])

        def restart():
            if self.player.is_ui_element_on_screen(self.ui['AB_RESTART_CANCEL_BUTTON']):
                self.player.click_button(self.ui['AB_RESTART_CANCEL_BUTTON'].button)
                return True
            return False

        return [score, restart]

    def do_missions(self, mode=MODE.ALL_BATTLES):
        """Do missions."""
        if self.stages > 0:
            self.start_missions(mode=mode)
            self.end_missions()

    def start_missions(self, mode=MODE.ALL_BATTLES):
        """Start Alliance Battles missions.

        :param mode: mode of battles to start (all or normal).
        """
        if mode != self.MODE.ALL_BATTLES and mode != self.MODE.NORMAL:
            logger.error(f"Alliance Battles: got wrong mode for battles: {mode}.")
            return
        if not self.go_to_alliance_battle():
            logger.warning("Alliance Battles: can't get in battles lobby.")
            return
        if mode == self.MODE.NORMAL:
            logger.info("Alliance Battles: starting only NORMAL battle.")
            self.start_alliance_battle(start_button='AB_NORMAL_START_BUTTON', home_or_next_button='AB_HOME')
        if mode == self.MODE.ALL_BATTLES:
            logger.info("Alliance Battles: starting ALL battles.")
            self.start_alliance_battle(start_button='AB_NORMAL_START_BUTTON', home_or_next_button='AB_NEXT_EXTREME')
            self.close_after_mission_notifications(timeout=7)
            self.start_alliance_battle(start_button='AB_EXTREME_START_BUTTON', home_or_next_button='AB_HOME')

    def go_to_alliance_battle(self):
        """Go to Alliance battle screen and select battle."""
        self.game.select_mode(self.mode_name)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['AB_NORMAL_READY_BUTTON']):
            self.player.click_button(self.ui['AB_NORMAL_READY_BUTTON'].button)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['AB_NORMAL_START_BUTTON'])
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['AB_EXTREME_READY_BUTTON']):
            self.player.click_button(self.ui['AB_EXTREME_READY_BUTTON'].button)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['AB_EXTREME_START_BUTTON'])
        return False

    def start_alliance_battle(self, start_button, home_or_next_button):
        """Start alliance battle.

        :param start_button: start button UI.
        :param home_or_next_button: next to extreme button or home button UI.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=10, ui_element=self.ui[start_button]):
            r_sleep(2)
            self.deploy_characters()
            self.player.click_button(self.ui[start_button].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['AB_NO_CHARACTERS']):
                logger.warning("Alliance Battle: no available 3 characters were found. Exiting.")
                self.player.click_button(self.ui['AB_NO_CHARACTERS'].button)
                return
            ManualBattleBot(self.game, self.battle_over_conditions).fight()
            self.close_mission_notifications()
            self.player.click_button(self.ui[home_or_next_button].button)
        else:
            logger.warning(f"Cannot find START battle button: {start_button}")

    def deploy_characters(self):
        """Deploy 3 characters to battle."""
        def deploy_character(character_slot, character, additional_character):
            if self.player.is_image_on_screen(ui_element=self.ui[character_slot]):
                logger.debug(f"Deploying character {character}.")
                self.player.click_button(self.ui[character].button)
                if self.player.is_image_on_screen(ui_element=self.ui[character_slot]):
                    logger.debug(f"Deploying additional character {additional_character}.")
                    self.player.click_button(self.ui[additional_character].button)

        deploy_character(character_slot='AB_NO_CHARACTER_MAIN', character='AB_CHARACTER_1',
                         additional_character='AB_CHARACTER_4')
        deploy_character(character_slot='AB_NO_CHARACTER_LEFT', character='AB_CHARACTER_2',
                         additional_character='AB_CHARACTER_5')
        deploy_character(character_slot='AB_NO_CHARACTER_RIGHT', character='AB_CHARACTER_3',
                         additional_character='AB_CHARACTER_6')
