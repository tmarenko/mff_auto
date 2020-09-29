import lib.logger as logging
from math import ceil
from lib.functions import wait_until, is_strings_similar, r_sleep
from lib.game.ui import load_daily_trivia

logger = logging.get_logger(__name__)


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
                            notification_closed = wait_until(self.game.close_complete_challenge_notification, timeout=3)
                            logger.debug(f"Complete challenge notifications was closed: {notification_closed}")
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

    def collect_antimatter(self):
        self.game.go_to_lab()
        r_sleep(1)  # Wait for button's animation
        if self.player.is_ui_element_on_screen(ui_element=self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_1']):
            logger.debug("Found COLLECT button with max lvl generator, collecting.")
            self.player.click_button(self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_1'].button)
        if self.player.is_ui_element_on_screen(ui_element=self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_2']):
            logger.debug("Found COLLECT button with not max lvl generator, collecting.")
            self.player.click_button(self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_2'].button)
        self.game.go_to_main_menu()


class EnhancePotential:
    """Class for working with character's potential enhancement."""

    COSMIC_CUBE_FRAGMENT = "COSMIC_CUBE_FRAGMENT"
    BLACK_ANTI_MATTER = "BLACK_ANTI_MATTER"
    NORN_STONE_OF_CHAOS = "NORN_STONE_OF_CHAOS"

    def __init__(self, game):
        """Class initialization.

        :param lib.game.Game game: instance of the game.
        """
        self.game = game
        self.player = game.player
        self.ui = game.ui

    @property
    def success_rate(self):
        """Returns Success Rate number of enhancement."""
        success_rate_text = self.player.get_screen_text(ui_element=self.ui['ENHANCE_POTENTIAL_RATE'])
        success_rate = success_rate_text.replace("%", "").replace(" ", "")
        return float(success_rate)

    def apply_material(self, material, click_speed=0.02):
        """Apply material to enhancement.

        :param material: name of the material.
        :param click_speed: clicking speed of applying.
        """
        if material == self.COSMIC_CUBE_FRAGMENT:
            self.player.click_button(self.ui['ENHANCE_POTENTIAL_COSMIC_CUBES'].button, click_speed, click_speed)
        if material == self.BLACK_ANTI_MATTER:
            self.player.click_button(self.ui['ENHANCE_POTENTIAL_ANTI_MATTER'].button, click_speed, click_speed)
        if material == self.NORN_STONE_OF_CHAOS:
            self.player.click_button(self.ui['ENHANCE_POTENTIAL_NORN_STONES'].button, click_speed, click_speed)

    def press_upgrade(self):
        """Press Upgrade button to enhance potential.

        :return: was button pressed successful or not.
        """
        if wait_until(self.player.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_UPGRADE'],
                      timeout=3):
            logger.debug(f"Upgrading potential with rate: {self.success_rate}.")
            self.player.click_button(self.ui['ENHANCE_POTENTIAL_UPGRADE'].button)
            if wait_until(self.player.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_UPGRADE_OK'],
                          timeout=3):
                self.player.click_button(self.ui['ENHANCE_POTENTIAL_UPGRADE_OK'].button)
                return True
        logger.warning("Can't find Upgrade button to click.")
        return False

    def check_enhance_success(self):
        """Check enhancement result.

        :return: was enhancement successful or not.
        """
        if wait_until(self.player.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_FAILED'],
                      timeout=3):
            logger.debug("Enhance Potential failed.")
            self.player.click_button(self.ui['ENHANCE_POTENTIAL_FAILED'].button, min_duration=1, max_duration=1.5)
            return False
        if wait_until(self.player.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_SUCCESS'],
                      timeout=3):
            logger.debug("Enhance Potential success.")
            self.player.click_button(self.ui['ENHANCE_POTENTIAL_SUCCESS'].button, min_duration=1, max_duration=1.5)
            return True

    def enhance_potential(self, target_success_rate=10.00, material_to_use=(NORN_STONE_OF_CHAOS, BLACK_ANTI_MATTER)):
        """Try to enhance potential with materials.

        :param target_success_rate: minimal success rate of enhancement to proceed upgrading.
        :param material_to_use: name of materials to use in enhancement.
        """
        if not self.player.is_ui_element_on_screen(ui_element=self.ui['ENHANCE_POTENTIAL_LABEL']):
            logger.error("Open Enhance Potential menu to enhance potential.")
            return
        if not isinstance(material_to_use, (list, tuple)):
            material_to_use = [material_to_use]
        wrong_materials = [material for material in material_to_use if material not in (self.COSMIC_CUBE_FRAGMENT,
                                                                                        self.BLACK_ANTI_MATTER,
                                                                                        self.NORN_STONE_OF_CHAOS)]
        if wrong_materials:
            logger.error(f"Material to use contains wrong materials: {wrong_materials}")
            return
        for material in material_to_use:
            current_rate = self.success_rate
            self.apply_material(material)
            r_sleep(1)  # Wait for success rate animation
            material_cost = self.success_rate - current_rate - 0.005
            if material_cost == 0:
                continue
            steps_count = ceil((target_success_rate - self.success_rate) / material_cost)
            logger.debug(f"{material} material cost = {material_cost}, "
                         f"steps to achieve target {target_success_rate} from {current_rate } is {steps_count} steps.")
            for _ in range(steps_count):
                self.apply_material(material)
            r_sleep(1)  # Wait for success rate animation
            if self.success_rate >= target_success_rate:
                break
        if self.success_rate >= target_success_rate:
            if self.press_upgrade():
                if not self.check_enhance_success():
                    r_sleep(1)
                    self.enhance_potential(target_success_rate=target_success_rate, material_to_use=material_to_use)
        else:
            logger.error(f"Current Success Rate: {self.success_rate}, cannot get to target {target_success_rate}.")
            return


class ComicCards:
    """Class for working with Comic Cards."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.Game game: instance of the game.
        """
        self.game = game
        self.player = game.player
        self.ui = game.ui

    def upgrade_all_cards(self):
        """Upgrade all available Comic Cards."""
        self.game.go_to_comic_cards()
        logger.info("Comic Cards: upgrading all available cards.")
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['CARDS_UPGRADE_ALL']):
            self.player.click_button(self.ui['CARDS_UPGRADE_ALL'].button)
            for card_index in range(1, 6):
                card_select_ui = self.ui[f'CARDS_SELECT_GRADE_{card_index}']
                self.player.click_button(card_select_ui.button)
                logger.debug(f"Comic Cards: starting to upgrade UI Element {card_select_ui.name}")
                if not wait_until(self.player.is_image_on_screen, timeout=3, ui_element=card_select_ui):
                    logger.warning("Comic Cards: can't select card's grade.")
                    continue
                logger.debug(f"Comic Cards: successfully selected UI Element {card_select_ui.name}")
                self.player.click_button(self.ui['CARDS_SELECT_GRADE'].button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['CARDS_UPGRADE_CONFIRM']):
                    self.player.click_button(self.ui['CARDS_UPGRADE_CONFIRM'].button)
                    if wait_until(self.player.is_ui_element_on_screen, timeout=10,
                                  ui_element=self.ui['CARDS_UPGRADE_RESULTS_OK']):
                        logger.debug(f"Comic Cards: successfully upgraded UI Element {card_select_ui.name}")
                        self.player.click_button(self.ui['CARDS_UPGRADE_RESULTS_OK'].button)
                        wait_until(self.player.is_image_on_screen, timeout=3, ui_element=card_select_ui)
                        continue
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['CARDS_UPGRADE_ALL_CANCEL']):
            self.player.click_button(self.ui['CARDS_UPGRADE_ALL_CANCEL'].button)
            self.game.go_to_main_menu()
