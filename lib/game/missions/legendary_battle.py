from lib.functions import wait_until, r_sleep
from lib.game.missions.missions import Missions
from lib.game.battle_bot import ManualBattleBot
import lib.logger as logging

logger = logging.get_logger(__name__)


class LegendaryBattle(Missions):
    """Class for working with Legendary Battle missions."""

    THOR_RAGNAROK = "THOR_RAGNAROK"
    BLACK_PANTHER = "BLACK_PANTHER"
    INFINITY_WAR = "INFINITY_WAR"
    ANT_MAN = "ANT_MAN"
    CAPTAIN_MARVEL = "CAPTAIN_MARVEL"

    class MODE:
        NORMAL = "NORMAL"
        EXTREME = "EXTREME"

    class STAGE:
        BATTLE_1 = "LB_BATTLE_STAGE_1"
        BATTLE_2 = "LB_BATTLE_STAGE_2"
        BATTLE_3 = "LB_BATTLE_STAGE_3"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'LB_LABEL')

    @property
    def battle_over_conditions(self):
        def score():
            return self.player.is_ui_element_on_screen(self.ui['LEGENDARY_SCORE'])

        return [score]

    def do_missions(self, times=None, battle=THOR_RAGNAROK, stage=STAGE.BATTLE_1, mode=MODE.NORMAL):
        """Do missions."""
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(battle=battle, stage=stage, mode=mode)
            self.end_missions()

    def start_missions(self, battle=THOR_RAGNAROK, stage=STAGE.BATTLE_1, mode=MODE.NORMAL):
        """Start Legendary Battle missions."""
        logger.info(f"Legendary battles: {self.stages} stages available")
        if self.stages > 0:
            if not self.go_to_stages_list():
                logger.error("Can't get to Legendary Battle stages, exiting.")
                return
            if not self.select_legendary_battle(battle=battle, mode=mode):
                logger.error("Can't select Legendary Battle, exiting.")
                return
            if not self.select_stage(stage=stage):
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

    def select_legendary_battle(self, battle, mode):
        """Select legendary battle.

        :param battle: name of the battle.
        :param mode: difficulty of legendary battle.
        """
        if mode != self.MODE.NORMAL and mode != self.MODE.EXTREME:
            logger.error(f"Legendary Battle: got wrong mode for battles: {mode}.")
            return False
        if battle not in [self.THOR_RAGNAROK, self.BLACK_PANTHER, self.ANT_MAN, self.INFINITY_WAR, self.CAPTAIN_MARVEL]:
            logger.error(f"Legendary Battle: got wrong battle: {battle}.")
            return False
        if battle == self.THOR_RAGNAROK:
            return self.select_legendary_battle_from_bottom(title=self.ui['LB_RAGNAROK_BATTLE_TITLE'],
                                                            battle=self.ui['LB_RAGNAROK_BATTLE'], mode=mode)
        if battle == self.BLACK_PANTHER:
            return self.select_legendary_battle_from_bottom(title=self.ui['LB_BLACK_PANTHER_BATTLE_TITLE'],
                                                            battle=self.ui['LB_BLACK_PANTHER_BATTLE'], mode=mode)
        if battle == self.INFINITY_WAR:
            return self.select_legendary_battle_from_bottom(title=self.ui['LB_INFINITY_WAR_BATTLE_TITLE'],
                                                            battle=self.ui['LB_INFINITY_WAR_BATTLE'], mode=mode)
        if battle == self.ANT_MAN:
            return self.select_legendary_battle_from_bottom(title=self.ui['LB_ANT_MAN_BATTLE_TITLE'],
                                                            battle=self.ui['LB_ANT_MAN_BATTLE'], mode=mode)
        if battle == self.CAPTAIN_MARVEL:
            return self.select_legendary_battle_from_bottom(title=self.ui['LB_CAPTAIN_MARVEL_BATTLE_TITLE'],
                                                            battle=self.ui['LB_CAPTAIN_MARVEL_BATTLE'], mode=mode)

    def select_mode(self, mode):
        """Select battle mode.

        :param mode: difficulty of legendary battle.
        """
        if mode == self.MODE.NORMAL:
            logger.debug(f"Legendary Battle: selecting {mode} mode.")
            if self.player.is_ui_element_on_screen(ui_element=self.ui['LB_DIFFICULTY_NORMAL']):
                self.player.click_button(self.ui['LB_DIFFICULTY_NORMAL'].button)
                return True
        if mode == self.MODE.EXTREME:
            logger.debug(f"Legendary Battle: selecting {mode} mode.")
            if self.player.is_ui_element_on_screen(ui_element=self.ui['LB_DIFFICULTY_EXTREME']):
                self.player.click_button(self.ui['LB_DIFFICULTY_EXTREME'].button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['LB_EXTREME_UPGRADE']):
                    logger.error(f"Legendary Battle: {mode} mode is unavailable, you need to buy it first.")
                    self.player.click_button(self.ui['LB_EXTREME_UPGRADE'].button)
                    return False
                return True

    def select_legendary_battle_from_bottom(self, title, battle, mode):
        """Select Legendary Battle from bottom of the list.

        :param UIElement title: title of legendary battle.
        :param UIElement battle: legendary battle.
        :param mode: difficulty of legendary battle.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=title):
            logger.debug(f"Legendary Battle: found selected {title.text}, entering with {mode} mode.")
            return self.select_mode(mode=mode)
        else:
            logger.debug(f"Legendary Battle: {title.text} isn't selected, trying to found it.")
            self.player.drag(self.ui['LB_DRAG_FROM'].button, self.ui['LB_DRAG_TO'].button)
            r_sleep(1)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=battle):
                logger.debug(f"Legendary Battle: found {title.text} battle. Selecting.")
                self.player.click_button(battle.button)
                return self.select_legendary_battle_from_bottom(title=title, battle=battle, mode=mode)
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
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['LB_NO_REWARD_NOTICE']):
                self.player.click_button(self.ui['LB_NO_REWARD_NOTICE'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['LB_IGNORE_NOTICE']):
                self.player.click_button(self.ui['LB_IGNORE_NOTICE'].button)
            return True
        return False
