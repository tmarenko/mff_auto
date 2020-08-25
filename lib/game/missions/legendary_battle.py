from lib.functions import wait_until, r_sleep
from lib.game.missions.missions import Missions
from lib.game.battle_bot import ManualBattleBot
import lib.logger as logging

logger = logging.get_logger(__name__)


class LegendaryBattle(Missions):
    """Class for working with Legendary Battle missions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'LB_LABEL')
        self.ui['LB_RAGNAROK_BATTLE'].scale = 3

    @property
    def battle_over_conditions(self):
        def score():
            return self.player.is_ui_element_on_screen(self.ui['LEGENDARY_SCORE'])

        return [score]

    def start_missions(self):
        """Start Legendary Battle missions."""
        logger.info(f"Legendary battles: {self.stages} stages available")
        if self.stages > 0:
            if not self.go_to_stages_list():
                logger.error("Can't get to Legendary Battle stages, exiting.")
                return
            if not self.select_ragnarok_battle():
                logger.error("Can't select Ragnarok Battle, exiting.")
                return
            if not self.select_stage('LB_BATTLE_STAGE_1'):
                logger.error("Can't select first stage of the battle, exiting.")
                return
            while self.stages > 0:
                if not self.press_start_button():
                    logger.error("Cannot start legendary battle, exiting")
                    return
                ManualBattleBot(self.game, self.battle_over_conditions).fight()
                self.stages -= 1
                if self.stages > 0:
                    self.press_repeat_button(repeat_button_ui='LB_REPEAT_BUTTON', start_button_ui='LB_START_BUTTON')
            self.press_home_button(home_button='LB_HOME_BUTTON')
        logger.info("No more stages for legendary battles.")

    def go_to_stages_list(self):
        """Go to Legendary Battle stages list screen."""
        self.game.select_mode(self.mode_name)
        legendary_home = wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['LB_MENU_LABEL'])
        difficulty_on_screen = wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                          ui_element=self.ui['LB_DIFFICULTY_NORMAL'])
        return legendary_home and difficulty_on_screen

    def select_ragnarok_battle(self):
        """Select RAGNAROK battle with NORMAL difficulty."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=2, ui_element=self.ui['LB_RAGNAROK_BATTLE_TITLE']):
            logger.debug("Found selected Ragnarok Battle, entering.")
            self.player.click_button(self.ui['LB_DIFFICULTY_NORMAL'].button)
            return True
        else:
            logger.debug("Ragnarok Battle isn't selecting, trying to found it.")
            self.player.drag(self.ui['LB_DRAG_FROM'].button, self.ui['LB_DRAG_TO'].button)
            r_sleep(1)
            if wait_until(self.player.is_ui_element_on_screen, timeout=2, ui_element=self.ui['LB_RAGNAROK_BATTLE']):
                logger.debug("Found RAGNAROK battle. Selecting and entering.")
                self.player.click_button(self.ui['LB_RAGNAROK_BATTLE'].button)
                return self.select_ragnarok_battle()
        return False

    def select_stage(self, stage):
        """Select stage of the battle."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui[stage]):
            self.player.click_button(self.ui[stage].button)
            return True
        return False

    def press_start_button(self, start_button_ui='LB_START_BUTTON'):
        """Press start button of the mission."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui[start_button_ui]):
            self.player.click_button(self.ui[start_button_ui].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['LB_IGNORE_NOTICE']):
                self.player.click_button(self.ui['LB_IGNORE_NOTICE'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['LB_NO_REWARD_NOTICE']):
                self.player.click_button(self.ui['LB_NO_REWARD_NOTICE'].button)
            return True
        return False
