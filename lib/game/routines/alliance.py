import lib.logger as logging
from lib.game.notifications import Notifications
from lib.functions import wait_until

logger = logging.get_logger(__name__)


class Alliance(Notifications):
    """Class for working with Alliance."""

    def check_in(self):
        """Click Check-In button in Alliance."""
        self.game.go_to_alliance()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_CHECK_IN']):
            self.emulator.click_button(self.ui['ALLIANCE_CHECK_IN'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_CHECK_IN_CLOSE']):
                self.emulator.click_button(self.ui['ALLIANCE_CHECK_IN_CLOSE'].button)
        self.game.go_to_main_menu()

    def donate_resources(self, donate_gold=True, donate_memento=True):
        """Donate resources to Alliance

        :param donate_gold: True or False.
        :param donate_memento: True or False.
        """
        if not donate_gold and not donate_memento:
            logger.info("Nothing to donate.")
        self.game.go_to_alliance()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_DONATE']):
            self.emulator.click_button(self.ui['ALLIANCE_DONATE'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_DONATION_MENU']):
                if donate_gold:
                    logger.debug("Maxing GOLD for donation.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_MAX_GOLD'].button)
                if donate_memento:
                    logger.debug("Maxing ALLIANCE MEMENTO for donation.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_MAX_MEMENTO'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['ALLIANCE_DONATION_CONFIRM']):
                    logger.info("Donating resources for Alliance.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_CONFIRM'].button)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['ALLIANCE_DONATION_REWARD_CLOSE']):
                        logger.info("Resources were donated, exiting.")
                        self.emulator.click_button(self.ui['ALLIANCE_DONATION_REWARD_CLOSE'].button)
                else:
                    logger.info("Can't donate resource for Alliance. Probably already donated, exiting.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_CANCEL'].button)
        self.game.go_to_main_menu()
