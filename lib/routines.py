from lib.functions import wait_until, is_strings_similar
from lib.missions import Missions
from lib.battle_bot import AutoBattleBot
from lib.ui import load_daily_trivia
import logging
import time

logger = logging.getLogger(__name__)


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
