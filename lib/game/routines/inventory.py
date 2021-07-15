import lib.logger as logging
from lib.game.notifications import Notifications
from lib.functions import wait_until

logger = logging.get_logger(__name__)


class ComicCards(Notifications):
    """Class for working with Comic Cards."""

    def upgrade_all_cards(self):
        """Upgrade all available Comic Cards."""
        self.game.go_to_comic_cards()
        logger.info("Comic Cards: upgrading all available cards.")
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['CARDS_UPGRADE_ALL']):
            self.emulator.click_button(self.ui['CARDS_UPGRADE_ALL'].button)
            for card_index in range(1, 6):
                card_select_ui = self.ui[f'CARDS_SELECT_GRADE_{card_index}']
                self.emulator.click_button(card_select_ui.button)
                logger.debug(f"Comic Cards: starting to upgrade UI Element {card_select_ui.name}")
                if not wait_until(self.emulator.is_image_on_screen, timeout=3, ui_element=card_select_ui):
                    logger.warning("Comic Cards: can't select card's grade.")
                    continue
                logger.debug(f"Comic Cards: successfully selected UI Element {card_select_ui.name}")
                self.emulator.click_button(self.ui['CARDS_SELECT_GRADE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['CARDS_UPGRADE_CONFIRM']):
                    self.emulator.click_button(self.ui['CARDS_UPGRADE_CONFIRM'].button)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=10,
                                  ui_element=self.ui['CARDS_UPGRADE_RESULTS_OK']):
                        logger.debug(f"Comic Cards: successfully upgraded UI Element {card_select_ui.name}")
                        self.emulator.click_button(self.ui['CARDS_UPGRADE_RESULTS_OK'].button)
                        wait_until(self.emulator.is_image_on_screen, timeout=3, ui_element=card_select_ui)
                        continue
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['CARDS_UPGRADE_ALL_CANCEL']):
            self.emulator.click_button(self.ui['CARDS_UPGRADE_ALL_CANCEL'].button)
            self.close_after_mission_notifications()
            self.game.go_to_main_menu()


class CustomGear(Notifications):
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
        self.emulator.click_button(self.ui['INVENTORY_CUSTOM_GEAR_TAB'].button)
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
                self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['CUSTOM_GEAR_QUICK_UPGRADE_CONFIRM']):
                    logger.debug("Custom Gear: confirming upgrading.")
                    self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_CONFIRM'].button)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['CUSTOM_GEAR_QUICK_UPGRADE_INCLUDE_UPGRADED']):
                        logger.debug("Custom Gear: confirming to use upgraded gear.")
                        self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_INCLUDE_UPGRADED'].button)
                    self.close_upgrade_result()
                else:
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['CUSTOM_GEAR_NO_MATERIALS']):
                        logger.error("Custom Gear: you have no materials for gear upgrade.")
                        self.emulator.click_button(self.ui['CUSTOM_GEAR_NO_MATERIALS'].button)
                        break

        # `self.is_quick_toggle is False` not working o_O
        if self.is_quick_toggle is not None and not self.is_quick_toggle:
            logger.debug("Custom Gear: returning Quick Upgrade toggle to inactive.")
            self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'].button)
        self.game.go_to_main_menu()

    def is_custom_gear_tab(self):
        """Check if Custom Gear tab is opened."""
        return self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE']) or \
               self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_ENHANCE']) or \
               self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_CHANGE_OPTION'])

    def toggle_quick_upgrade(self):
        """Toggle Quick Upgrade toggle."""
        self.is_quick_toggle = self.emulator.is_image_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'])
        if not self.is_quick_toggle:
            logger.debug("Custom Gear: found Quick Upgrade toggle inactive. Clicking it.")
            self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'].button)
            wait_until(self.emulator.is_image_on_screen, timeout=3,
                       ui_element=self.ui['CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE'])
        return self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE'])

    def close_upgrade_result(self):
        """Close upgrade's result notification."""

        def is_results_window():
            return self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1']) or \
                   self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2'])

        if wait_until(is_results_window, timeout=10):
            if self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1']):
                self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1'].button)
            if self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2']):
                self.emulator.click_button(self.ui['CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2'].button)
            self.close_after_mission_notifications()
        if is_results_window() or not self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_SELL_ALL']):
            return self.close_upgrade_result()
        logger.debug("Custom Gear: successfully upgraded custom gear.")

    def try_to_select_gear_for_upgrade(self):
        """Try to select gear for upgrade from inventory."""
        if self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_CHANGE_OPTION']):
            self.emulator.click_button(self.ui['CUSTOM_GEAR_1'].button)
        return not self.emulator.is_ui_element_on_screen(self.ui['CUSTOM_GEAR_CHANGE_OPTION'])
