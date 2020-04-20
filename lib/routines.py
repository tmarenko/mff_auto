from lib.functions import wait_until, is_strings_similar
from lib.missions import Missions
from lib.battle_bot import AutoBattleBot
from lib.ui import load_daily_trivia
import logging
import time

logger = logging.getLogger(__name__)


class DailyMissions(Missions):
    """Class for working with Daily Missions."""

    class DIFFICULTY:
        STAGE_1 = "DAILY_MISSION_DIFFICULTY_STAGE_1"
        STAGE_2 = "DAILY_MISSION_DIFFICULTY_STAGE_2"
        STAGE_3 = "DAILY_MISSION_DIFFICULTY_STAGE_3"
        STAGE_4 = "DAILY_MISSION_DIFFICULTY_STAGE_4"

    class MISSIONS:
        ISO_8_AND_NORN_STONES = "DAILY_MISSION_ISO_STAGE"
        GOLD_AND_EXP_CHIPS = "DAILY_MISSION_GOLD_STAGE"
        MKRAAN_SHARDS = "DAILY_MISSION_MKRAAN_STAGE"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'DAILY_MISSION_STAGE_LABEL')
        self.stages = super().stages

    def do_missions(self, stage=None, difficulty=None):
        """Do missions.

        :param stage: name of UI element that contains info about Special Mission stage.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        """
        if self.stages > 0:
            self.start_missions(stage=stage, difficulty=difficulty)
            self.end_missions()

    def start_missions(self, stage=None, difficulty=None):
        """Start Daily Mission.

        :param stage: name of UI element that contains info about Daily Mission stage.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        """
        self.game.select_mode(self.mode_name)
        logger.info(f"Daily Missions: {self.stages} stages available")
        if self.stages > 0:
            self.select_stage(stage=stage, difficulty=difficulty)
            while self.stages > 0 and self.is_stage_startable():
                if not self.press_start_button():
                    logger.error("Cannot start Daily Mission battle, exiting.")
                    return
                AutoBattleBot(self.game).fight()
                self.stages -= 1
                self.close_mission_notifications()
                if self.stages > 0:
                    self.press_repeat_button()
                else:
                    self.press_home_button(home_button='HOME_BUTTON_POSITION_3')
        logger.info("No more stages for Daily Missions.")

    def select_stage(self, stage, difficulty):
        """Select Daily Mission's stage.

        :param stage: name of UI element that contains info about Daily Mission stage.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DAILY_MISSION_STAGE_LABEL']):
            self.player.click_button(self.ui[stage].button)
            time.sleep(1)
            self.player.click_button(self.ui[difficulty].button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['START_BUTTON'])


class DailyTrivia:
    """Class for working with Daily Trivia."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.Game game: instance of the game.
        """
        self.game = game
        self.player = game.player
        self.ui = game.ui
        self.trivia = load_daily_trivia()

    def do_trivia(self):
        """Do trivia."""
        self.game.go_to_challenges()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DAILY_TRIVIA_STAGE']):
            self.player.click_button(self.ui['DAILY_TRIVIA_STAGE'].button)
            if not self.player.is_ui_element_on_screen(ui_element=self.ui['DAILY_TRIVIA_TODAY_TEXT']):
                logger.debug("Daily Trivia isn't started, starting it.")
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['DAILY_TRIVIA_START_BUTTON']):
                    self.player.click_button(self.ui['DAILY_TRIVIA_START_BUTTON'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['DAILY_TRIVIA_TODAY_TEXT']):
                logger.debug("Daily Trivia started, solving questions.")
                while wait_until(self.player.is_ui_element_on_screen, timeout=1,
                                 ui_element=self.ui['DAILY_TRIVIA_TODAY_TEXT']):
                    if not self.solve_trivia():
                        break
        self.game.go_to_main_menu()

    def solve_trivia(self):
        """Solve trivia question."""
        question = self.player.get_screen_text(ui_element=self.ui['DAILY_TRIVIA_QUESTION'])
        logger.debug(f"Found question: {question}")
        answers = [value for key, value in self.trivia.items() if is_strings_similar(question, key)]
        if answers:
            logger.debug(f"Found answers: {answers}, selecting.")
            for answer in answers:
                for i in range(1, 5):
                    available_answer_ui = self.ui[f'DAILY_TRIVIA_ANSWER_{i}']
                    available_answer = self.player.get_screen_text(ui_element=available_answer_ui)
                    logger.debug(f"Found available answer: {available_answer}.")
                    if is_strings_similar(answer, available_answer):
                        logger.debug(f"Found correct answer on UI element: {available_answer_ui.name}, clicking.")
                        self.player.click_button(available_answer_ui.button)
                        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                      ui_element=self.ui['DAILY_TRIVIA_CLOSE_ANSWER']):
                            self.player.click_button(self.ui['DAILY_TRIVIA_CLOSE_ANSWER'].button)
                            return True
                        else:
                            logger.error("Something went wrong after selecting correct answer.")
        logger.error(f"Can find answer for question: {question}")
        return False


class ShieldLab:

    def __init__(self, game):
        """Class initialization.

        :param lib.game.Game game: instance of the game.
        """
        self.game = game
        self.player = game.player
        self.ui = game.ui
        self.trivia = load_daily_trivia()

    def collect_antimatter(self):
        self.game.go_to_lab()
        if self.player.is_ui_element_on_screen(ui_element=self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_1']):
            logger.debug("Found COLLECT button with max lvl generator, collecting.")
            self.player.click_button(self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_1'].button)
        if self.player.is_ui_element_on_screen(ui_element=self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_2']):
            logger.debug("Found COLLECT button with not max lvl generator, collecting.")
            self.player.click_button(self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_2'].button)
        self.game.go_to_main_menu()
