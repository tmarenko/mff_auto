import regex

import lib.logger as logging
from lib.functions import wait_until
from lib.game import ui
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class WorldBossInvasion(Missions):
    """Class for working with World Boss Invasion missions."""

    class MissionFilter:
        """Class for working with mission types of World Boss Invasion."""

        DEFAULT_ERROR = 3  # Number of errors in the form of inserted, deleted or substituted characters in regex

        def __init__(self, pattern, opposite_pattern, mission_filter, opposite_filter):
            """Class initialization.

            :param str pattern: regular expression pattern for mission's condition.
            :param str opposite_pattern: regular expression pattern for opposite mission's condition.
            :param ui.UIElement mission_filter: UI for main mission filter.
            :param ui.UIElement opposite_filter: UI for opposite mission filter.
            """
            self.pattern = f"({pattern}){{e<={self.DEFAULT_ERROR}}}"
            self._regexp = regex.compile(self.pattern)
            self.opposite_pattern = f"({opposite_pattern}){{e<={self.DEFAULT_ERROR}}}"
            self._opposite_regexp = regex.compile(self.opposite_pattern)
            self.filter = mission_filter
            self.opposite_filter = opposite_filter

        def get_filter(self, text):
            if self._regexp.match(text):
                return self.filter
            if self._opposite_regexp.match(text):
                return self.opposite_filter

    class SuperHeroes(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Super Heroes",
                             opposite_pattern="Clear the stage with less than N Super Heroes",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_HERO,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_VILLAIN)

    class SuperVillain(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Super Villain",
                             opposite_pattern="Clear the stage with less than N Super Villain",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_VILLAIN,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_HERO)

    class BlastCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Blast type Characters",
                             opposite_pattern="Clear the stage with less than N Blast type Characters",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_BLAST,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_ALL)

    class CombatCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Combat type Characters",
                             opposite_pattern="Clear the stage with less than N Combat type Characters",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_COMBAT,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_ALL)

    class SpeedCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Speed type Characters",
                             opposite_pattern="Clear the stage with less than N Speed type Characters",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_SPEED,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_ALL)

    class UniversalCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Universal type Characters",
                             opposite_pattern="Clear the stage with less than N Universal type Characters",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_UNIVERSAL,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_ALL)

    class MaleCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Male Characters",
                             opposite_pattern="Clear the stage with less than N Male Characters",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_MALE,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_FEMALE)

    class FemaleCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Female Characters",
                             opposite_pattern="Clear the stage with less than N Female Characters",
                             mission_filter=ui.INVASION_CHARACTER_FILTER_FEMALE,
                             opposite_filter=ui.INVASION_CHARACTER_FILTER_MALE)

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='WORLD BOSS INVASION')
        self._chests = None
        self._max_chests = None
        self._boss_mission = None
        self.mission_filters = [self.SuperHeroes(), self.SuperVillain(), self.MaleCharacters(), self.FemaleCharacters(),
                                self.CombatCharacters(), self.SpeedCharacters(), self.BlastCharacters(),
                                self.UniversalCharacters()]

    @property
    def battle_over_conditions(self):
        def damage():
            if self.emulator.is_ui_element_on_screen(ui.INVASION_END_BATTLE_DAMAGE):
                logger.info("Won battle, chest was acquired.")
                self._chests += 1
                return True
            return False

        def failed():
            return self.emulator.is_ui_element_on_screen(ui.INVASION_FAILED)

        return [damage, failed]

    def do_missions(self, times=None, ignore_coop_mission=False):
        """Does missions."""
        self.start_missions(times=times, ignore_coop_mission=ignore_coop_mission)
        self.end_missions()

    def start_missions(self, times=None, ignore_coop_mission=False):
        """Starts World Boss Invasion."""
        if self.open_world_boss_invasion():
            if self.chests > 0:
                if not self.acquire_chests():
                    return
            if times:
                self._max_chests = times
            if self.chests < self.max_chests and self._find_boss_for_fight():
                while self.chests < self.max_chests:
                    logger.debug(f"{times} stages left to complete ({self.chests} out of {self.max_chests}.")
                    if not self.press_start_button(ignore_coop_mission=ignore_coop_mission):
                        return
                    self._wait_for_players_and_start_fight()
        logger.info("No more stages.")

    def end_missions(self):
        """Ends missions."""
        if not self.game.is_main_menu():
            self.game.emulator.click_button(ui.HOME)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def open_world_boss_invasion(self):
        """Opens World Boss Invasion missions.

        :return: is WBI missions open or not.
        :rtype: bool
        """
        self.game.go_to_coop()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_LABEL):
            self.emulator.click_button(ui.INVASION_LABEL)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_MENU_LABEL):
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_MANAGE_CHESTS)
        return False

    def _get_chests_count(self):
        """Stores current chests and max chests amount."""
        chests_text = self.emulator.get_screen_text(ui_element=ui.INVASION_STAGES)
        current_chest, max_chest = self.game.get_current_and_max_values_from_text(chests_text)
        self._chests = 5 if current_chest > 5 else current_chest
        self._max_chests = 5 if max_chest > 5 else max_chest
        logger.info(f"{self._chests} chests out of {self._max_chests} (from '{chests_text}' text).")

    @property
    def chests(self):
        """Get current amount of chests.

        :rtype: int
        """
        if self._chests is None:
            self._get_chests_count()
        return self._chests

    @chests.setter
    def chests(self, value):
        """Update available chests value.

        :param int value: value to set.
        """
        self._chests = value

    @property
    def max_chests(self):
        """Get max amount of chests.

        :rtype: int
        """
        if self._max_chests is None:
            self._get_chests_count()
        return self._max_chests

    def acquire_chests(self):
        """Acquires all available chests."""
        logger.debug("Starting to acquire all available chests.")
        self.emulator.click_button(ui.INVASION_MANAGE_CHESTS)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_CHESTS_MENU_LABEL):
            for chest_index in range(1, self.max_chests + 1):
                self._acquire_chest(chest_index)
        logger.debug("Going back to mission's lobby.")
        self.emulator.click_button(ui.MENU_BACK)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_MANAGE_CHESTS):
            self._get_chests_count()
            return True
        logger.error("Can't get back to mission's lobby.")

    def _acquire_chest(self, chest_index):
        """Acquires chest by chest index.

        :param int chest_index: chest index (from 1 to max chests + 1)

        :return: was chest acquired or not.
        :rtype: bool
        """
        logger.debug(f"Trying to acquire chest #{chest_index}")
        chest_ui = ui.get_by_name(f'INVASION_CHEST_AVAILABLE_{chest_index}')
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=1, ui_element=chest_ui):
            logger.debug(f"Chest {chest_index} is available. Trying to open.")
            self.emulator.click_button(chest_ui)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_SKIP_CHEST):
                while self.emulator.is_ui_element_on_screen(ui_element=ui.INVASION_SKIP_CHEST):
                    logger.debug("Skipping chests items.")
                    self.emulator.click_button(ui.INVASION_SKIP_CHEST, min_duration=0.5,
                                               max_duration=0.8)
                while not self.emulator.is_ui_element_on_screen(ui_element=ui.INVASION_CHESTS_MENU_LABEL):
                    self.emulator.click_button(ui.INVASION_SKIP_CHEST, min_duration=0.5,
                                               max_duration=0.8)
                logger.debug("Chest acquired, going back to chest's menu.")
                return True
        logger.debug(f"Chest #{chest_index} isn't available.")
        return False

    def _find_boss_for_fight(self):
        """Finds available boss fight and enter it.

        :return: was fight found and entered or not.
        :rtype: bool
        """
        weekly_boss_name = self.emulator.get_screen_text(ui_element=ui.INVASION_NAME)
        logger.debug(f"Weekly boss name: {weekly_boss_name}")
        for bosses in ['INVASION_TWILIGHT_BATTLE_', 'INVASION_BLACK_ORDER_BATTLE_']:
            for boss_index in range(1, 8):
                boss_ui = ui.get_by_name(f'{bosses}{boss_index}')
                boss_time = self.emulator.get_screen_text(ui_element=boss_ui)
                if boss_time:
                    logger.debug(f"Found boss with UI: {boss_ui} with time {boss_time}, entering.")
                    self.emulator.click_button(boss_ui)
                    if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_BOSS_FIGHT_ENTER):
                        self._boss_mission = self.emulator.get_screen_text(ui.INVASION_BOSS_MISSION)
                        logger.debug(f"Current boss mission: {self._boss_mission}")
                        self.emulator.click_button(ui.INVASION_BOSS_FIGHT_ENTER)
                        return True
                    logger.error(f"Something went wrong with found boss {boss_ui}")
                    if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_BOSS_FIGHT_CLOSE):
                        logger.warning(f"Closing {boss_ui}")
                        self.emulator.click_button(ui.INVASION_BOSS_FIGHT_CLOSE)
        logger.error("Failed to found boss.")
        return False

    def _check_notifications_before_fight(self):
        """Checks fight notifications about any obstacles to start a fight.

        :return: can we start a fight or not.
        :rtype: bool
        """
        waiting_for_other_players = self.emulator.is_ui_element_on_screen(
            ui_element=ui.WAITING_FOR_OTHER_PLAYERS)
        if not waiting_for_other_players:
            if self.emulator.is_ui_element_on_screen(ui_element=ui.NOT_ENOUGH_ENERGY):
                self.emulator.click_button(ui.NOT_ENOUGH_ENERGY)
                self._chests = self._max_chests

            if self.emulator.is_ui_element_on_screen(ui_element=ui.INVASION_NOT_ENOUGH_CHARACTERS):
                self.emulator.click_button(ui.INVASION_NOT_ENOUGH_CHARACTERS)
                self._chests = self._max_chests
            return False
        return True

    def press_start_button(self, start_button_ui=ui.INVASION_BOSS_FIGHT_START, ignore_coop_mission=False):
        """Presses start button of the mission.

        :return: was button clicked successfully or not.
        :rtype: bool
        """
        logger.debug(f"Pressing START button with UI Element: {start_button_ui}.")
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=start_button_ui):
            self._deploy_characters(ignore_coop_mission=ignore_coop_mission)
            self.emulator.click_button(start_button_ui)
            if wait_until(self._check_notifications_before_fight, timeout=10):
                return True
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVASION_NO_CHEST_SLOTS):
                logger.warning("No slots for chests. Exiting.")
                self.emulator.click_button(ui.INVASION_NO_CHEST_SLOTS)
                return False
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                      ui_element=ui.DISCONNECT_NEW_OPPONENT):
            logger.debug("Found disconnect notification. Trying to start again.")
            self.emulator.click_button(ui.DISCONNECT_NEW_OPPONENT)
            return True
        logger.error(f"Unable to press {start_button_ui} button.")
        return False

    def _deploy_characters(self, ignore_coop_mission=False):
        """Deploys 3 characters to battle."""
        no_main = self.emulator.is_image_on_screen(ui_element=ui.INVASION_NO_CHARACTER_MAIN)
        no_left = self.emulator.is_image_on_screen(ui_element=ui.INVASION_NO_CHARACTER_LEFT)
        no_right = self.emulator.is_image_on_screen(ui_element=ui.INVASION_NO_CHARACTER_RIGHT)
        if not ignore_coop_mission and (no_main or no_left or no_right):
            self._select_character_filter_by_mission()
        if no_main:
            self.emulator.click_button(ui.INVASION_CHARACTER_1)
        if no_left:
            self.emulator.click_button(ui.INVASION_CHARACTER_2)
        if no_right:
            self.emulator.click_button(ui.INVASION_CHARACTER_3)

    def _select_character_filter_by_mission(self):
        """Selects character filter by current mission."""
        for mission_filter in self.mission_filters:
            characters_filter = mission_filter.get_filter(text=self._boss_mission)
            if characters_filter:
                logger.debug(f"Found filter {characters_filter} by {mission_filter.__class__.__name__}")
                self.emulator.click_button(ui.INVASION_CHARACTER_FILTER, min_duration=1, max_duration=1)
                self.emulator.click_button(characters_filter, min_duration=1, max_duration=1)

    def _wait_for_players_and_start_fight(self):
        """Waits for players before start of the fight."""
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WAITING_FOR_OTHER_PLAYERS):
            logger.debug("Waiting for other players before battle.")
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=60, condition=False, period=0.5,
                          ui_element=ui.WAITING_FOR_OTHER_PLAYERS):
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                              ui_element=ui.DISCONNECT_NEW_OPPONENT):
                    logger.debug("Found disconnect notification. Trying to start again.")
                    self.emulator.click_button(ui.DISCONNECT_NEW_OPPONENT)
                    return self._wait_for_players_and_start_fight()
                logger.debug("Battle is loading. Starting manual bot.")
                return self._manual_bot_start()
            logger.warning("Waiting other players very long, trying to reset.")
            self.emulator.click_button(ui.WAITING_FOR_OTHER_PLAYERS)

    def _manual_bot_start(self):
        """Starts manual bot for the fight."""
        ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
        if wait_until(self.emulator.is_image_on_screen, timeout=2, ui_element=ui.INVASION_HOME_BUTTON):
            if self._chests < self._max_chests:
                self.press_repeat_button(repeat_button_ui=ui.INVASION_REPEAT_BUTTON,
                                         start_button_ui=ui.INVASION_BOSS_FIGHT_START)
            else:
                self.press_home_button(home_button=ui.INVASION_HOME_BUTTON)
            return
        # In case we got back from fight by disconnect or something else
        logger.debug("Any chest after boss fight wasn't acquired.")
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=20,
                      ui_element=ui.INVASION_BOSS_FIGHT_START):
            if self.press_start_button():
                self._wait_for_players_and_start_fight()
