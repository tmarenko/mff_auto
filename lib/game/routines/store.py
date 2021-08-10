import lib.logger as logging
from lib.game.notifications import Notifications
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class EnergyStore(Notifications):
    """Class for working with energy in store."""

    def open_energy_store(self):
        """Open energy store using plus button near energy counter."""
        self.game.go_to_main_menu()
        self.emulator.click_button(self.ui['STORE_COLLECT_ENERGY_PLUS_SIGN'].button)
        self.game.close_ads()
        return wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['STORE_LABEL'])

    def collect_free_energy(self):
        """Collect free daily energy."""
        if not self.open_energy_store():
            logger.error("Failed get to Store - Energy menu.")
            self.game.go_to_main_menu()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['STORE_COLLECT_ENERGY_FREE']):
            logger.debug("Found available free energy button.")
            self.emulator.click_button(self.ui['STORE_COLLECT_ENERGY_FREE'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['STORE_COLLECT_ENERGY_FREE_PURCHASE']):
                self.emulator.click_button(self.ui['STORE_COLLECT_ENERGY_FREE_PURCHASE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE']):
                    logger.info("Free energy collected.")
                    self.emulator.click_button(self.ui['STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_COLLECT_ENERGY_FREE_FULL']):
                    logger.info("Energy is already full, cannot collect.")
                    self.emulator.click_button(self.ui['STORE_COLLECT_ENERGY_FREE_FULL'].button)
        else:
            logger.info("Free energy isn't available right now.")
        self.game.go_to_main_menu()

    def collect_energy_via_assemble_points(self, use_all_points=True):
        """Collect energy using available Assemble Points.

        :param use_all_points: use all available points or not.
        """
        if not self.open_energy_store():
            logger.error("Failed get to Store - Energy menu.")
            self.game.go_to_main_menu()
        recharged = self._recharge_energy_with_points()
        if use_all_points and recharged:
            while recharged:
                logger.debug("Trying to recharge energy again.")
                recharged = self._recharge_energy_with_points()
        self.game.go_to_main_menu()

    def _recharge_energy_with_points(self):
        """Recharge energy with Assemble Points once.

        :return: (bool) was energy recharged or not.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['STORE_RECHARGE_ENERGY_VIA_POINTS']):
            self.emulator.click_button(self.ui['STORE_RECHARGE_ENERGY_VIA_POINTS'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['STORE_RECHARGE_ENERGY_VIA_POINTS_PURCHASE']):
                logger.debug("Purchasing energy via assemble points.")
                self.emulator.click_button(self.ui['STORE_RECHARGE_ENERGY_VIA_POINTS_PURCHASE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE']):
                    logger.info("Energy recharged.")
                    self.emulator.click_button(self.ui['STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE'].button)
                    return True
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_RECHARGE_ENERGY_VIA_NO_POINTS']):
                    logger.info("Not enough Assemble Points for energy recharge.")
                    self.emulator.click_button(self.ui['STORE_RECHARGE_ENERGY_VIA_NO_POINTS'].button)
                    return False
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_RECHARGE_ENERGY_VIA_POINTS_LIMIT']):
                    logger.info("Reached daily limit for energy recharging.")
                    self.emulator.click_button(self.ui['STORE_RECHARGE_ENERGY_VIA_POINTS_LIMIT'].button)
                    return False
        return False


class CharacterStore(Notifications):
    """Class for working with Character Store."""

    def open_character_store(self):
        """Open energy store using plus button near energy counter."""
        self.game.go_to_main_menu()
        self.emulator.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_DIMENSION_CHEST']):
                self.emulator.click_button(self.ui['MAIN_MENU_DIMENSION_CHEST'].button)
                self.close_ads()
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_OPEN_CHARACTER_FROM_DIMENSION_CHEST']):
                    logger.debug("Opening Character tab.")
                    self.emulator.click_button(self.ui['STORE_OPEN_CHARACTER_FROM_DIMENSION_CHEST'].button)
                    return True
        return False

    def _open_hero_chest_tab(self):
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['STORE_CHARACTER_HERO_CHEST_TAB']):
            logger.debug("Opening Hero Chest tab.")
            self.emulator.click_button(self.ui['STORE_CHARACTER_HERO_CHEST_TAB'].button)
            return True
        return False

    def acquire_free_hero_chest(self):
        """Acquire available Free Hero Chest."""
        self.open_character_store()
        if self._open_hero_chest_tab():
            if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_CHARACTER_FREE_HERO_CHEST_BUTTON']):
                logger.info("No available Free Hero Chest, exiting.")
                return self.game.go_to_main_menu()

            logger.info("Free Hero Chest is available.")
            self.emulator.click_button(self.ui['STORE_CHARACTER_FREE_HERO_CHEST_BUTTON'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['STORE_CHARACTER_FREE_HERO_CHEST_BUTTON_ACQUIRE']):
                self.emulator.click_button(self.ui['STORE_CHARACTER_FREE_HERO_CHEST_BUTTON_ACQUIRE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE']):
                    self.emulator.click_button(self.ui['STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE'].button)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['SKIP_CUTSCENE']):
                        self.emulator.click_button(self.ui['SKIP_CUTSCENE'].button)
                        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                      ui_element=self.ui['STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE_CLOSE']):
                            self.emulator.click_button(
                                self.ui['STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE_CLOSE'].button)
                            r_sleep(1)  # Wait for animation
                            logger.info("Free Hero Chest acquired.")
                            self.emulator.click_button(self.ui['MENU_BACK'].button)
                            r_sleep(1)  # Wait for animation
        self.game.go_to_main_menu()
