import json
import lib.logger as logging
from random import randint
from lib.game.notifications import Notifications
from lib.functions import wait_until, is_strings_similar

logger = logging.get_logger(__name__)


class DailyTrivia(Notifications):
    """Class for working with Daily Trivia."""

    @staticmethod
    def load_daily_trivia(path="settings/daily_trivia.json"):
        """Load daily trivia's questions and answers.

        :param path: path to settings.

        :return: dictionary of questions and answers.
        """
        with open(path, encoding='utf-8') as json_data:
            return json.load(json_data)

    def __init__(self, game):
        """Class initialization.

        :param lib.game.Game game: instance of the game.
        """
        super().__init__(game)
        self.trivia = self.load_daily_trivia()

    def do_trivia(self):
        """Do trivia."""
        self.game.go_to_challenges()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DAILY_TRIVIA_STAGE']):
            self.emulator.click_button(self.ui['DAILY_TRIVIA_STAGE'].button)
            if not self.emulator.is_ui_element_on_screen(ui_element=self.ui['DAILY_TRIVIA_TODAY_TEXT']):
                logger.debug("Daily Trivia isn't started, starting it.")
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['DAILY_TRIVIA_START_BUTTON']):
                    self.emulator.click_button(self.ui['DAILY_TRIVIA_START_BUTTON'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['DAILY_TRIVIA_TODAY_TEXT']):
                logger.debug("Daily Trivia started, solving questions.")
                while wait_until(self.emulator.is_ui_element_on_screen, timeout=1,
                                 ui_element=self.ui['DAILY_TRIVIA_TODAY_TEXT']):
                    if not self.solve_trivia():
                        break
        self.game.go_to_main_menu()

    def solve_trivia(self):
        """Solve trivia question."""
        question = self.emulator.get_screen_text(ui_element=self.ui['DAILY_TRIVIA_QUESTION'])
        logger.debug(f"Found question: {question}")
        answers = [value for key, value in self.trivia.items() if is_strings_similar(question, key)]
        if not answers:
            logger.error(f"Can find answer for question: {question}")
            return False
        logger.debug(f"Found answers: {answers}, selecting.")
        for answer in answers:
            for i in range(1, 5):
                available_answer_ui = self.ui[f'DAILY_TRIVIA_ANSWER_{i}']
                available_answer = self.emulator.get_screen_text(ui_element=available_answer_ui)
                logger.debug(f"Found available answer: {available_answer}.")
                if is_strings_similar(answer, available_answer):
                    logger.debug(f"Found correct answer on UI element: {available_answer_ui.name}, clicking.")
                    self.emulator.click_button(available_answer_ui.button)
                    return self.close_daily_trivia_answer_notification()
        else:
            logger.error("No available answers was found for trivia question.")
            random_answer = randint(1, 4)
            random_answer_ui = self.ui[f'DAILY_TRIVIA_ANSWER_{random_answer}']
            logger.warning(f"Selecting random answer: {random_answer}.")
            self.emulator.click_button(random_answer_ui.button)
            return self.close_daily_trivia_answer_notification()


class DailyRewards(Notifications):
    """Class for working Daily rewards."""

    def acquire_all_daily_rewards(self):
        self.game.go_to_challenges()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DAILY_REWARDS_TAB']):
            self.emulator.click_button(self.ui['DAILY_REWARDS_TAB'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['DAILY_REWARDS_ACQUIRE_ALL_BUTTON']):
                logger.debug("Acquiring daily rewards.")
                self.emulator.click_button(self.ui['DAILY_REWARDS_ACQUIRE_ALL_BUTTON'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=1,
                              ui_element=self.ui['DAILY_REWARDS_ACQUIRE_ALL_CLOSE']):
                    logger.info("Daily rewards acquired, exiting.")
                    self.emulator.click_button(self.ui['DAILY_REWARDS_ACQUIRE_ALL_CLOSE'].button)
                    return True
            else:
                logger.debug("No rewards to acquire.")
        self.game.go_to_main_menu()
