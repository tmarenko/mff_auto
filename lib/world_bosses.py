from lib.battle_bot import ManualBattleBot
from lib.missions import Missions
from lib.functions import wait_until
import logging

logger = logging.getLogger(__name__)


class WorldBosses(Missions):
    """Class for working with World Bosses."""

    class MODE:

        BEGINNER = "BEGINNER"
        NORMAL = "NORMAL"
        ULTIMATE = "ULTIMATE"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'WB_LABEL')

    @property
    def battle_over_conditions(self):
        def score():
            return self.player.is_ui_element_on_screen(self.ui['WB_SCORE'])

        def respawn():
            return self.player.is_ui_element_on_screen(self.ui['WB_RESPAWN'])

        return [score, respawn]

    def do_missions(self, mode=MODE.ULTIMATE, difficulty=0):
        """Do missions."""
        if mode == self.MODE.ULTIMATE and difficulty == 0:
            logger.error(f"World Boss Ultimate: with mode {mode} difficulty should be greater than {difficulty}.")
            return
        if self.stages > 0:
            self.start_missions(mode=mode, difficulty=difficulty)
            self.end_missions()

    def go_to_wb(self):
        """Go to World Boss."""
        self.game.select_mode(self.mode_name)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_MISSION_BUTTON'])

    def start_missions(self, mode=MODE.ULTIMATE, difficulty=0):
        """Start World Boss battles.

        :param mode: mode of battles to start (beginner or normal or ultimate).
        :param difficulty: difficulty of Ultimate mode.
        """
        if mode != self.MODE.BEGINNER and mode != self.MODE.NORMAL and mode != self.MODE.ULTIMATE:
            logger.error(f"World Boss: got wrong mode for battles: {mode}.")
            return
        if not self.go_to_wb():
            logger.warning("World Boss: can't get in battles lobby.")
            return
        else:
            self.player.click_button(self.ui['WB_MISSION_BUTTON'].button)
        if mode == self.MODE.BEGINNER:
            logger.info(f"World Boss: starting BEGINNER battle.")
            self.player.click_button(self.ui['WB_BEGINNER_MODE'].button)
        if mode == self.MODE.NORMAL:
            logger.info(f"World Boss: starting NORMAL battle.")
            self.player.click_button(self.ui['WB_NORMAL_MODE'].button)
        if mode == self.MODE.ULTIMATE:
            logger.info(f"World Boss: starting ULTIMATE battle.")
            self.player.click_button(self.ui['WB_ULTIMATE_MODE'].button)
            self.select_stage_level(level_num=difficulty)

        deploy_characters = True
        while self.stages > 0:
            self.start_world_boss_battle(deploy_characters=deploy_characters)
            if self.player.is_ui_element_on_screen(ui_element=self.ui['WB_RESPAWN']):
                logger.info("World Boss: lost battle. Respawning.")
                self.player.click_button(self.ui['WB_RESPAWN'].button)
                if not wait_until(self.player.is_ui_element_on_screen, timeout=10, ui_element=self.ui['WB_SCORE']):
                    logger.warning("World Boss: something went wrong while respawning after lost battle.")
                deploy_characters = False
            else:
                self.stages -= 1
                deploy_characters = True
            if self.stages > 0:
                self.press_repeat_button(repeat_button_ui="WB_REPEAT_BUTTON", start_button_ui="WB_READY_BUTTON")
            else:
                self.press_home_button(home_button="WB_HOME_BUTTON")
        logger.info("No more stages for World Bosses.")

    def start_world_boss_battle(self, deploy_characters=False):
        """Start World Boss battle.

        :param: deploy characters or not.
        """
        self.player.click_button(self.ui['WB_READY_BUTTON'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_SET_TEAM']):
            if deploy_characters:
                self.player.click_button(self.ui['WB_CHARACTER_FILTER'].button, min_duration=1, max_duration=1)
                # selecting ALL filter for top characters
                self.player.click_button(self.ui['WB_CHARACTER_FILTER'].button, min_duration=1, max_duration=1)
                self.deploy_characters()
            self.player.click_button(self.ui['WB_SET_TEAM'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_START_BUTTON']):
                if deploy_characters:
                    self.deploy_allies()
                self.player.click_button(self.ui['WB_START_BUTTON'].button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['WB_NOT_FULL_ALLY_TEAM']):
                    self.player.click_button(self.ui['WB_NOT_FULL_ALLY_TEAM'].button)
                    ManualBattleBot(self.game, self.battle_over_conditions).fight(move_around=True)
                    self.close_mission_notifications()

    def deploy_characters(self):
        """Deploy 3 characters to battle."""
        self.player.click_button(self.ui['WB_NON_FEATURED_CHARACTER_1'].button)
        self.player.click_button(self.ui['WB_NON_FEATURED_CHARACTER_2'].button)
        self.player.click_button(self.ui['WB_NON_FEATURED_CHARACTER_3'].button)

    def deploy_allies(self):
        """Deploy 4 characters as allies to battle."""
        self.player.click_button(self.ui['WB_ALLY_CHARACTER_1'].button)
        self.player.click_button(self.ui['WB_ALLY_CHARACTER_2'].button)
        self.player.click_button(self.ui['WB_ALLY_CHARACTER_3'].button)
        self.player.click_button(self.ui['WB_ALLY_CHARACTER_4'].button)

    @property
    def stage_level(self):
        """Get current stage level.

        :return: current stage level.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_READY_BUTTON']):
            stage_str = self.player.get_screen_text(ui_element=self.ui['WB_ULTIMATE_STAGE'])
            try:
                stage_int = int(stage_str)
            except ValueError:
                logger.critical(f"World Boss: cannot convert stage to integer: {stage_str}")
                stage_int = 0
            return stage_int
        return 0

    def increase_stage_level(self):
        """Increase current stage level"""
        logger.info("World Boss Ultimate: increasing stage difficulty level.")
        self.player.click_button(self.ui['WB_ULTIMATE_PLUS'].button, min_duration=0.01, max_duration=0.01)

    def decrease_stage_level(self):
        """Decrease current stage level"""
        logger.info("World Boss Ultimate: decreasing stage difficulty level.")
        self.player.click_button(self.ui['WB_ULTIMATE_MINUS'].button, min_duration=0.01, max_duration=0.01)

    def select_stage_level(self, level_num=20):
        """Select stage level.

        :param level_num: level to select.
        """
        if level_num == 0:
            logger.debug(f"Stage level is {level_num}. Stage won't change.")
        if level_num > 99 or level_num < 0:
            logger.error(f"World Boss Ultimate: stage level should be between 1 and 99, got {level_num} instead.")
            return
        safe_counter = 0
        diff = abs(level_num - self.stage_level)
        while self.stage_level != level_num:
            if safe_counter > diff:
                logger.warning(f"World Boss Ultimate: stage level was changed more than {safe_counter}. "
                               f"Your max stage level probably lesser than {level_num}.")
                break
            safe_counter += 1
            if self.stage_level > level_num:
                self.decrease_stage_level()
            if self.stage_level < level_num:
                self.increase_stage_level()
