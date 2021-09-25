import lib.logger as logging
from lib.functions import wait_until
from lib.game import ui
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)


class Friends(Notifications):
    """Class for working with Friends."""

    def send_all(self):
        """Sends all tokens to friends."""
        self.game.go_to_friends()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.FRIENDS_TOKEN_SEND_ALL):
            self.emulator.click_button(ui.FRIENDS_TOKEN_SEND_ALL)
            notification_closed = wait_until(self.game.close_complete_challenge_notification)
            logger.debug(f"Complete challenge notifications was closed: {notification_closed}")
        self.game.go_to_main_menu()

    def acquire_all(self):
        """Acquires all tokens from friends."""
        self.game.go_to_friends()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.FRIENDS_TOKEN_ACQUIRE_ALL):
            self.emulator.click_button(ui.FRIENDS_TOKEN_ACQUIRE_ALL)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.FRIENDS_TOKEN_ACQUIRE_ALL_CLOSE):
                self.emulator.click_button(ui.FRIENDS_TOKEN_ACQUIRE_ALL_CLOSE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.FRIENDS_ACQUIRE_NOTICE):
                logger.debug("Friends: can't acquire more tokens, exiting.")
                self.emulator.click_button(ui.FRIENDS_ACQUIRE_NOTICE)
        self.game.go_to_main_menu()
