import lib.logger as logging
from lib.functions import wait_until, r_sleep
from lib.game import ui
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)


class Inbox(Notifications):
    """Class for working with Inbox."""

    def acquire_all_chests(self):
        """Acquires all chests from Inbox."""
        self.game.go_to_inbox()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_CHEST_TAB):
            r_sleep(2)  # Wait for animation
            self.emulator.click_button(ui.INBOX_CHEST_TAB)
            self._acquire_chests()
        self.game.go_to_main_menu()

    def acquire_all_gifts(self, acquire_energy=False):
        """Acquires all gifts from Inbox.

        :param bool acquire_energy: acquire energy or not.
        """
        self.game.go_to_inbox()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_GIFT_TAB):
            r_sleep(2)  # Wait for animations
            self.emulator.click_button(ui.INBOX_GIFT_TAB)
            self._acquire_gifts(acquire_energy=acquire_energy)
        self.game.go_to_main_menu()

    def _acquire_chests(self):
        """Acquires chests."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.INBOX_ACQUIRE_ALL_BUTTON):
            logger.debug("Found Acquire All button.")
            self.emulator.click_button(ui.INBOX_ACQUIRE_ALL_BUTTON)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_CHEST_ACQUIRE_ALL_NOTICE):
                logger.info("Acquiring all chests.")
                self.emulator.click_button(ui.INBOX_CHEST_ACQUIRE_ALL_NOTICE)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=120,
                              ui_element=ui.INBOX_CHEST_ACQUIRE_CLOSE_RESULTS):
                    logger.info("Chests acquired, exiting.")
                    self.emulator.click_button(ui.INBOX_CHEST_ACQUIRE_CLOSE_RESULTS)
                    return True
        elif self.emulator.is_ui_element_on_screen(ui_element=ui.INBOX_ACQUIRE_BUTTON):
            logger.debug("Found only one Acquire button.")
            self.emulator.click_button(ui.INBOX_ACQUIRE_BUTTON)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_CHEST_ACQUIRE_CLOSE_ONE_RESULT):
                logger.info("Chest acquired, exiting.")
                r_sleep(1)  # Wait for animation
                self.emulator.click_button(ui.INBOX_CHEST_ACQUIRE_CLOSE_ONE_RESULT)
                return True

    def _acquire_gifts(self, acquire_energy):
        """Acquires gifts.

        :param bool acquire_energy: acquire energy or not.
        """
        if self.emulator.is_ui_element_on_screen(ui_element=ui.INBOX_ACQUIRE_ALL_BUTTON):
            logger.debug("Found Acquire All button.")
            self.emulator.click_button(ui.INBOX_ACQUIRE_ALL_BUTTON)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_GIFT_ACQUIRE_ALL_NOTICE):
                self._check_and_set_acquire_energy_toggle(acquire_energy=acquire_energy)
                logger.info("Acquiring all gifts.")
                self.emulator.click_button(ui.INBOX_GIFT_ACQUIRE_ALL_NOTICE)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_GIFT_ACQUIRE_CLOSE_RESULTS):
                    logger.info("Gifts acquired, exiting.")
                    self.emulator.click_button(ui.INBOX_GIFT_ACQUIRE_CLOSE_RESULTS)
                    return True
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_GIFT_ACQUIRE_NOTICE_NO_ITEMS):
                    logger.info("No gifts was acquired, exiting.")
                    self.emulator.click_button(ui.INBOX_GIFT_ACQUIRE_NOTICE_NO_ITEMS)
                    return True
        elif self.emulator.is_ui_element_on_screen(ui_element=ui.INBOX_ACQUIRE_BUTTON):
            pass
            # TODO: selectors has their own menu
            # logger.debug("Found only one Acquire button.")
            # self.emulator.click_button(self.ui['INBOX_ACQUIRE_BUTTON'].button)
            # if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
            #               ui_element=self.ui['INBOX_GIFT_ACQUIRE_CLOSE_ONE_RESULT']):
            #     logger.info("Gift acquired, exiting.")
            #     r_sleep(1)  # Wait for animation
            #     self.emulator.click_button(self.ui['INBOX_GIFT_ACQUIRE_CLOSE_ONE_RESULT'].button)
            #     return True

    def _check_and_set_acquire_energy_toggle(self, acquire_energy):
        """Checks and sets energy toggle before acquiring items.

        :param bool acquire_energy: acquire energy or not.
        """
        energy_included = self.emulator.is_image_on_screen(ui.INBOX_GIFT_ACQUIRE_ALL_TOGGLE)
        if acquire_energy and not energy_included:
            logger.debug("Acquire energy toggle is inactive. Enabling it.")
            self.emulator.click_button(ui.INBOX_GIFT_ACQUIRE_ALL_TOGGLE)
        if not acquire_energy and energy_included:
            logger.debug("Acquire energy toggle is active. Disabling it.")
            self.emulator.click_button(ui.INBOX_GIFT_ACQUIRE_ALL_TOGGLE)
