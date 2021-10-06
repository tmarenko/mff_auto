import lib.logger as logging
from lib.functions import wait_until, is_strings_similar, r_sleep
from lib.game import ui
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class WorldBoss(Missions):
    """Class for working with World Boss missions."""

    class MODE:

        BEGINNER = "BEGINNER"
        NORMAL = "NORMAL"
        ULTIMATE = "ULTIMATE"

    class BOSS:

        TODAYS_BOSS = "TODAYS_BOSS"
        PROXIMA_MIDNIGHT = "WB_BOSS_PROXIMA_MIDNIGHT"
        BLACK_DWARF = "WB_BOSS_BLACK_DWARF"
        CORVUS_GLAIVE = "WB_BOSS_CORVUS_GLAIVE"
        SUPERGIANT = "WB_BOSS_SUPERGIANT"
        EBONY_MAW = "WB_BOSS_EBONY_MAW"
        THANOS = "WB_BOSS_THANOS"
        QUICKSILVER = "WB_BOSS_QUICKSILVER"
        CABLE = "WB_BOSS_CABLE"
        SCARLET_WITCH = "WB_BOSS_SCARLET_WITCH"
        APOCALYPSE = "WB_BOSS_APOCALYPSE"
        KNULL = "WB_BOSS_KNULL"
        MEPHISTO = "WB_BOSS_MEPHISTO"

    class BOSS_OF_THE_DAY:

        PROXIMA_MIDNIGHT = "Proxima Midnight"
        BLACK_DWARF = "Black Dwarf"
        CORVUS_GLAIVE = "Corvus Glave"
        SUPERGIANT = "Supergiant"
        EBONY_MAW = "Ebony Maw"
        THANOS = "Thanos"
        QUICKSILVER = "Quicksilver"
        CABLE = "Cable"
        SCARLET_WITCH = "Scarlet Witch"
        APOCALYPSE = "Apocalypse"
        KNULL = "Knull"
        MEPHISTO = "Mephisto"

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='WORLD BOSS')
        self._stage_ui = None
        self._plus_ui = None
        self._minus_ui = None
        self._sync_character_and_ally_teams = False

    @property
    def battle_over_conditions(self):
        def score():
            return self.emulator.is_ui_element_on_screen(ui.WB_SCORE)

        def respawn():
            return self.emulator.is_ui_element_on_screen(ui.WB_RESPAWN)

        return [score, respawn]

    def do_missions(self, times=None, mode=MODE.ULTIMATE, difficulty=0, boss=BOSS.TODAYS_BOSS,
                    sync_character_and_ally_teams=False):
        """Does missions."""
        if mode == self.MODE.ULTIMATE and difficulty == 0:
            return logger.error(f"With mode {mode} difficulty should be greater than {difficulty}.")
        self._sync_character_and_ally_teams = sync_character_and_ally_teams
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(mode=mode, difficulty=difficulty, boss=boss)
            self.end_missions()

    def open_world_boss(self):
        """Opens World Boss mission lobby."""
        if self.game.select_mode(self.mode_name):
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_MISSION_BUTTON)

    def start_missions(self, mode=MODE.ULTIMATE, difficulty=0, boss=BOSS.TODAYS_BOSS):
        """Starts World Boss battles.

        :param str mode: mode of battles to start (beginner or normal or ultimate).
        :param int difficulty: difficulty of Ultimate mode.
        :param str boss: boss to play.
        """
        logger.info(f"{self.stages} stages available, running {mode} mode with difficulty = {difficulty}.")
        if mode != self.MODE.BEGINNER and mode != self.MODE.NORMAL and mode != self.MODE.ULTIMATE:
            return logger.error(f"Got wrong mode for battles: {mode}.")
        if not self.open_world_boss():
            return logger.error("Can't get in battles lobby.")
        if boss != self.BOSS.TODAYS_BOSS and ui.get_by_name(boss):
            logger.debug(f"Selecting boss {boss}")
            self.emulator.click_button(ui.get_by_name(boss))
        self.emulator.click_button(ui.WB_MISSION_BUTTON)
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_READY_BUTTON):
            return logger.error(f"Can't find {ui.WB_READY_BUTTON} button after selecting the boss.")
        if mode == self.MODE.BEGINNER:
            logger.info("Starting BEGINNER battle.")
            self.emulator.click_button(ui.WB_BEGINNER_MODE)
        if mode == self.MODE.NORMAL:
            logger.info("Starting NORMAL battle.")
            self.emulator.click_button(ui.WB_NORMAL_MODE)
        if mode == self.MODE.ULTIMATE:
            logger.info("Starting ULTIMATE/LEGEND battle.")
            self.emulator.click_button(ui.WB_ULTIMATE_MODE)
            self._select_stage_level(level_num=difficulty)

        while self.stages > 0:
            if not self._start_world_boss_battle():
                logger.error("Failed to start battle. Returning to main menu.")
                return self.game.go_to_main_menu()
            if self.emulator.is_ui_element_on_screen(ui_element=ui.WB_RESPAWN):
                logger.info("Lost battle. Respawning.")
                self.emulator.click_button(ui.WB_RESPAWN)
                if not wait_until(self.emulator.is_ui_element_on_screen, timeout=10, ui_element=ui.WB_SCORE):
                    logger.error("Something went wrong while respawning after lost battle.")
            else:
                self.stages -= 1
            logger.debug(f"{self.stages} stages left to complete.")
            if self.stages > 0:
                self.press_repeat_button(repeat_button_ui=ui.WB_REPEAT_BUTTON, start_button_ui=ui.WB_READY_BUTTON)
            else:
                self.press_home_button(home_button=ui.WB_HOME_BUTTON)
        logger.info("No more stages.")

    def _start_world_boss_battle(self, check_inventory=True):
        """Starts World Boss battle.

        :param bool check_inventory: check for full inventory or not.
        """
        self.emulator.click_button(ui.WB_READY_BUTTON)
        self.close_mission_notifications()
        self.close_after_mission_notifications()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_SET_TEAM):
            self._deploy_characters()
            self.emulator.click_button(ui.WB_SET_TEAM)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_UNAVAILABLE_CHARACTER):
                logger.warning("Stopping battle because your team has unavailable characters.")
                self.emulator.click_button(ui.WB_UNAVAILABLE_CHARACTER)
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_LOW_VALOR_OR_ATTACK):
                self.emulator.click_button(ui.WB_LOW_VALOR_OR_ATTACK)
                # Second notification about ATK is similar
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_LOW_VALOR_OR_ATTACK):
                    self.emulator.click_button(ui.WB_LOW_VALOR_OR_ATTACK)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_START_BUTTON):
                self._deploy_allies()
                self.emulator.click_button(ui.WB_START_BUTTON)
                if check_inventory and wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                                                  ui_element=ui.INVENTORY_FULL):
                    logger.warning("Stopping battle because inventory is full.")
                    self.emulator.click_button(ui.INVENTORY_FULL)
                    self.stages *= 0
                    return False
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_NOT_FULL_ALLY_TEAM):
                    self.emulator.click_button(ui.WB_NOT_FULL_ALLY_TEAM)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_EXCLUDE_CHARACTERS_FROM_ALLIES):
                    self.emulator.click_button(ui.WB_EXCLUDE_CHARACTERS_FROM_ALLIES)
                ManualBattleBot(self.game, self.battle_over_conditions).fight(move_around=True)
                self.close_mission_notifications()
                return True
            logger.error(f"Failed to locate {ui.WB_START_BUTTON} button.")
            return False
        logger.error("Failed to set team.")

    def _deploy_characters(self):
        """Deploys 3 characters to battle."""
        if self._sync_character_and_ally_teams:
            logger.debug(f"Selecting Character Team #{self.stages}")
            self.emulator.click_button(ui.get_by_name(f'WB_SELECT_CHARACTER_TEAM_{self.stages}'))
        no_main = self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_MAIN)
        no_left = self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_LEFT)
        no_right = self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_RIGHT)
        if no_main or no_left or no_right:
            self.emulator.click_button(ui.WB_CHARACTER_FILTER, min_duration=1, max_duration=1)
            # selecting ALL filter for top characters
            self.emulator.click_button(ui.WB_CHARACTER_FILTER, min_duration=1, max_duration=1)
        if no_main:
            self.emulator.click_button(ui.WB_NON_FEATURED_CHARACTER_1)
        if no_left:
            self.emulator.click_button(ui.WB_NON_FEATURED_CHARACTER_2)
        if no_right:
            self.emulator.click_button(ui.WB_NON_FEATURED_CHARACTER_3)

    def _deploy_allies(self):
        """Deploys 4 characters as allies to battle."""
        if self._sync_character_and_ally_teams:
            logger.debug(f"Selecting Ally Team #{self.stages}")
            self.emulator.click_button(ui.get_by_name(f'WB_SELECT_ALLY_TEAM_{self.stages}'))
        if self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_ALLY_1):
            self.emulator.click_button(ui.WB_ALLY_CHARACTER_1)
        if self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_ALLY_2):
            self.emulator.click_button(ui.WB_ALLY_CHARACTER_2)
        if self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_ALLY_3):
            self.emulator.click_button(ui.WB_ALLY_CHARACTER_3)
        if self.emulator.is_image_on_screen(ui_element=ui.WB_NO_CHARACTER_ALLY_4):
            self.emulator.click_button(ui.WB_ALLY_CHARACTER_4)

    @property
    def stage_ui(self):
        """Gets UI element of current stage counter.

        :rtype: ui.UIElement
        """
        if self._stage_ui is None:
            if self.emulator.is_ui_element_on_screen(ui_element=ui.WB_ULTIMATE_STAGE_LABEL):
                logger.debug("Selected ULTIMATE stage label.")
                self._stage_ui = ui.WB_ULTIMATE_STAGE
            if self.emulator.is_ui_element_on_screen(ui_element=ui.WB_LEGEND_STAGE_LABEL):
                logger.debug("Selected LEGEND stage label.")
                self._stage_ui = ui.WB_LEGEND_STAGE
        return self._stage_ui

    @property
    def plus_ui(self):
        """Gets UI element for PLUS sign in stage counter.

        :rtype: ui.UIElement
        """
        if self._plus_ui is None:
            if self.stage_ui == ui.WB_ULTIMATE_STAGE:
                self._plus_ui = ui.WB_ULTIMATE_PLUS
            if self.stage_ui == ui.WB_LEGEND_STAGE:
                self._plus_ui = ui.WB_LEGEND_PLUS
        return self._plus_ui

    @property
    def minus_ui(self):
        """Gets UI element for MINUS sign in stage counter.

        :rtype: ui.UIElement
        """
        if self._minus_ui is None:
            if self.stage_ui == ui.WB_ULTIMATE_STAGE:
                self._minus_ui = ui.WB_ULTIMATE_MINUS
            if self.stage_ui == ui.WB_LEGEND_STAGE:
                self._minus_ui = ui.WB_LEGEND_MINUS
        return self._minus_ui

    @property
    def stage_level(self):
        """Gets current stage level.

        :rtype: int
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_READY_BUTTON):
            stage_str = self.emulator.get_screen_text(ui_element=self.stage_ui)
            try:
                stage_int = int(stage_str)
            except ValueError:
                logger.critical(f"Cannot convert stage to integer: {stage_str}")
                stage_int = 0
            return stage_int
        return 0

    def _increase_stage_level(self):
        """Increases current stage level"""
        logger.info("Increasing stage difficulty level.")
        self.emulator.click_button(self.plus_ui, min_duration=0.01, max_duration=0.01)

    def _decrease_stage_level(self):
        """Decreases current stage level"""
        logger.info("Decreasing stage difficulty level.")
        self.emulator.click_button(self.minus_ui, min_duration=0.01, max_duration=0.01)

    def _select_stage_level(self, level_num=20):
        """Selects stage level.

        :param int level_num: level to select.
        """
        if level_num == 0:
            logger.debug(f"Stage level is {level_num}. Stage won't change.")
        if level_num > 99 or level_num < 0:
            return logger.error(f"Stage level should be between 1 and 99, got {level_num} instead.")
        safe_counter = 0
        diff = abs(level_num - self.stage_level)
        while self.stage_level != level_num:
            if safe_counter > diff:
                logger.warning(f"Stage level was changed more than {safe_counter}. "
                               f"Your max stage level probably lesser than {level_num}.")
                break
            safe_counter += 1
            if self.stage_level > level_num:
                self._decrease_stage_level()
            if self.stage_level < level_num:
                self._increase_stage_level()

    def change_world_boss_of_the_day(self, world_boss, max_resets=0):
        """Changes Today's World Boss.

        :param str | list[str] world_boss: name or list of the Bosses' names.
        :param int max_resets: number of maximum resets.
        """
        if max_resets == 0 or not world_boss:
            return logger.error(f"No boss was selected ({world_boss}) or max resets is invalid ({max_resets}).")
        target_world_boss = world_boss if isinstance(world_boss, list) else [world_boss]
        if not self.open_world_boss():
            return logger.error("Can't get in battles lobby.")
        self.emulator.click_button(ui.WB_RESET_TODAYS_BOSS)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.WB_RESET_TODAYS_BOSS_MENU):
            logger.debug("Reset Menu is opened.")
            self._reset_world_boss(target_world_boss=target_world_boss, current_reset=0, max_resets=max_resets)
            return self.end_missions()
        logger.warning("Can't open Reset Menu. Probably your VIP status is low.")
        self.end_missions()

    def _reset_world_boss(self, target_world_boss, current_reset, max_resets):
        """Resets World Boss in reset menu.

        :param list[str] target_world_boss: name or list of the Bosses' names for reset.
        :param int current_reset: number of current reset to compare with maximum.
        :param int max_resets: number of maximum resets.
        """
        if current_reset > max_resets:
            return logger.warning(f"Achieved max resets of {current_reset} for Today's World Boss.")
        current_world_boss = self.emulator.get_screen_text(ui.WB_RESET_TODAYS_BOSS_NAME)
        logger.debug(f"Current boss of the day is {current_world_boss}; resetting for {target_world_boss}")
        target_world_boss_found = [is_strings_similar(boss, current_world_boss) for boss in target_world_boss]
        if any(target_world_boss_found):
            logger.debug("No need to reset World Boss. Exiting reset menu.")
            self.emulator.click_button(ui.WB_RESET_TODAYS_BOSS_MENU_CLOSE)
            return self.game.go_to_main_menu()
        else:
            logger.debug("Resetting World Boss of the day.")
            self.emulator.click_button(ui.WB_RESET_TODAYS_BOSS_BUTTON)
            r_sleep(1)  # Wait for reset animation
            return self._reset_world_boss(target_world_boss=target_world_boss, current_reset=current_reset + 1,
                                          max_resets=max_resets)
