import lib.logger as logging
from lib.game.notifications import Notifications
from lib.functions import wait_until

logger = logging.get_logger(__name__)


class Friends(Notifications):
    """Class for working with Friends."""

    def send_all(self):
        """Send all tokens to friends."""
        self.game.go_to_friends()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['FRIENDS_TOKEN_SEND_ALL']):
            self.emulator.click_button(self.ui['FRIENDS_TOKEN_SEND_ALL'].button)
            notification_closed = wait_until(self.game.close_complete_challenge_notification, timeout=3)
            logger.debug(f"Complete challenge notifications was closed: {notification_closed}")
        self.game.go_to_main_menu()

    def acquire_all(self):
        """Acquire all tokens from friends."""
        self.game.go_to_friends()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['FRIENDS_TOKEN_ACQUIRE_ALL']):
            self.emulator.click_button(self.ui['FRIENDS_TOKEN_ACQUIRE_ALL'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['FRIENDS_TOKEN_ACQUIRE_ALL_CLOSE']):
                self.emulator.click_button(self.ui['FRIENDS_TOKEN_ACQUIRE_ALL_CLOSE'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['FRIENDS_ACQUIRE_NOTICE']):
                logger.debug("Friends: can't acquire more tokens, exiting.")
                self.emulator.click_button(self.ui['FRIENDS_ACQUIRE_NOTICE'].button)
        self.game.go_to_main_menu()
