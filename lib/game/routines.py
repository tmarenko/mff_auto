import urllib.request as request
import urllib.error as urlib_error
import json
import lib.logger as logging
from datetime import datetime, timedelta
from math import ceil
from random import randint
from time import sleep
from lib.game.missions.missions import Missions
from lib.functions import wait_until, is_strings_similar, r_sleep

logger = logging.get_logger(__name__)


class Routine(Missions):

    def __init__(self, game):
        super().__init__(game, "")


class DailyTrivia(Routine):
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
        def close_notifications():
            return self.game.close_complete_challenge_notification() or self.close_shield_lvl_up_notification()

        question = self.player.get_screen_text(ui_element=self.ui['DAILY_TRIVIA_QUESTION'])
        logger.debug(f"Found question: {question}")
        answers = [value for key, value in self.trivia.items() if is_strings_similar(question, key)]
        if not answers:
            logger.error(f"Can find answer for question: {question}")
            return False
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
                        notification_closed = wait_until(close_notifications, timeout=3)
                        logger.debug(f"Complete challenge notifications was closed: {notification_closed}")
                        return True
                    else:
                        logger.error("Something went wrong after selecting correct answer.")
        else:
            logger.error("No available answers was found for trivia question.")
            random_answer = randint(1, 4)
            random_answer_ui = self.ui[f'DAILY_TRIVIA_ANSWER_{random_answer}']
            logger.warning(f"Selecting random answer: {random_answer}.")
            self.player.click_button(random_answer_ui.button)
            return True


class ShieldLab(Routine):
    """Class for working with Shield Lab."""

    def collect_antimatter(self):
        """Collect all available antimatter in the lab."""
        self.game.go_to_lab()
        r_sleep(1)  # Wait for button's animation
        if self.player.is_ui_element_on_screen(ui_element=self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_1']):
            logger.debug("Found COLLECT button with max lvl generator, collecting.")
            self.player.click_button(self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_1'].button)
        if self.player.is_ui_element_on_screen(ui_element=self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_2']):
            logger.debug("Found COLLECT button with not max lvl generator, collecting.")
            self.player.click_button(self.ui['LAB_ANTIMATTER_GENERATOR_COLLECT_2'].button)
        self.game.go_to_main_menu()


class EnhancePotential(Routine):
    """Class for working with character's potential enhancement."""

    COSMIC_CUBE_FRAGMENT = "COSMIC_CUBE_FRAGMENT"
    BLACK_ANTI_MATTER = "BLACK_ANTI_MATTER"
    NORN_STONE_OF_CHAOS = "NORN_STONE_OF_CHAOS"

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
        logger.error("Can't find Upgrade button to click.")
        return False

    def check_enhance_was_successful(self):
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
            logger.debug("Enhance Potential succeeded.")
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
                if not self.check_enhance_was_successful():
                    r_sleep(1)
                    self.enhance_potential(target_success_rate=target_success_rate, material_to_use=material_to_use)
        else:
            logger.error(f"Current Success Rate: {self.success_rate}, cannot get to target {target_success_rate}.")
            return


class ComicCards(Routine):
    """Class for working with Comic Cards."""

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
            self.close_after_mission_notifications()
            self.game.go_to_main_menu()


class CustomGear(Routine):
    """Class for working with Custom Gear."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.Game game: instance of the game.
        """
        super().__init__(game)
        self.is_quick_toggle = None

    def quick_upgrade_gear(self, times=0):
        """Quick Upgrade custom gear.

        :param times: how many times to upgrade.
        """
        self.game.go_to_inventory()
        logger.info(f"Custom Gear: upgrading gear {times} times.")
        self.player.click_button(self.ui['INVENTORY_CUSTOM_GEAR_TAB'].button)
        if wait_until(self.is_custom_gear_tab, timeout=3, period=1):
            if not self.try_to_select_gear_for_upgrade():
                logger.error("Custom Gear: can't select gear for upgrade, probably you have none, exiting.")
                self.game.go_to_main_menu()
                return
            if not self.toggle_quick_upgrade():
                logger.error("Custom Gear: can't find Quick Upgrade button, exiting.")
                self.game.go_to_main_menu()
                return
            for _ in range(times):
                if not self.try_to_select_gear_for_upgrade():
                    logger.error("Custom Gear: can't select gear for upgrade, probably you have none, exiting.")
                    self.game.go_to_main_menu()
                    break
                self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE'].button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['CUSTOM_GEAR_QUICK_UPGRADE_CONFIRM']):
                    logger.debug("Custom Gear: confirming upgrading.")
                    self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_CONFIRM'].button)
                    if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['CUSTOM_GEAR_QUICK_UPGRADE_INCLUDE_UPGRADED']):
                        logger.debug("Custom Gear: confirming to use upgraded gear.")
                        self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_INCLUDE_UPGRADED'].button)
                    self.close_upgrade_result()
                else:
                    if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['CUSTOM_GEAR_NO_MATERIALS']):
                        logger.error("Custom Gear: you have no materials for gear upgrade.")
                        self.player.click_button(self.ui['CUSTOM_GEAR_NO_MATERIALS'].button)
                        break

        # `self.is_quick_toggle is False` not working o_O
        if self.is_quick_toggle is not None and not self.is_quick_toggle:
            logger.debug("Custom Gear: returning Quick Upgrade toggle to inactive.")
            self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'].button)
        self.game.go_to_main_menu()

    def is_custom_gear_tab(self):
        """Check if Custom Gear tab is opened."""
        return self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE']) or \
               self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_ENHANCE']) or \
               self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_CHANGE_OPTION'])

    def toggle_quick_upgrade(self):
        """Toggle Quick Upgrade toggle."""
        self.is_quick_toggle = self.player.is_image_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'])
        if not self.is_quick_toggle:
            logger.debug("Custom Gear: found Quick Upgrade toggle inactive. Clicking it.")
            self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'].button)
            wait_until(self.player.is_image_on_screen, timeout=3,
                       ui_element=self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'])
        return self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE'])

    def close_upgrade_result(self):
        """Close upgrade's result notification."""
        def is_results_window():
            return self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1']) or \
                   self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2'])

        if wait_until(is_results_window, timeout=10):
            if self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1']):
                self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1'].button)
            if self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2']):
                self.player.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2'].button)
            self.close_after_mission_notifications()
        if is_results_window() or not self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_SELL_ALL']):
            return self.close_upgrade_result()
        logger.debug("Custom Gear: successfully upgraded custom gear.")

    def try_to_select_gear_for_upgrade(self):
        """Try to select gear for upgrade from inventory."""
        if self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_CHANGE_OPTION']):
            self.player.click_button(self.ui['CUSTOM_GEAR_1'].button)
        return not self.player.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_CHANGE_OPTION'])


