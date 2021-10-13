import lib.logger as logging
from lib.functions import wait_until, r_sleep
from lib.game import ui
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)


class Store(Notifications):

    def is_store_open(self):
        """Checks if Store is open.

        :rtype: bool
        """
        return self.emulator.is_ui_element_on_screen(ui.STORE_LABEL) or \
               self.emulator.is_ui_element_on_screen(ui.STORE_LABEL_2)


class EnergyStore(Store):
    """Class for working with energy in store."""

    def open_energy_store(self):
        """Opens energy store using plus button near energy counter."""
        self.game.go_to_main_menu()
        self.emulator.click_button(ui.STORE_COLLECT_ENERGY_PLUS_SIGN)
        self.game.close_ads()
        return wait_until(self.is_store_open)

    def collect_free_energy(self):
        """Collects free daily energy."""
        if not self.open_energy_store():
            logger.error("Failed get to Store - Energy menu.")
            return self.game.go_to_main_menu()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_COLLECT_ENERGY_FREE):
            logger.debug("Found available free energy button.")
            self.emulator.click_button(ui.STORE_COLLECT_ENERGY_FREE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_COLLECT_ENERGY_FREE_PURCHASE):
                self.emulator.click_button(ui.STORE_COLLECT_ENERGY_FREE_PURCHASE)
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE):
                    logger.info("Free energy collected.")
                    self.emulator.click_button(ui.STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_COLLECT_ENERGY_FREE_FULL):
                    logger.info("Energy is already full, can't collect.")
                    self.emulator.click_button(ui.STORE_COLLECT_ENERGY_FREE_FULL)
        else:
            logger.info("Free energy isn't available right now.")
        self.game.go_to_main_menu()

    def collect_energy_via_assemble_points(self, use_all_points=True):
        """Collects energy using available Assemble Points.

        :param bool use_all_points: use all available points or not.
        """
        if not self.open_energy_store():
            logger.error("Failed get to Store - Energy menu.")
            return self.game.go_to_main_menu()
        recharged = self._recharge_energy_with_points()
        if use_all_points and recharged:
            while recharged:
                logger.debug("Trying to recharge energy again.")
                recharged = self._recharge_energy_with_points()
        self.game.go_to_main_menu()

    def _recharge_energy_with_points(self):
        """Recharges energy with Assemble Points once.

        :return: was energy recharged or not.
        :rtype: bool
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_RECHARGE_ENERGY_VIA_POINTS):
            self.emulator.click_button(ui.STORE_RECHARGE_ENERGY_VIA_POINTS)
            if wait_until(self.emulator.is_ui_element_on_screen,
                          ui_element=ui.STORE_RECHARGE_ENERGY_VIA_POINTS_PURCHASE):
                logger.debug("Purchasing energy via assemble points.")
                self.emulator.click_button(ui.STORE_RECHARGE_ENERGY_VIA_POINTS_PURCHASE)
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE):
                    logger.info("Energy recharged.")
                    self.emulator.click_button(ui.STORE_COLLECT_ENERGY_FREE_PURCHASE_CLOSE)
                    return True
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_RECHARGE_ENERGY_VIA_NO_POINTS):
                    logger.info("Not enough Assemble Points for energy recharge.")
                    self.emulator.click_button(ui.STORE_RECHARGE_ENERGY_VIA_NO_POINTS)
                    return False
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_RECHARGE_ENERGY_VIA_POINTS_LIMIT):
                    logger.info("Reached daily limit for energy recharging.")
                    self.emulator.click_button(ui.STORE_RECHARGE_ENERGY_VIA_POINTS_LIMIT)
                    return False
        return False


class CharacterStore(Store):
    """Class for working with Character Store."""

    def open_character_store(self):
        """Opens Character store using Dimension Chest button in Main Menu."""
        self.game.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_DIMENSION_CHEST):
                self.emulator.click_button(ui.MAIN_MENU_DIMENSION_CHEST)
                self.close_ads()
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_OPEN_CHARACTER_FROM_DIMENSION_CHEST):
                    logger.debug("Opening Character tab.")
                    self.emulator.click_button(ui.STORE_OPEN_CHARACTER_FROM_DIMENSION_CHEST)
                    return True
        return False

    def _open_hero_chest_tab(self):
        """Open `Hero` chest tab in the Store."""
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_CHARACTER_HERO_CHEST_TAB):
            logger.debug("Opening Hero Chest tab.")
            self.emulator.click_button(ui.STORE_CHARACTER_HERO_CHEST_TAB)
            return True
        return False

    def acquire_free_hero_chest(self):
        """Acquires available Free Hero Chest."""
        self.open_character_store()
        if self._open_hero_chest_tab():
            if not wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_CHARACTER_FREE_HERO_CHEST_BUTTON):
                logger.info("No available Free Hero Chest, exiting.")
                return self.game.go_to_main_menu()

            logger.info("Free Hero Chest is available.")
            self.emulator.click_button(ui.STORE_CHARACTER_FREE_HERO_CHEST_BUTTON)
            if wait_until(self.emulator.is_ui_element_on_screen,
                          ui_element=ui.STORE_CHARACTER_FREE_HERO_CHEST_BUTTON_ACQUIRE):
                self.emulator.click_button(ui.STORE_CHARACTER_FREE_HERO_CHEST_BUTTON_ACQUIRE)
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE):
                    self.emulator.click_button(ui.STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE)
                    if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SKIP_CUTSCENE):
                        self.emulator.click_button(ui.SKIP_CUTSCENE)
                        if wait_until(self.emulator.is_ui_element_on_screen,
                                      ui_element=ui.STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE_CLOSE):
                            self.emulator.click_button(ui.STORE_CHARACTER_FREE_HERO_CHEST_PURCHASE_CLOSE)
                            r_sleep(1)  # Wait for animation
                            logger.info("Free Hero Chest acquired.")
                            self.emulator.click_button(ui.MENU_BACK)
                            r_sleep(1)  # Wait for animation
        self.game.go_to_main_menu()


class ArtifactStore(Store):
    """Class for working with Artifact Store."""

    def open_artifact_store(self):
        """Opens Artifact store using Dimension Chest button in Main Menu."""
        self.game.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_DIMENSION_CHEST):
                self.emulator.click_button(ui.MAIN_MENU_DIMENSION_CHEST)
                self.close_ads()
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.STORE_OPEN_ARTIFACT_FROM_DIMENSION_CHEST):
                    logger.debug("Opening Artifact tab.")
                    self.emulator.click_button(ui.STORE_OPEN_ARTIFACT_FROM_DIMENSION_CHEST)
                    return True
        return False

    def acquire_free_artifact_chest(self):
        """Acquires available Free Artifact Chest."""
        self.open_artifact_store()
        self.emulator.click_button(ui.STORE_ARTIFACT_FREE_CHEST)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORE_ARTIFACT_FREE_CHEST_BUTTON_ACQUIRE):
            logger.debug("Acquiring Free Artifact Chest.")
            self.emulator.click_button(ui.STORE_ARTIFACT_FREE_CHEST_BUTTON_ACQUIRE)
            if wait_until(self.emulator.is_ui_element_on_screen,
                          ui_element=ui.STORE_ARTIFACT_FREE_CHEST_PURCHASE):
                self.emulator.click_button(ui.STORE_ARTIFACT_FREE_CHEST_PURCHASE)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SKIP_CUTSCENE):
                    self.emulator.click_button(ui.SKIP_CUTSCENE)
                    if wait_until(self.emulator.is_ui_element_on_screen,
                                  ui_element=ui.STORE_ARTIFACT_FREE_CHEST_PURCHASE_CLOSE):
                        self.emulator.click_button(ui.STORE_ARTIFACT_FREE_CHEST_PURCHASE_CLOSE)
                        r_sleep(1)  # Wait for animation
                        logger.info("Free Artifact Chest acquired.")
                        self.emulator.click_button(ui.MENU_BACK)
                        r_sleep(1)  # Wait for animation
        else:
            logger.info("No available Free Artifact Chest, exiting.")
            self.emulator.click_button(ui.MENU_BACK)
            r_sleep(1)  # Wait for animation
        self.game.go_to_main_menu()
