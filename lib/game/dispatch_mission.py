import lib.logger as logging
from lib.functions import r_sleep
from lib.game import ui

logger = logging.get_logger(__name__)


class DispatchMission:
    """Class for working with Dispatch Mission."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        self.emulator = game.emulator
        self.game = game

    def acquire_all_rewards(self):
        """Acquires all available rewards in Dispatch Mission."""
        if not self.game.go_to_dispatch_mission():
            return logger.error("Can't get into mission lobby.")
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DISPATCH_SECTOR_BUTTON):
            logger.debug("Closing DISPATCH sector menu")
            self.emulator.click_button(ui.DISPATCH_SECTOR_CLOSE)
        self._acquire_rewards_from_sectors()
        self.game.go_to_main_menu()

    def _drag_to_the_left(self):
        """Drags Dispatch sector menu to the left side."""
        logger.debug("Dragging to the left side.")
        self.emulator.drag(ui.DISPATCH_DRAG_LEFT_POSITION, ui.DISPATCH_DRAG_RIGHT_POSITION)
        r_sleep(1)
        self.emulator.drag(ui.DISPATCH_DRAG_LEFT_POSITION, ui.DISPATCH_DRAG_RIGHT_POSITION)
        r_sleep(1)

    def _acquire_rewards_from_sectors(self):
        """Acquired rewards from Dispatch Mission's sectors starting from the left one."""
        self._drag_to_the_left()
        if self.emulator.is_ui_element_on_screen(ui_element=ui.DISPATCH_ACQUIRE_SECTOR_1):
            self.emulator.click_button(ui.DISPATCH_ACQUIRE_SECTOR_1)
            logger.debug("Started acquiring rewards from sectors.")
            while not self.emulator.is_ui_element_on_screen(ui_element=ui.DISPATCH_ACQUIRE_OK_BUTTON):
                if self.emulator.is_ui_element_on_screen(ui_element=ui.DISPATCH_NEXT_REWARD):
                    logger.debug("Next reward is available, acquiring.")
                    self.emulator.click_button(ui.DISPATCH_NEXT_REWARD)
                r_sleep(0.3)  # In order to not be fast as Sonic
            logger.debug("Acquired all available rewards.")
            self.emulator.click_button(ui.DISPATCH_ACQUIRE_OK_BUTTON)
