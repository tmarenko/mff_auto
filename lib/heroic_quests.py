import logging
from lib.functions import wait_until
logger = logging.getLogger(__name__)


class HeroicQuests:
    """Class for working with Heroic Quests."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.player = game.player
        self.ui = game.ui
        self.game = game

    def close_chest_notification(self):
        """Close 'Buy Crystal Chest' notification."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL']):
            self.player.click_button(self.ui['HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL_OK']):
                self.player.click_button(self.ui['HQ_CRYSTAL_CHEST_NOTIFICATION_CANCEL_OK'].button)
                return True
        return False

    def acquire_reward(self):
        """Acquire quest reward."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['HQ_ACQUIRE_REWARD']):
            logger.debug("Acquiring Heroic Quest reward.")
            self.player.click_button(self.ui['HQ_ACQUIRE_REWARD'].button, min_duration=0.5, max_duration=0.7)
            self.player.click_button(self.ui['HQ_ACQUIRE_REWARD'].button)
            return True
        return False

    def acquire_reward_and_return_back(self):
        """Acquire quest reward and return back."""
        if self.close_chest_notification():
            logger.info("Crystal chest is available in Heroic Quest. Skipping reward.")
            return True
        if self.acquire_reward():
            logger.info("Heroic Quest reward acquired. Going back.")
            self.player.click_button(self.ui['MENU_BACK'].button)
            return True
        logger.warning("Something went wrong while acquiring Heroic Quest reward. Going to main menu.")
        self.game.go_to_main_menu()
        return False
