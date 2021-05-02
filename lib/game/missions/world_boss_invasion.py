import regex
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, convert_colors_in_image
import lib.logger as logging

logger = logging.get_logger(__name__)

# Low and high values for colors to convert
NUMBERS_COLOR = ([100, 100, 0], [255, 255, 30])
COMBAT_COLOR = ([100, 30, 20], [255, 50, 30])
BLAST_COLOR = ([0, 100, 100], [30, 255, 255])
SPEED_COLOR = ([0, 100, 0], [30, 255, 30])
UNIVERSAL_COLOR = ([100, 40, 100], [255, 70, 255])
CHARACTERS_COLOR = ([120, 100, 0], [180, 255, 30])


class WorldBossInvasion(Missions):
    """Class for working with World Boss Invasion missions."""

    class MissionFilter:
        """Class for working with mission types of World Boss Invasion."""

        DEFAULT_ERROR = 3  # Number of errors in the form of inserted, deleted or substituted characters in regex

        def __init__(self, pattern, opposite_pattern, mission_filter, opposite_filter):
            """Class initialization.

            :param pattern: regular expression pattern for mission's condition.
            :param opposite_pattern: regular expression pattern for opposite mission's condition.
            :param mission_filter: UI for main mission filter.
            :param opposite_filter: UI for opposite mission filter.
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
                             mission_filter='INVASION_CHARACTER_FILTER_HERO',
                             opposite_filter='INVASION_CHARACTER_FILTER_VILLAIN')

    class SuperVillain(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Super Villain",
                             opposite_pattern="Clear the stage with less than N Super Villain",
                             mission_filter='INVASION_CHARACTER_FILTER_VILLAIN',
                             opposite_filter='INVASION_CHARACTER_FILTER_HERO')

    class BlastCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Blast type Characters",
                             opposite_pattern="Clear the stage with less than N Blast type Characters",
                             mission_filter='INVASION_CHARACTER_FILTER_BLAST',
                             opposite_filter='INVASION_CHARACTER_FILTER_ALL')

    class CombatCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Combat type Characters",
                             opposite_pattern="Clear the stage with less than N Combat type Characters",
                             mission_filter='INVASION_CHARACTER_FILTER_COMBAT',
                             opposite_filter='INVASION_CHARACTER_FILTER_ALL')

    class SpeedCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Speed type Characters",
                             opposite_pattern="Clear the stage with less than N Speed type Characters",
                             mission_filter='INVASION_CHARACTER_FILTER_SPEED',
                             opposite_filter='INVASION_CHARACTER_FILTER_ALL')

    class UniversalCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Universal type Characters",
                             opposite_pattern="Clear the stage with less than N Universal type Characters",
                             mission_filter='INVASION_CHARACTER_FILTER_UNIVERSAL',
                             opposite_filter='INVASION_CHARACTER_FILTER_ALL')

    class MaleCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Male Characters",
                             opposite_pattern="Clear the stage with less than N Male Characters",
                             mission_filter='INVASION_CHARACTER_FILTER_MALE',
                             opposite_filter='INVASION_CHARACTER_FILTER_FEMALE')

    class FemaleCharacters(MissionFilter):

        def __init__(self):
            super().__init__(pattern="Clear the stage with more than N Female Characters",
                             opposite_pattern="Clear the stage with less than N Female Characters",
                             mission_filter='INVASION_CHARACTER_FILTER_FEMALE',
                             opposite_filter='INVASION_CHARACTER_FILTER_MALE')

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'INVASION_MENU_LABEL')
        self._chests = None
        self._max_chests = None
        self._boss_mission = None
        self.mission_filters = [self.SuperHeroes(), self.SuperVillain(), self.MaleCharacters(), self.FemaleCharacters(),
                                self.CombatCharacters(), self.SpeedCharacters(), self.BlastCharacters(),
                                self.UniversalCharacters()]

    @property
    def battle_over_conditions(self):
        def chest():
            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['INVASION_SLOT_CHEST']):
                logger.debug("Acquiring chest after boss fight.")
                self.emulator.click_button(self.ui['INVASION_SLOT_CHEST'].button)
                self._chests += 1
                return True
            return False

        def failed():
            return self.emulator.is_ui_element_on_screen(self.ui['INVASION_FAILED'])

        return [chest, failed]

    def do_missions(self, times=None):
        """Do missions."""
        self.start_missions(times=times)
        self.end_missions()

    def start_missions(self, times=None):
        """Start World Boss Invasion."""
        if self.open_world_boss_invasion():
            if self.chests > 0:
                if not self.acquire_chests():
                    return
            if times:
                self._max_chests = times
            if self.chests < self.max_chests and self._find_boss_for_fight():
                while self.chests < self.max_chests:
                    if not self.press_start_button():
                        return
                    self._wait_for_players_and_start_fight()
        logger.info("No more stages.")

    def end_missions(self):
        """End missions."""
        if not self.game.is_main_menu():
            self.game.emulator.click_button(self.ui['HOME'].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def open_world_boss_invasion(self):
        """Open World Boss Invasion missions.

        :return: True or False: is WBI missions open.
        """
        self.game.go_to_coop()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_LABEL']):
            self.emulator.click_button(self.ui['INVASION_LABEL'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_MENU_LABEL']):
                return wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVASION_MANAGE_CHESTS'])
        return False

    def _get_chests_count(self):
        """Receive current chests and max chests amount."""
        chests_text = self.emulator.get_screen_text(ui_element=self.ui['INVASION_STAGES'])
        current_chest, max_chest = self.game.get_current_and_max_values_from_text(chests_text)
        self._chests = 5 if current_chest > 5 else current_chest
        self._max_chests = 5 if max_chest > 5 else max_chest
        logger.info(f"{self._chests} chests out of {self._max_chests} (from '{chests_text}' text).")

    @property
    def chests(self):
        """Get current amount of chests."""
        if self._chests is None:
            self._get_chests_count()
        return self._chests

    @chests.setter
    def chests(self, value):
        """Update available chests value."""
        self._chests = value

    @property
    def max_chests(self):
        """Get max amount of chests."""
        if self._max_chests is None:
            self._get_chests_count()
        return self._max_chests

    def acquire_chests(self):
        """Acquire all available chests."""
        logger.debug("Starting to acquire all available chests.")
        self.emulator.click_button(self.ui['INVASION_MANAGE_CHESTS'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['INVASION_CHESTS_MENU_LABEL']):
            for chest_index in range(1, self.max_chests + 1):
                self._acquire_chest(chest_index)
        logger.debug("Going back to mission's lobby.")
        self.emulator.click_button(self.ui['MENU_BACK'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_MANAGE_CHESTS']):
            self._get_chests_count()
            return True
        logger.error("Can't get back to mission's lobby.")

    def _acquire_chest(self, chest_index):
        """Acquire chest by chest index.

        :param chest_index: chest index (from 1 to max chests + 1)
        :return: True or False: was chest acquired.
        """
        logger.debug(f"Trying to acquire chest #{chest_index}")
        chest_ui = self.ui[f'INVASION_CHEST_AVAILABLE_{chest_index}']
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=1, ui_element=chest_ui):
            logger.debug(f"Chest {chest_index} is available. Trying to open.")
            self.emulator.click_button(chest_ui.button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_SKIP_CHEST']):
                while self.emulator.is_ui_element_on_screen(ui_element=self.ui['INVASION_SKIP_CHEST']):
                    logger.debug("Skipping chests items.")
                    self.emulator.click_button(self.ui['INVASION_SKIP_CHEST'].button, min_duration=0.5,
                                               max_duration=0.8)
                while not self.emulator.is_ui_element_on_screen(ui_element=self.ui['INVASION_CHESTS_MENU_LABEL']):
                    self.emulator.click_button(self.ui['INVASION_SKIP_CHEST'].button, min_duration=0.5,
                                               max_duration=0.8)
                logger.debug("Chest acquired, going back to chest's menu.")
                return True
        logger.debug(f"Chest #{chest_index} isn't available.")
        return False

    def _get_boss_mission_text(self):
        """Get boss's mission text and store it."""
        image = self.emulator.get_screen_image(rect=self.ui['INVASION_BOSS_MISSION'].rect)
        converted_image = convert_colors_in_image(image=image, colors=[NUMBERS_COLOR, COMBAT_COLOR, BLAST_COLOR,
                                                                       CHARACTERS_COLOR, SPEED_COLOR, UNIVERSAL_COLOR])
        self._boss_mission = self.emulator.get_screen_text(self.ui['INVASION_BOSS_MISSION'], screen=converted_image)
        logger.debug(f"Current boss mission: {self._boss_mission}")

    def _find_boss_for_fight(self):
        """Find available boss fight and enter it.

        :return: True or False: was fight found and entered.
        """
        weekly_boss_name = self.emulator.get_screen_text(ui_element=self.ui['INVASION_NAME'])
        logger.debug(f"Weekly boss name: {weekly_boss_name}")
        for bosses in ['INVASION_TWILIGHT_BATTLE_', 'INVASION_BLACK_ORDER_BATTLE_']:
            for boss_index in range(1, 8):
                boss_ui = self.ui[f'{bosses}{boss_index}']
                boss_time = self.emulator.get_screen_text(ui_element=boss_ui)
                if boss_time:
                    logger.debug(f"Found boss with UI: {boss_ui.name} with time {boss_time}, entering.")
                    self.emulator.click_button(boss_ui.button)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVASION_BOSS_FIGHT_ENTER']):
                        self._get_boss_mission_text()
                        self.emulator.click_button(self.ui['INVASION_BOSS_FIGHT_ENTER'].button)
                        return True
                    logger.warning(f"Something went wrong with found boss {boss_ui.name}")
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVASION_BOSS_FIGHT_CLOSE']):
                        logger.warning(f"Closing {boss_ui.name}")
                        self.emulator.click_button(self.ui['INVASION_BOSS_FIGHT_CLOSE'].button)
        logger.error("Failed to found boss.")
        return False

    def _check_notifications_before_fight(self):
        """Check fight notifications about any obstacles to start a fight.

        :return: True or False: can we start a fight or not.
        """
        waiting_for_other_players = self.emulator.is_ui_element_on_screen(
            ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS'])
        if not waiting_for_other_players:
            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['NOT_ENOUGH_ENERGY']):
                self.emulator.click_button(self.ui['NOT_ENOUGH_ENERGY'].button)
                self._chests = self._max_chests

            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['INVASION_NOT_ENOUGH_CHARACTERS']):
                self.emulator.click_button(self.ui['INVASION_NOT_ENOUGH_CHARACTERS'].button)
                self._chests = self._max_chests
            return False
        return True

    def press_start_button(self, start_button_ui='INVASION_BOSS_FIGHT_START'):
        """Press start button of the mission.

        :return: was button clicked successfully.
        """
        logger.debug(f"Pressing START button with UI Element: {start_button_ui}.")
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui[start_button_ui]):
            self._deploy_characters()
            self.emulator.click_button(self.ui[start_button_ui].button)
            if wait_until(self._check_notifications_before_fight, timeout=10):
                return True
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['INVASION_NO_CHEST_SLOTS']):
                logger.warning("No slots for chests. Exiting.")
                self.emulator.click_button(self.ui['INVASION_NO_CHEST_SLOTS'].button)
                return False
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                      ui_element=self.ui['DISCONNECT_NEW_OPPONENT']):
            logger.debug("Found disconnect notification. Trying to start again.")
            self.emulator.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
            return True
        logger.warning("Unable to press START button.")
        return False

    def _deploy_characters(self):
        """Deploy 3 characters to battle."""
        no_main = self.emulator.is_image_on_screen(ui_element=self.ui['INVASION_NO_CHARACTER_MAIN'])
        no_left = self.emulator.is_image_on_screen(ui_element=self.ui['INVASION_NO_CHARACTER_LEFT'])
        no_right = self.emulator.is_image_on_screen(ui_element=self.ui['INVASION_NO_CHARACTER_RIGHT'])
        if no_main or no_left or no_right:
            self._select_character_filter_by_mission()
        if no_main:
            self.emulator.click_button(self.ui['INVASION_CHARACTER_1'].button)
        if no_left:
            self.emulator.click_button(self.ui['INVASION_CHARACTER_2'].button)
        if no_right:
            self.emulator.click_button(self.ui['INVASION_CHARACTER_3'].button)

    def _select_character_filter_by_mission(self):
        """Select character filter by current mission."""
        for mission_filter in self.mission_filters:
            characters_filter = mission_filter.get_filter(text=self._boss_mission)
            if characters_filter:
                logger.debug(f"Found filter {characters_filter} by {mission_filter.__class__.__name__}")
                self.emulator.click_button(self.ui['INVASION_CHARACTER_FILTER'].button, min_duration=1, max_duration=1)
                self.emulator.click_button(self.ui[characters_filter].button, min_duration=1, max_duration=1)

    def _wait_for_players_and_start_fight(self):
        """Wait for players before start of the fight."""
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
            logger.debug("Waiting for other players before battle.")
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=60, condition=False, period=0.5,
                          ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                              ui_element=self.ui['DISCONNECT_NEW_OPPONENT']):
                    logger.debug("Found disconnect notification. Trying to start again.")
                    self.emulator.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
                    self._wait_for_players_and_start_fight()
                    return
                logger.debug("Battle is loading. Starting manual bot.")
                self._manual_bot_start()
                return
            logger.error("Waiting other emulator very long, trying to reset.")
            self.emulator.click_button(self.ui['WAITING_FOR_OTHER_PLAYERS'].button)

    def _manual_bot_start(self):
        """Start manual bot for the fight."""
        ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
        if wait_until(self.emulator.is_image_on_screen, timeout=2, ui_element=self.ui['INVASION_HOME_BUTTON']):
            if self._chests < self._max_chests:
                self.press_repeat_button(repeat_button_ui='INVASION_REPEAT_BUTTON',
                                         start_button_ui='INVASION_BOSS_FIGHT_START')
            else:
                self.press_home_button(home_button='INVASION_HOME_BUTTON')
            return
        # In case we got back from fight by disconnect or something else
        logger.debug("Any chest after boss fight wasn't acquired.")
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=20,
                      ui_element=self.ui['INVASION_BOSS_FIGHT_START']):
            if self.press_start_button():
                self._wait_for_players_and_start_fight()
