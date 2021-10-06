import random

import regex

import lib.logger as logging
from lib.functions import r_sleep, wait_until
from lib.game import ui
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class Shadowland(Missions):
    """Class for working with Shadowland."""

    class FloorFilter:
        """Class for working with floor rules."""

        DEFAULT_ERROR = 3  # Number of errors in the form of inserted, deleted or substituted characters in regex

        def __init__(self, pattern, floor_filter):
            """Class initialization.

            :param str pattern: regular expression pattern for mission's condition.
            :param ui.UIElement floor_filter: UI for main mission filter.
            """
            self.pattern = f"[\\S\\s]*({pattern}){{e<={self.DEFAULT_ERROR}}}[\\S\\s]*"
            self._regexp = regex.compile(self.pattern)
            self.filter = floor_filter

        def get_filter(self, text):
            if self._regexp.match(text):
                return self.filter

        def __str__(self):
            return self.__class__.__name__

    class SuperHeroes(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Heroes have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_HERO)

    class SuperVillain(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Villains have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_VILLAIN)

    class UniversalSuperVillain(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Universal-type Villains have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_UNIVERSAL)

    class BlastCharacters(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Blast-type characters have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_BLAST)

    class CombatCharacters(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Combat-type characters have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_COMBAT)

    class SpeedCharacters(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Speed-type characters have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_SPEED)

    class UniversalCharacters(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Universal-type characters have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_UNIVERSAL)

    class MaleHeroes(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Male Heroes have an advantage in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER_MALE)

    class FireElement(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Fire Element attacks won't work in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER)

    class IceElement(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Ice Element attacks won't work in this stage.",
                             floor_filter=ui.SL_CHARACTER_FILTER)

    class BreakingJar(FloorFilter):

        def __init__(self):
            super().__init__(pattern="Breaking the jar will decrease the enemy dodge rate.",
                             floor_filter=ui.SL_CHARACTER_FILTER)

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='SHADOWLAND')
        self._cleared_previously = False
        self._room_rule = None
        self.floor_filters = [self.SuperHeroes(), self.SuperVillain(), self.UniversalSuperVillain(),
                              self.BlastCharacters(), self.CombatCharacters(), self.SpeedCharacters(),
                              self.UniversalCharacters(), self.MaleHeroes(), self.FireElement(), self.IceElement(),
                              self.BreakingJar()]

    @property
    def battle_over_conditions(self):
        def success():
            return self.emulator.is_ui_element_on_screen(ui.SL_BATTLE_SUCCESS)

        def rewards():
            return self.emulator.is_ui_element_on_screen(ui.SL_BATTLE_REWARDS)

        def try_again():
            return self.emulator.is_ui_element_on_screen(ui.SL_BATTLE_LOST)

        return [success, rewards, try_again]

    def open_shadowland(self):
        """Opens Shadowland gamemode."""
        self.game.select_mode(self.mode_name)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SL_KING_OF_THE_HILL_REWARD):
            logger.debug("Closing `King of the Hill` rewards notification.")
            self.emulator.click_button(ui.SL_KING_OF_THE_HILL_REWARD)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SL_KING_OF_THE_HILL_NOTICE):
            logger.debug("Closing `King of the Hill` notification.")
            self.emulator.click_button(ui.SL_KING_OF_THE_HILL_NOTICE)
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SL_ENTER_SHADOWLAND)

    def do_missions(self, times=None):
        """Does Shadowland battles.

        :param int times: how many Shadowland floors to clear.
        """
        if times:
            self.stages = times
        elif self.stages_max == 35:
            self.stages = self.stages_max - self.stages - 1
        if self.stages > 0:
            self.start_missions(times=self.stages)
            self.end_missions()
        self.game.go_to_main_menu()

    def start_missions(self, times=0):
        """Starts Shadowland battles.

        :param int times: how many Shadowland floors to clear.
        """
        logger.info(f"Starting Shadowland for {self.stages} times.")
        if not self.open_shadowland():
            return logger.error("Can't get into Shadowland.")

        while times > 0:
            if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SL_ENTER_SHADOWLAND):
                return logger.error("Can't enter into Shadowland Floor.")
            self.emulator.click_button(ui.SL_ENTER_SHADOWLAND)
            if not wait_until(self._is_floor_open):
                return logger.error("Can't open Shadowland Floor, exiting.")
            if not self.select_floor():
                return logger.error("Can't select Shadowland Floor, exiting.")

            if not self.press_start_button():
                return logger.error("Failed to start Shadowland Floor battle.")
            ManualBattleBot(self.game, self.battle_over_conditions).fight()
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SL_BATTLE_LOST):
                logger.info("Lost Shadowland battle, exiting.")
                return self.press_home_button(home_button=ui.SL_BATTLE_HOME_BUTTON)
            times -= 1
            logger.debug(f"{times} floors left to complete.")
            if times > 0:
                self.press_repeat_button(repeat_button_ui=ui.SL_BATTLE_NEXT_BUTTON,
                                         start_button_ui=ui.SL_ENTER_SHADOWLAND)
                r_sleep(3)  # Wait for floor animations
            else:
                self.press_home_button(home_button=ui.SL_BATTLE_HOME_BUTTON)
                self.close_after_mission_notifications()

    def press_start_button(self, start_button_ui=ui.SL_START_BATTLE):
        """Presses start button of the Shadowland floor."""
        if self.emulator.is_ui_element_on_screen(start_button_ui):
            if self._cleared_previously:
                all_deployed = self._deploy_characters()
                if not all_deployed:
                    self._cleared_previously = False  # Select characters from the bottom of the list
                    logger.debug("Missing characters. Redeploying additional characters using floor rules.")
                    all_deployed = self._deploy_characters(apply_character_filter=True)
                if not all_deployed:
                    logger.debug("Not enough characters with floor rules. Deploying any possible character")
                    self.emulator.click_button(ui.SL_CHARACTER_FILTER, min_duration=1, max_duration=1)
                    self.emulator.click_button(ui.SL_CHARACTER_FILTER, min_duration=1, max_duration=1)
                    all_deployed = self._deploy_characters(apply_character_filter=False)
            else:
                all_deployed = self._deploy_characters(apply_character_filter=True)
            if not all_deployed:
                logger.warning("No more characters to deploy. Exiting")
                return False
            self.emulator.click_button(ui.SL_START_BATTLE)
            return True
        return False

    def _is_floor_open(self):
        """Checks whether if any of Shadowland's floor is open. Looks for `ENTER` text on each possible floor."""
        return self.emulator.is_ui_element_on_screen(ui.SL_LEFT_ROOM_ENTER) or \
               self.emulator.is_ui_element_on_screen(ui.SL_MIDDLE_ROOM_ENTER) or \
               self.emulator.is_ui_element_on_screen(ui.SL_RIGHT_ROOM_ENTER) or \
               self.emulator.is_ui_element_on_screen(ui.SL_SINGLE_ROOM_ENTER) or \
               self.emulator.is_ui_element_on_screen(ui.SL_DOUBLE_LEFT_ROOM_ENTER) or \
               self.emulator.is_ui_element_on_screen(ui.SL_DOUBLE_RIGHT_ROOM_ENTER)

    def _toggle_stage_info(self):
        """Toggles `Stage Info` toggle on available floor in order to see floor's rule."""
        if self.emulator.is_ui_element_on_screen(ui.SL_MIDDLE_ROOM_ENTER):
            if not self.emulator.is_image_on_screen(ui.SL_STAGE_INFO_TOGGLE):
                logger.debug("Enabling 'Stage Info' toggle (3 rooms)")
                self.emulator.click_button(ui.SL_STAGE_INFO_TOGGLE)

        if self.emulator.is_ui_element_on_screen(ui.SL_SINGLE_ROOM_ENTER):
            if not self.emulator.is_image_on_screen(ui.SL_SINGLE_STAGE_INFO_TOGGLE):
                logger.debug("Enabling 'Stage Info' toggle (1 room)")
                self.emulator.click_button(ui.SL_SINGLE_STAGE_INFO_TOGGLE)

        if self.emulator.is_ui_element_on_screen(ui.SL_DOUBLE_LEFT_ROOM_ENTER):
            if not self.emulator.is_image_on_screen(ui.SL_DOUBLE_STAGE_INFO_TOGGLE):
                logger.debug("Enabling 'Stage Info' toggle (2 room)")
                self.emulator.click_button(ui.SL_DOUBLE_STAGE_INFO_TOGGLE)

    def _select_random_floor(self, floors, rules):
        """Selects random floor and stores rules from it.

        :param tuple[ui.UIElement] floors: list of floors to choose from.
        :param tuple[ui.UIElement] rules: list of corresponding rules for each floor.
        """
        random_index = random.randrange(0, len(floors))
        random_room = floors[random_index]
        self._room_rule = self.emulator.get_screen_text(rules[random_index])
        logger.debug(f"Selected random room: {random_room}")
        self.emulator.click_button(random_room)

    def select_floor(self):
        """Selects available Shadowland floor.
        Tries to select floor that already have been cleared. If such floor isn't present then selects random floor.

        :return: was floor selected or not.
        :rtype: bool
        """
        self._toggle_stage_info()

        if self.emulator.is_ui_element_on_screen(ui.SL_LEFT_ROOM_CLEARED):
            self._cleared_previously = True
            self._room_rule = self.emulator.get_screen_text(ui.SL_LEFT_ROOM_RULE)
            logger.debug("Selected left room because it was cleared in previous season.")
            self.emulator.click_button(ui.SL_LEFT_ROOM_ENTER)
        elif self.emulator.is_ui_element_on_screen(ui.SL_MIDDLE_ROOM_CLEARED):
            self._cleared_previously = True
            self._room_rule = self.emulator.get_screen_text(ui.SL_MIDDLE_ROOM_RULE)
            logger.debug("Selected middle room because it was cleared in previous season.")
            self.emulator.click_button(ui.SL_MIDDLE_ROOM_ENTER)
        elif self.emulator.is_ui_element_on_screen(ui.SL_RIGHT_ROOM_CLEARED):
            self._cleared_previously = True
            self._room_rule = self.emulator.get_screen_text(ui.SL_RIGHT_ROOM_RULE)
            logger.debug("Selected right room because it was cleared in previous season.")
            self.emulator.click_button(ui.SL_RIGHT_ROOM_ENTER)
        elif self.emulator.is_ui_element_on_screen(ui.SL_SINGLE_ROOM_ENTER):
            self._cleared_previously = self.emulator.is_ui_element_on_screen(ui.SL_SINGLE_ROOM_CLEARED)
            self._room_rule = self.emulator.get_screen_text(ui.SL_SINGLE_ROOM_RULE)
            logger.debug("Selected single room.")
            self.emulator.click_button(ui.SL_SINGLE_ROOM_ENTER)
        elif self.emulator.is_ui_element_on_screen(ui.SL_DOUBLE_RIGHT_ROOM_ENTER):
            if self.emulator.is_ui_element_on_screen(ui.SL_DOUBLE_LEFT_ROOM_CLEARED):
                self._cleared_previously = True
                self._room_rule = self.emulator.get_screen_text(ui.SL_DOUBLE_LEFT_ROOM_RULE)
                logger.debug("Selected left room because it was cleared in previous season (from double rooms).")
                self.emulator.click_button(ui.SL_DOUBLE_LEFT_ROOM_ENTER)
            elif self.emulator.is_ui_element_on_screen(ui.SL_DOUBLE_RIGHT_ROOM_CLEARED):
                self._cleared_previously = True
                self._room_rule = self.emulator.get_screen_text(ui.SL_DOUBLE_RIGHT_ROOM_RULE)
                logger.debug("Selected left room because it was cleared in previous season (from double rooms).")
                self.emulator.click_button(ui.SL_DOUBLE_RIGHT_ROOM_ENTER)
            else:
                self._cleared_previously = False
                self._select_random_floor(floors=(ui.SL_DOUBLE_LEFT_ROOM_ENTER, ui.SL_DOUBLE_RIGHT_ROOM_ENTER),
                                          rules=(ui.SL_DOUBLE_LEFT_ROOM_RULE, ui.SL_DOUBLE_RIGHT_ROOM_RULE))
        else:
            self._cleared_previously = False
            self._select_random_floor(floors=(ui.SL_LEFT_ROOM_ENTER, ui.SL_MIDDLE_ROOM_ENTER, ui.SL_RIGHT_ROOM_ENTER),
                                      rules=(ui.SL_LEFT_ROOM_RULE, ui.SL_MIDDLE_ROOM_RULE, ui.SL_RIGHT_ROOM_RULE))
        self._room_rule = self._room_rule.replace("\n", " ")
        logger.debug(f"Rule for current room: {self._room_rule}")
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SL_START_BATTLE)

    def _deploy_characters(self, apply_character_filter=False):
        """Tries to deploy characters.
        If room was cleared in previous season then selects characters from top of the list.
        If room wasn't cleared in previous season then selectes characters from bottom of the list.
        Stops selecting characters when gets `NO EMPTY SLOTS` notification.

        :param bool apply_character_filter: should character filter be applied or not.

        :return: (True or False) full team was selected or not.
        :rtype: bool
        """
        if self._cleared_previously:
            char_num_gen = (char_num for char_num in range(1, 4))  # Only first 3 character from previous clear
        else:
            char_num_gen = (char_num for char_num in range(12, 0, -1))  # 12 characters from the bottom to top
        if apply_character_filter:
            self._select_character_filter_by_mission()
        while not self.emulator.is_ui_element_on_screen(ui.SL_SELECT_CHARACTERS_NO_EMPTY_SLOTS):
            char_num = next(char_num_gen, None)
            if not char_num:  # If no more characters is available to deploy
                if self._cleared_previously:  # Use default strategy with 12 characters
                    char_num_gen = (char_num for char_num in range(12, 0, -1))
                    self._cleared_previously = False
                    continue
                else:
                    return False
            # If `cleared` characters is no more then use default strategy with 12 characters
            if char_num and self._cleared_previously and not self.emulator.is_ui_element_on_screen(
                    ui.get_by_name(f"SL_CHARACTER_CLEARED_{char_num}")):
                char_num_gen = (char_num for char_num in range(12, 0, -1))
                self._cleared_previously = False
                continue
            self.emulator.click_button(ui.get_by_name(f"SL_CHARACTER_{char_num}"))
        self.emulator.click_button(ui.SL_SELECT_CHARACTERS_NO_EMPTY_SLOTS)
        return True

    def _select_character_filter_by_mission(self):
        """Selects character filter by matching rules with `FloorFilter` objects."""
        for floor_filter in self.floor_filters:
            characters_filter = floor_filter.get_filter(text=self._room_rule)
            if characters_filter:
                logger.debug(f"Found filter {characters_filter} by {floor_filter}")
                self.emulator.click_button(ui.SL_CHARACTER_FILTER, min_duration=1, max_duration=1)
                self.emulator.click_button(characters_filter, min_duration=1, max_duration=1)