class WaitUntil(Routine):
    """Class for working with waiting different events."""

    def wait_until_boost_points(self, value=100):
        """Wait until boost points value is equal or greater then given amount.

        :param value: value for boost pints.
        """
        logger.debug(f"Current Boost points: {self.game.boost}, waiting until: {value}")
        while int(self.game.boost) < value:
            sleep(90)
        logger.debug(f"Current Boost points: {self.game.boost}, done.")

    def wait_until_max_energy(self):
        """wait until energy is max out."""
        logger.debug(f"Current energy: {self.game.energy}, waiting until: {self.game.energy_max}")
        while int(self.game.energy) < int(self.game.energy_max):
            sleep(120)
        logger.debug(f"Current energy: {self.game.energy}, done.")

    def wait_until_daily_reset(self):
        """Wait until game's daily reset."""
        try:
            with request.urlopen("http://worldtimeapi.org/api/timezone/Etc/UTC") as url_data:
                content = url_data.read()
                time_data = json.loads(content)
        except urlib_error.HTTPError as err:
            logger.error(f"Caught HTTP error: {err}\n"
                         f"Trying to get time again in next 10 seconds.")
            sleep(10)
            return self.wait_until_daily_reset()
        current_time = datetime.strptime(time_data['datetime'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
        logger.debug(f"Current time is {current_time} (UTC timezone), waiting until 3 PM.")
        while current_time.hour < 15:
            sleep(60)
            current_time += timedelta(seconds=60)
        logger.debug(f"Current time is {current_time}, done.")


class Friends(Routine):
    """Class for working with Friends."""

    def send_all(self):
        """Send all tokens to friends."""
        self.game.go_to_friends()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['FRIENDS_TOKEN_SEND_ALL']):
            self.player.click_button(self.ui['FRIENDS_TOKEN_SEND_ALL'].button)
            notification_closed = wait_until(self.game.close_complete_challenge_notification, timeout=3)
            logger.debug(f"Complete challenge notifications was closed: {notification_closed}")
        self.game.go_to_main_menu()

    def acquire_all(self):
        """Acquire all tokens from friends."""
        self.game.go_to_friends()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['FRIENDS_TOKEN_ACQUIRE_ALL']):
            self.player.click_button(self.ui['FRIENDS_TOKEN_ACQUIRE_ALL'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['FRIENDS_TOKEN_ACQUIRE_ALL_CLOSE']):
                self.player.click_button(self.ui['FRIENDS_TOKEN_ACQUIRE_ALL_CLOSE'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['FRIENDS_ACQUIRE_NOTICE']):
                logger.debug("Friends: can't acquire more tokens, exiting.")
                self.player.click_button(self.ui['FRIENDS_ACQUIRE_NOTICE'].button)
        self.game.go_to_main_menu()


class Alliance(Routine):
    """Class for working with Alliance."""

    def check_in(self):
        """Click Check-In button in Alliance."""
        self.game.go_to_alliance()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_CHECK_IN']):
            self.player.click_button(self.ui['ALLIANCE_CHECK_IN'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_CHECK_IN_CLOSE']):
                self.player.click_button(self.ui['ALLIANCE_CHECK_IN_CLOSE'].button)
        self.game.go_to_main_menu()
