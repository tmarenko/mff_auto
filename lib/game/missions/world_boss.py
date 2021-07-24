from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, is_strings_similar, r_sleep
import lib.logger as logging

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

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'WB_LABEL')
        self._stage_ui = None
        self._plus_ui = None
        self._minus_ui = None

    @property
    def battle_over_conditions(self):
        def score():
            return self.emulator.is_ui_element_on_screen(self.ui['WB_SCORE'])

        def respawn():
            return self.emulator.is_ui_element_on_screen(self.ui['WB_RESPAWN'])

        return [score, respawn]

    def do_missions(self, times=None, mode=MODE.ULTIMATE, difficulty=0, boss=BOSS.TODAYS_BOSS):
        """Do missions."""
        if mode == self.MODE.ULTIMATE and difficulty == 0:
            logger.error(f"With mode {mode} difficulty should be greater than {difficulty}.")
            return
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(mode=mode, difficulty=difficulty, boss=boss)
            self.end_missions()

    def open_world_boss(self):
        """Open World Boss mission lobby."""
        self.game.select_mode(self.mode_name)
        self._close_special_offer_ad()
        return wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_MISSION_BUTTON'])

    def _close_special_offer_ad(self, timeout=3):
        """Close 'Special Offer' ad.
        # TODO: seems after 7.0.0 update this ad never shows up yet

        :param timeout: timeout of waiting for ads.
        """

        def close_ad():
            if self.emulator.is_ui_element_on_screen(self.ui['WB_CLOSE_OFFER_AD']):
                self.emulator.click_button(self.ui['WB_CLOSE_OFFER_AD'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=1.5,
                              ui_element=self.ui['WB_CLOSE_OFFER_AD_OK']):
                    self.emulator.click_button(self.ui['WB_CLOSE_OFFER_AD_OK'].button)
                    return True
            return False

        for _ in range(timeout):
            ad_closed = wait_until(close_ad, timeout=1)
            logger.debug(f"World Boss Special Offer was closed: {ad_closed}")

    def start_missions(self, mode=MODE.ULTIMATE, difficulty=0, boss=BOSS.TODAYS_BOSS):
        """Start World Boss battles.

        :param mode: mode of battles to start (beginner or normal or ultimate).
        :param difficulty: difficulty of Ultimate mode.
        :param boss: boss to play.
        """
        logger.info(f"{self.stages} stages available, running {mode} mode with difficulty = {difficulty}.")
        if mode != self.MODE.BEGINNER and mode != self.MODE.NORMAL and mode != self.MODE.ULTIMATE:
            logger.error(f"Got wrong mode for battles: {mode}.")
            return
        if not self.open_world_boss():
            logger.warning("Can't get in battles lobby.")
            return
        else:
            if boss != self.BOSS.TODAYS_BOSS and self.ui.get(boss):
                logger.debug(f"Selecting boss {boss}")
                self.emulator.click_button(self.ui[boss].button)
            self.emulator.click_button(self.ui['WB_MISSION_BUTTON'].button)
            if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_READY_BUTTON']):
                logger.error("Can't find READY button after selecting the boss.")
                return
        if mode == self.MODE.BEGINNER:
            logger.info("Starting BEGINNER battle.")
            self.emulator.click_button(self.ui['WB_BEGINNER_MODE'].button)
        if mode == self.MODE.NORMAL:
            logger.info("Starting NORMAL battle.")
            self.emulator.click_button(self.ui['WB_NORMAL_MODE'].button)
        if mode == self.MODE.ULTIMATE:
            logger.info("Starting ULTIMATE/LEGEND battle.")
            self.emulator.click_button(self.ui['WB_ULTIMATE_MODE'].button)
            self._select_stage_level(level_num=difficulty)

        while self.stages > 0:
            if not self._start_world_boss_battle():
                logger.error("Failed to start battle. Returning to main menu.")
                return self.game.go_to_main_menu()
            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['WB_RESPAWN']):
                logger.info("Lost battle. Respawning.")
                self.emulator.click_button(self.ui['WB_RESPAWN'].button)
                if not wait_until(self.emulator.is_ui_element_on_screen, timeout=10, ui_element=self.ui['WB_SCORE']):
                    logger.warning("Something went wrong while respawning after lost battle.")
            else:
                self.stages -= 1
            if self.stages > 0:
                self.press_repeat_button(repeat_button_ui="WB_REPEAT_BUTTON", start_button_ui="WB_READY_BUTTON")
            else:
                self.press_home_button(home_button="WB_HOME_BUTTON")
        logger.info("No more stages.")

    def _start_world_boss_battle(self, check_inventory=True):
        """Start World Boss battle.

        :param: check_inventory check for full inventory or not.
        """
        self.emulator.click_button(self.ui['WB_READY_BUTTON'].button)
        self.close_mission_notifications()
        self.close_after_mission_notifications()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_SET_TEAM']):
            self._deploy_characters()
            self.emulator.click_button(self.ui['WB_SET_TEAM'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['WB_UNAVAILABLE_CHARACTER']):
                logger.warning("Stopping battle because your team has unavailable characters.")
                self.emulator.click_button(self.ui['WB_UNAVAILABLE_CHARACTER'].button)
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['WB_LOW_VALOR_OR_ATTACK']):
                self.emulator.click_button(self.ui['WB_LOW_VALOR_OR_ATTACK'].button)
                # Second notification about ATK is similar
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['WB_LOW_VALOR_OR_ATTACK']):
                    self.emulator.click_button(self.ui['WB_LOW_VALOR_OR_ATTACK'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_START_BUTTON']):
                self._deploy_allies()
                self.emulator.click_button(self.ui['WB_START_BUTTON'].button)
                if check_inventory and wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                                                  ui_element=self.ui['INVENTORY_FULL']):
                    logger.warning("Stopping battle because inventory is full.")
                    self.emulator.click_button(self.ui['INVENTORY_FULL'].button)
                    self.stages *= 0
                    return False
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['WB_NOT_FULL_ALLY_TEAM']):
                    self.emulator.click_button(self.ui['WB_NOT_FULL_ALLY_TEAM'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['WB_EXCLUDE_CHARACTERS_FROM_ALLIES']):
                    self.emulator.click_button(self.ui['WB_EXCLUDE_CHARACTERS_FROM_ALLIES'].button)
                ManualBattleBot(self.game, self.battle_over_conditions).fight(move_around=True)
                self.close_mission_notifications()
                return True
            logger.warning("Failed to locate START button.")
            return False
        logger.warning("Failed to set team.")

    def _deploy_characters(self):
        """Deploy 3 characters to battle."""
        no_main = self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_MAIN'])
        no_left = self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_LEFT'])
        no_right = self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_RIGHT'])
        if no_main or no_left or no_right:
            self.emulator.click_button(self.ui['WB_CHARACTER_FILTER'].button, min_duration=1, max_duration=1)
            # selecting ALL filter for top characters
            self.emulator.click_button(self.ui['WB_CHARACTER_FILTER'].button, min_duration=1, max_duration=1)
        if no_main:
            self.emulator.click_button(self.ui['WB_NON_FEATURED_CHARACTER_1'].button)
        if no_left:
            self.emulator.click_button(self.ui['WB_NON_FEATURED_CHARACTER_2'].button)
        if no_right:
            self.emulator.click_button(self.ui['WB_NON_FEATURED_CHARACTER_3'].button)

    def _deploy_allies(self):
        """Deploy 4 characters as allies to battle."""
        if self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_ALLY_1']):
            self.emulator.click_button(self.ui['WB_ALLY_CHARACTER_1'].button)
        if self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_ALLY_2']):
            self.emulator.click_button(self.ui['WB_ALLY_CHARACTER_2'].button)
        if self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_ALLY_3']):
            self.emulator.click_button(self.ui['WB_ALLY_CHARACTER_3'].button)
        if self.emulator.is_image_on_screen(ui_element=self.ui['WB_NO_CHARACTER_ALLY_4']):
            self.emulator.click_button(self.ui['WB_ALLY_CHARACTER_4'].button)

    @property
    def stage_ui(self):
        """Get UI of current stage counter.

        :return: UI element for stage counter.
        """
        if self._stage_ui is None:
            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['WB_ULTIMATE_STAGE_LABEL']):
                logger.debug("Selected ULTIMATE stage label.")
                self._stage_ui = self.ui['WB_ULTIMATE_STAGE']
            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['WB_LEGEND_STAGE_LABEL']):
                logger.debug("Selected LEGEND stage label.")
                self._stage_ui = self.ui['WB_LEGEND_STAGE']
        return self._stage_ui

    @property
    def plus_ui(self):
        """Get UI element for PLUS sign in stage counter."""
        if self._plus_ui is None:
            if self.stage_ui == self.ui['WB_ULTIMATE_STAGE']:
                self._plus_ui = self.ui['WB_ULTIMATE_PLUS']
            if self.stage_ui == self.ui['WB_LEGEND_STAGE']:
                self._plus_ui = self.ui['WB_LEGEND_PLUS']
        return self._plus_ui

    @property
    def minus_ui(self):
        """Get UI element for MINUS sign in stage counter."""
        if self._minus_ui is None:
            if self.stage_ui == self.ui['WB_ULTIMATE_STAGE']:
                self._minus_ui = self.ui['WB_ULTIMATE_MINUS']
            if self.stage_ui == self.ui['WB_LEGEND_STAGE']:
                self._minus_ui = self.ui['WB_LEGEND_MINUS']
        return self._minus_ui

    @property
    def stage_level(self):
        """Get current stage level.

        :return: current stage level.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['WB_READY_BUTTON']):
            stage_str = self.emulator.get_screen_text(ui_element=self.stage_ui)
            try:
                stage_int = int(stage_str)
            except ValueError:
                logger.critical(f"Cannot convert stage to integer: {stage_str}")
                stage_int = 0
            return stage_int
        return 0

    def _increase_stage_level(self):
        """Increase current stage level"""
        logger.info("Increasing stage difficulty level.")
        self.emulator.click_button(self.plus_ui.button, min_duration=0.01, max_duration=0.01)

    def _decrease_stage_level(self):
        """Decrease current stage level"""
        logger.info("Decreasing stage difficulty level.")
        self.emulator.click_button(self.minus_ui.button, min_duration=0.01, max_duration=0.01)

    def _select_stage_level(self, level_num=20):
        """Select stage level.

        :param level_num: level to select.
        """
        if level_num == 0:
            logger.debug(f"Stage level is {level_num}. Stage won't change.")
        if level_num > 99 or level_num < 0:
            logger.error(f"Stage level should be between 1 and 99, got {level_num} instead.")
            return
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
        """Change Today's World Boss.

        :param world_boss: name or list of the Bosses' names.
        :param max_resets: number of maximum resets.
        """
        if max_resets == 0 or not world_boss:
            logger.error(f"No boss was selected ({world_boss}) or max resets is invalid ({max_resets}).")
            return
        target_world_boss = world_boss if isinstance(world_boss, list) else [world_boss]
        self.stages = max_resets
        if not self.open_world_boss():
            logger.warning("Can't get in battles lobby.")
            return
        self.emulator.click_button(self.ui['WB_RESET_TODAYS_BOSS'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['WB_RESET_TODAYS_BOSS_MENU']):
            logger.debug("Reset Menu is opened.")
            return self._reset_world_boss(target_world_boss=target_world_boss, current_reset=0, max_resets=max_resets)
        else:
            logger.warning("Can't open Reset Menu. Probably your VIP status is low.")
        self.stages = 0

    def _reset_world_boss(self, target_world_boss, current_reset, max_resets):
        """Resets World Boss in reset menu.

        :param target_world_boss: name or list of the Bosses' names for reset.
        :param current_reset: number of current reset to compare with maximum.
        :param max_resets: number of maximum resets.
        """
        if current_reset > max_resets:
            logger.warning(f"Achieved max resets of {current_reset} for Today's World Boss.")
        current_world_boss = self.emulator.get_screen_text(self.ui['WB_RESET_TODAYS_BOSS_NAME'])
        logger.debug(f"Current boss of the day is {current_world_boss}; resetting for {target_world_boss}")
        target_world_boss_found = [is_strings_similar(boss, current_world_boss) for boss in target_world_boss]
        if any(target_world_boss_found):
            logger.debug("No need to reset World Boss. Exiting reset menu.")
            self.emulator.click_button(self.ui['WB_RESET_TODAYS_BOSS_MENU_CLOSE'].button)
            return self.game.go_to_main_menu()
        else:
            logger.debug("Resetting World Boss of the day.")
            self.emulator.click_button(self.ui['WB_RESET_TODAYS_BOSS_BUTTON'].button)
            r_sleep(1)  # Wait for reset animation
            return self._reset_world_boss(target_world_boss=target_world_boss, current_reset=current_reset + 1,
                                          max_resets=max_resets)
