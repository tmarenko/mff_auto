from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until
import lib.logger as logging

logger = logging.get_logger(__name__)


class WorldBossInvasion(Missions):
    """Class for working with World Boss Invasions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'INVASION_MENU_LABEL')
        self._chests = None
        self._max_chests = None

    @property
    def battle_over_conditions(self):
        def chest():
            return self.player.is_ui_element_on_screen(self.ui['INVASION_SLOT_CHEST'])

        def failed():
            return self.player.is_ui_element_on_screen(self.ui['INVASION_FAILED'])

        return [chest, failed]

    def do_missions(self, times=None):
        """Do missions."""
        self.start_missions(times=times)
        self.end_missions()

    def start_missions(self, times=None):
        """Start World Boss Invasion."""
        if self.go_to_wbi():
            logger.info(f"World Boss Invasion: {self.chests} of {self.max_chests} chests.")
            if self.chests > 0:
                if not self.acquire_chests():
                    return
                self._get_chests_count()
            if times:
                self._max_chests = times
            if self.chests < self.max_chests and self.find_boss_fight():
                while self.chests < self.max_chests:
                    if self.press_start_button():
                        self.wait_for_players()
        logger.info("No more stages for World Boss Invasions.")

    def end_missions(self):
        """End missions."""
        if not self.game.is_main_menu():
            self.game.player.click_button(self.ui['HOME'].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def go_to_wbi(self):
        """Go to World Boss Invasion missions.

        :return: True or False: is WBI missions open.
        """
        self.game.go_to_coop()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_LABEL']):
            self.player.click_button(self.ui['INVASION_LABEL'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_MENU_LABEL']):
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVASION_MANAGE_CHESTS'])
        return False

    def _get_chests_count(self):
        """Receive current chests and max chests amount."""
        chests_count = self.player.get_screen_text(ui_element=self.ui['INVASION_STAGES'])
        logger.debug(f"World Boss Invasion: chest text: {chests_count}")
        current_chest, max_chest = self.game.get_current_and_max_values_from_text(chests_count)
        self._chests = 5 if current_chest > 5 else current_chest
        self._max_chests = 5 if max_chest > 5 else max_chest
        logger.info(f"World Boss Invasion: {self._chests} chests out of {self._max_chests} founded.")

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
        self.player.click_button(self.ui['INVASION_MANAGE_CHESTS'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_CHESTS_MENU_LABEL']):
            for chest_index in range(1, self.max_chests + 1):
                if not self.acquire_chest(chest_index):
                    logger.error(f"Can't acquire chest {chest_index}, exiting.")
                    return False
        logger.debug("All chests obtained, going back to WBI.")
        self.player.click_button(self.ui['MENU_BACK'].button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_MANAGE_CHESTS'])

    def acquire_chest(self, chest_index):
        """Acquire chest by chest index.

        :param chest_index: chest index (from 1 to max chests + 1)
        :return: True or False: was chest acquired.
        """
        chest_ui = self.ui[f'INVASION_CHEST_AVAILABLE_{chest_index}']
        if wait_until(self.player.is_ui_element_on_screen, timeout=1, ui_element=chest_ui):
            logger.debug(f"Chest {chest_index} is available. Trying to open.")
            self.player.click_button(chest_ui.button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_SKIP_CHEST']):
                while self.player.is_ui_element_on_screen(ui_element=self.ui['INVASION_SKIP_CHEST']):
                    logger.debug("Skipping chests items.")
                    self.player.click_button(self.ui['INVASION_SKIP_CHEST'].button, min_duration=0.5, max_duration=0.8)
                while not self.player.is_ui_element_on_screen(ui_element=self.ui['INVASION_CHESTS_MENU_LABEL']):
                    self.player.click_button(self.ui['INVASION_SKIP_CHEST'].button, min_duration=0.5, max_duration=0.8)
                logger.debug("Chest acquired, going back.")
                return True
            return False
        return True

    def find_boss_fight(self):
        """Find available boss fight and enter it.

        :return: True or False: was fight found and entered.
        """
        weekly_name = self.player.get_screen_text(ui_element=self.ui['INVASION_NAME'])
        logger.debug(f"WBI weekly: {weekly_name}")
        for bosses in ['INVASION_TWILIGHT_BATTLE_', 'INVASION_BLACK_ORDER_BATTLE_']:
            for boss_index in range(1, 8):
                boss_ui = self.ui[f'{bosses}{boss_index}']
                boss_time = self.player.get_screen_text(ui_element=boss_ui)
                if boss_time:
                    logger.debug(f"Found boss with UI: {boss_ui.name} with time {boss_time}")
                    self.player.click_button(boss_ui.button)
                    if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVASION_BOSS_FIGHT_ENTER']):
                        self.player.click_button(self.ui['INVASION_BOSS_FIGHT_ENTER'].button)
                        return True
                    logger.warning(f"Something went wrong with found boss {boss_ui.name}")
                    if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVASION_BOSS_FIGHT_CLOSE']):
                        logger.warning(f"Closing {boss_ui.name}")
                        self.player.click_button(self.ui['INVASION_BOSS_FIGHT_CLOSE'].button)
        logger.warning("Failed to found boss.")
        return False

    def check_fight_notifications(self):
        """Check fight notifications about any obstacles to start a fight.

        :return: True or False: can we start a fight or not.
        """
        waiting_for_other_players = self.player.is_ui_element_on_screen(
            ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS'])
        if not waiting_for_other_players:
            not_enough_energy = self.player.is_ui_element_on_screen(ui_element=self.ui['NOT_ENOUGH_ENERGY'])
            not_enough_characters = self.player.is_ui_element_on_screen(
                ui_element=self.ui['INVASION_NOT_ENOUGH_CHARACTERS'])
            if not_enough_characters or not_enough_energy:
                name = 'NOT_ENOUGH_ENERGY' if not_enough_energy else 'INVASION_NOT_ENOUGH_CHARACTERS'
                self.player.click_button(self.ui[name].button)
                self._chests = self._max_chests
            return False
        return True

    def press_start_button(self):
        """Press start button of the mission.

        :return: was button clicked successfully.
        """
        logger.debug(f"Pressing START button.")
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVASION_BOSS_FIGHT_START']):
            self.deploy_characters()
            self.player.click_button(self.ui['INVASION_BOSS_FIGHT_START'].button)
            if wait_until(self.check_fight_notifications, timeout=10):
                return True
        if wait_until(self.player.is_ui_element_on_screen, timeout=2,
                      ui_element=self.ui['DISCONNECT_NEW_OPPONENT']):
            logger.debug("Found disconnect notification. Trying to start again.")
            self.player.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
            return True
        logger.warning("Unable to press START button.")
        return False

    def deploy_characters(self):
        """Deploy 3 characters to battle."""
        no_main = self.player.is_image_on_screen(ui_element=self.ui['INVASION_NO_CHARACTER_MAIN'])
        no_left = self.player.is_image_on_screen(ui_element=self.ui['INVASION_NO_CHARACTER_LEFT'])
        no_right = self.player.is_image_on_screen(ui_element=self.ui['INVASION_NO_CHARACTER_RIGHT'])
        if no_main:
            self.player.click_button(self.ui['INVASION_CHARACTER_1'].button)
        if no_left:
            self.player.click_button(self.ui['INVASION_CHARACTER_2'].button)
        if no_right:
            self.player.click_button(self.ui['INVASION_CHARACTER_3'].button)

    def wait_for_players(self):
        """Wait for players before start of the fight."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
            logger.debug("Waiting for other players before battle.")
            if wait_until(self.player.is_ui_element_on_screen, timeout=60, condition=False, period=0.5,
                          ui_element=self.ui['WAITING_FOR_OTHER_PLAYERS']):
                if wait_until(self.player.is_ui_element_on_screen, timeout=2,
                              ui_element=self.ui['DISCONNECT_NEW_OPPONENT']):
                    logger.debug("Found disconnect notification. Trying to start again.")
                    self.player.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
                    self.wait_for_players()
                    return
                logger.debug("Battle is loading. Starting manual bot.")
                self.manual_bot_start()
                return
            logger.error("Waiting other player very long.")
            self.player.click_button(self.ui['WAITING_FOR_OTHER_PLAYERS'].button)

    def manual_bot_start(self):
        """Start manual bot for the fight."""
        ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions).fight()
        if self.player.is_ui_element_on_screen(ui_element=self.ui['INVASION_SLOT_CHEST']):
            self.player.click_button(self.ui['INVASION_SLOT_CHEST'].button)
            self._chests += 1
        if wait_until(self.player.is_image_on_screen, timeout=2, ui_element=self.ui['INVASION_HOME_BUTTON']):
            if self._chests < self._max_chests:
                self.press_repeat_button(repeat_button_ui='INVASION_REPEAT_BUTTON',
                                         start_button_ui='INVASION_BOSS_FIGHT_START')
            else:
                self.press_home_button(home_button='INVASION_HOME_BUTTON')
            return
        # In case we got back from fight by disconnect or something else
        logger.debug("Any chest after boss fight wasn't acquired.")
        if wait_until(self.player.is_ui_element_on_screen, timeout=20, ui_element=self.ui['INVASION_BOSS_FIGHT_START']):
            if self.press_start_button():
                self.wait_for_players()
