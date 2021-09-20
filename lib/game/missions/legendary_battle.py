from lib.functions import wait_until, r_sleep
from lib.game.missions.missions import Missions
from lib.game.battle_bot import ManualBattleBot
from lib.game import ui
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
        super().__init__(game, mode_name='LEGENDARY BATTLE')

    @property
    def battle_over_conditions(self):
        def score():
            return self.emulator.is_ui_element_on_screen(ui.LEGENDARY_SCORE)

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
        logger.info(f"{self.stages} stages available")
        if self.stages > 0:
            if not self.open_legendary_battle():
                logger.warning("Can't get in battles lobby.")
                return
            if not self._select_legendary_battle(battle=battle, mode=mode):
                logger.error(f"Can't select battle {battle}, exiting.")
                return
            if not self._select_stage(stage=stage):
                logger.error(f"Can't select stage {stage} of the battle, exiting.")
                return
            while self.stages > 0:
                if not self.press_start_button():
                    return
                ManualBattleBot(self.game, self.battle_over_conditions).fight()
                self.stages -= 1
                if self.stages > 0:
                    self.press_repeat_button(repeat_button_ui=ui.LB_REPEAT_BUTTON, start_button_ui=ui.LB_START_BUTTON)
            self.press_home_button(home_button=ui.LB_HOME_BUTTON)
        logger.info("No more stages.")

    def open_legendary_battle(self):
        """Go to Legendary Battle stages list screen."""
        self.game.select_mode(self.mode_name)
        legendary_home = wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.LB_MENU_LABEL)
        difficulty_on_screen = wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.LB_DIFFICULTY_NORMAL)
        return legendary_home and difficulty_on_screen

    def _select_legendary_battle(self, battle, mode):
        """Select legendary battle.

        :param battle: name of the battle.
        :param mode: difficulty of legendary battle.
        """
        if mode != self.MODE.NORMAL and mode != self.MODE.EXTREME:
            logger.error(f"Got wrong mode for battles: {mode}.")
            return False
        if battle not in [self.THOR_RAGNAROK, self.BLACK_PANTHER, self.ANT_MAN, self.INFINITY_WAR, self.CAPTAIN_MARVEL]:
            logger.error(f"Got wrong battle: {battle}.")
            return False
        if battle == self.THOR_RAGNAROK:
            return self._select_legendary_battle_from_bottom(title=ui.LB_RAGNAROK_BATTLE_TITLE,
                                                             battle=ui.LB_RAGNAROK_BATTLE, mode=mode)
        if battle == self.BLACK_PANTHER:
            return self._select_legendary_battle_from_bottom(title=ui.LB_BLACK_PANTHER_BATTLE_TITLE,
                                                             battle=ui.LB_BLACK_PANTHER_BATTLE, mode=mode)
        if battle == self.INFINITY_WAR:
            return self._select_legendary_battle_from_bottom(title=ui.LB_INFINITY_WAR_BATTLE_TITLE,
                                                             battle=ui.LB_INFINITY_WAR_BATTLE, mode=mode)
        if battle == self.ANT_MAN:
            return self._select_legendary_battle_from_bottom(title=ui.LB_ANT_MAN_BATTLE_TITLE,
                                                             battle=ui.LB_ANT_MAN_BATTLE, mode=mode)
        if battle == self.CAPTAIN_MARVEL:
            return self._select_legendary_battle_from_bottom(title=ui.LB_CAPTAIN_MARVEL_BATTLE_TITLE,
                                                             battle=ui.LB_CAPTAIN_MARVEL_BATTLE, mode=mode)

    def _select_battle_mode(self, mode):
        """Select battle mode.

        :param mode: difficulty of legendary battle.
        """
        if mode == self.MODE.NORMAL:
            if self.emulator.is_ui_element_on_screen(ui_element=ui.LB_DIFFICULTY_NORMAL):
                logger.debug(f"Selecting {mode} mode.")
                self.emulator.click_button(ui.LB_DIFFICULTY_NORMAL)
                return True
        if mode == self.MODE.EXTREME:
            if self.emulator.is_ui_element_on_screen(ui_element=ui.LB_DIFFICULTY_EXTREME):
                logger.debug(f"Selecting {mode} mode.")
                self.emulator.click_button(ui.LB_DIFFICULTY_EXTREME)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.LB_EXTREME_UPGRADE):
                    logger.error(f"{mode} mode is unavailable, you need to buy it first.")
                    self.emulator.click_button(ui.LB_EXTREME_UPGRADE)
                    return False
                return True

    def _select_legendary_battle_from_bottom(self, title, battle, mode):
        """Select Legendary Battle from bottom of the list.

        :param UIElement title: title of legendary battle.
        :param UIElement battle: legendary battle.
        :param mode: difficulty of legendary battle.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=title):
            logger.debug(f"Found selected {title.text}, entering with {mode} mode.")
            return self._select_battle_mode(mode=mode)
        else:
            logger.debug(f"{title.text} isn't selected, trying to found it.")
            self.emulator.drag(ui.LB_DRAG_FROM, ui.LB_DRAG_TO)
            r_sleep(1)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=battle):
                logger.debug(f"Found {title.text} battle. Selecting.")
                self.emulator.click_button(battle)
                return self._select_legendary_battle_from_bottom(title=title, battle=battle, mode=mode)
        return False

    def _select_stage(self, stage):
        """Select stage of the battle."""
        stage_ui = ui.get_by_name(stage)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=stage_ui):
            self.emulator.click_button(stage_ui)
            return True
        return False

    def press_start_button(self, start_button_ui=ui.LB_START_BUTTON):
        """Press start button of the mission."""
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=start_button_ui):
            r_sleep(1)  # Sometimes it's need time for enabling
            self.emulator.click_button(start_button_ui)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.LB_NO_REWARD_NOTICE):
                self.emulator.click_button(ui.LB_NO_REWARD_NOTICE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.LB_IGNORE_NOTICE):
                self.emulator.click_button(ui.LB_IGNORE_NOTICE)
            return True
        logger.error(f"Can't find {start_button_ui} button.")
        return False
