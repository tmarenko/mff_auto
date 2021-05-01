import lib.logger as logging
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class DispatchMission:
    """Class for working with Dispatch Mission."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.player = game.player
        self.ui = game.ui
        self.game = game

    def acquire_all_rewards(self):
        """Acquire all available rewards in Dispatch Mission."""
        if not self.game.go_to_dispatch_mission():
            logger.error("Dispatch Mission: can't get into mission lobby.")
            return
        if self.player.is_ui_element_on_screen(ui_element=self.ui['DISPATCH_SECTOR_BUTTON']):
            logger.debug("Dispatch Mission: closing DISPATCH sector menu")
            self.player.click_button(self.ui['DISPATCH_SECTOR_CLOSE'].button)
        if self._acquire_sectors_from_the_left():
            self._acquire_sectors_from_the_right()
        self.game.go_to_main_menu()

    def _drag_to_the_left(self):
        """Drag Dispatch sector menu to the left side."""
        logger.debug("Dispatch Mission: dragging to the left side.")
        self.player.drag(self.ui['DISPATCH_DRAG_LEFT_POSITION'].button, self.ui['DISPATCH_DRAG_RIGHT_POSITION'].button)
        r_sleep(1)
        self.player.drag(self.ui['DISPATCH_DRAG_LEFT_POSITION'].button, self.ui['DISPATCH_DRAG_RIGHT_POSITION'].button)
        r_sleep(1)

    def _drag_to_the_right(self):
        """Drag Dispatch sector menu to the right side."""
        logger.debug("Dispatch Mission: dragging to the right side.")
        self.player.drag(self.ui['DISPATCH_DRAG_RIGHT_POSITION'].button, self.ui['DISPATCH_DRAG_LEFT_POSITION'].button)
        r_sleep(1)
        self.player.drag(self.ui['DISPATCH_DRAG_RIGHT_POSITION'].button, self.ui['DISPATCH_DRAG_LEFT_POSITION'].button)
        r_sleep(1)

    def _acquire_sectors_from_the_left(self):
        """Acquire all available rewards in sectors from the left side.

        :return: True or False: were all dispatch missions closed on the left side.
        """
        self._drag_to_the_left()
        dispatch_closed = []
        for sector_index in range(1, 7):
            sector_ui = self.ui[f'DISPATCH_ACQUIRE_SECTOR_{sector_index}']
            if self.player.is_ui_element_on_screen(ui_element=sector_ui):
                self.player.click_button(sector_ui.button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['DISPATCH_ACQUIRE_OK_BUTTON']):
                    logger.debug(f"Dispatch Mission: acquired rewards for sector #{sector_index}")
                    self.player.click_button(self.ui['DISPATCH_ACQUIRE_OK_BUTTON'].button)
                    dispatch_closed.append(True)
        return len(dispatch_closed) == 6

    def _acquire_sectors_from_the_right(self):
        """Acquire all available rewards in sectors from the right side."""
        self._drag_to_the_right()
        for sector_index in range(6, 11):
            sector_ui = self.ui[f'DISPATCH_ACQUIRE_SECTOR_{sector_index}']
            if self.player.is_ui_element_on_screen(ui_element=sector_ui):
                self.player.click_button(sector_ui.button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['DISPATCH_ACQUIRE_OK_BUTTON']):
                    logger.debug(f"Dispatch Mission: acquired rewards for sector #{sector_index}")
                    self.player.click_button(self.ui['DISPATCH_ACQUIRE_OK_BUTTON'].button)
