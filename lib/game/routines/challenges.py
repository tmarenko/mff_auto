import lib.logger as logging
from random import randint
from lib.game.data.daily_trivia import trivia_qa
from lib.game.notifications import Notifications
from lib.game import ui
from lib.functions import wait_until, is_strings_similar

logger = logging.get_logger(__name__)


class DailyTrivia(Notifications):
    """Class for working with Daily Trivia."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game)
        self.trivia = trivia_qa

    def do_trivia(self):
        """Does trivia."""
        self.game.go_to_challenges()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_TRIVIA_STAGE):
            self.emulator.click_button(ui.DAILY_TRIVIA_STAGE)
            if not self.emulator.is_ui_element_on_screen(ui_element=ui.DAILY_TRIVIA_TODAY_TEXT):
                logger.debug("Daily Trivia isn't started, starting it.")
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_TRIVIA_START_BUTTON):
                    self.emulator.click_button(ui.DAILY_TRIVIA_START_BUTTON)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_TRIVIA_TODAY_TEXT):
                logger.debug("Daily Trivia started, solving questions.")
                while wait_until(self.emulator.is_ui_element_on_screen, timeout=1,
                                 ui_element=ui.DAILY_TRIVIA_TODAY_TEXT):
                    if not self.solve_trivia():
                        break
        self.game.go_to_main_menu()

    def solve_trivia(self):
        """Solves trivia question."""
        question = self.emulator.get_screen_text(ui_element=ui.DAILY_TRIVIA_QUESTION)
        logger.debug(f"Found question: {question}")
        answers = [value for key, value in self.trivia.items() if is_strings_similar(question, key)]
        if not answers:
            logger.error(f"Can find answer for question: {question}")
            return False
        logger.debug(f"Found answers: {answers}, selecting.")
        for answer in answers:
            for i in range(1, 5):
                available_answer_ui = ui.get_by_name(f'DAILY_TRIVIA_ANSWER_{i}')
                available_answer = self.emulator.get_screen_text(ui_element=available_answer_ui)
                logger.debug(f"Found available answer: {available_answer}.")
                if is_strings_similar(answer, available_answer):
                    logger.debug(f"Found correct answer on UI element: {available_answer_ui}, clicking.")
                    self.emulator.click_button(available_answer_ui)
                    return self.close_daily_trivia_answer_notification()
        else:
            logger.error("No available answers was found for trivia question.")
            random_answer_ui = ui.get_by_name(f'DAILY_TRIVIA_ANSWER_{randint(1, 4)}')
            logger.warning(f"Selecting random answer: {random_answer_ui}.")
            self.emulator.click_button(random_answer_ui)
            return self.close_daily_trivia_answer_notification()


class DailyRewards(Notifications):
    """Class for working Daily rewards."""

    def acquire_all_daily_rewards(self):
        """Acquired all available daily rewards from Daily Challenges."""
        self.game.go_to_challenges()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_REWARDS_TAB):
            self.emulator.click_button(ui.DAILY_REWARDS_TAB)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_REWARDS_ACQUIRE_ALL_BUTTON):
                logger.debug("Acquiring daily rewards.")
                self.emulator.click_button(ui.DAILY_REWARDS_ACQUIRE_ALL_BUTTON)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=1,
                              ui_element=ui.DAILY_REWARDS_ACQUIRE_ALL_CLOSE):
                    logger.info("Daily rewards acquired, exiting.")
                    self.emulator.click_button(ui.DAILY_REWARDS_ACQUIRE_ALL_CLOSE)
            else:
                logger.debug("No rewards to acquire.")
        self.game.go_to_main_menu()

    def acquire_all_weekly_rewards(self):
        """Acquired all available weekly rewards from Daily Challenges."""
        self.game.go_to_challenges()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_REWARDS_TAB):
            self.emulator.click_button(ui.DAILY_REWARDS_TAB)
            for reward_num in range(1, 6):
                reward_ui = ui.get_by_name(f"DAILY_REWARDS_ACQUIRE_WEEKLY_{reward_num}")
                self.emulator.click_button(reward_ui)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_REWARDS_ACQUIRE_WEEKLY_CLOSE):
                    logger.info(f"Weekly reward #{reward_num} acquired.")
                    self.emulator.click_button(ui.DAILY_REWARDS_ACQUIRE_WEEKLY_CLOSE)
        self.game.go_to_main_menu()
