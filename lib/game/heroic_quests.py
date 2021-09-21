import logging
from lib.game import ui
from lib.functions import wait_until

logger = logging.getLogger(__name__)


class HeroicQuests:
    """Class for working with Heroic Quests."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        self.emulator = game.emulator
        self.game = game

    def close_chest_notification(self):
        """Closes 'Buy Crystal Chest' notification."""
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL):
            self.emulator.click_button(ui.HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL_OK):
                self.emulator.click_button(ui.HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL_OK)
                return True
        return False

    def acquire_reward(self):
        """Acquires quest reward."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.HQ_ACQUIRE_REWARD):
            logger.debug("Acquiring Heroic Quest reward.")
            self.emulator.click_button(ui.HQ_ACQUIRE_REWARD, min_duration=0.5, max_duration=0.7)
            self.emulator.click_button(ui.HQ_ACQUIRE_REWARD)
            return True
        return False

    def acquire_reward_and_return_back(self):
        """Acquires quest reward and return back."""
        if self.close_chest_notification():
            logger.info("Crystal chest is available in Heroic Quest. Skipping reward.")
            return True
        if self.acquire_reward():
            logger.info("Heroic Quest reward acquired. Going back.")
            self.emulator.click_button(ui.MENU_BACK)
            return True
        logger.error("Something went wrong while acquiring Heroic Quest reward. Going to main menu.")
        self.game.go_to_main_menu()
        return False
