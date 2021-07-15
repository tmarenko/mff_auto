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
