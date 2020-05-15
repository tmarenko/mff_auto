from lib.battle_bot import AutoBattleBot
from lib.missions import Missions
from lib.functions import wait_until
import logging
import time

logger = logging.getLogger(__name__)


class TimelineBattle(Missions):
    """Class for working with TimeLine Battles."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'TL_LABEL')

    def select_team(self):
        """Select team for missions."""
        team_element = self.ui[f'TL_SELECT_TEAM_{self.game.timeline_team}']
        logger.debug(f"Selecting team: {team_element.name}")
        self.player.click_button(team_element.button)

    def start_missions(self):
        """Start TimeLine Battles."""
        logger.info(f"Timeline Battle: {self.stages} stages available")
        if self.stages > 0:
            self.go_to_timeline_battle()
            while self.stages > 0:
                self.search_new_opponent()
                self.fight()
        logger.info("No more stages for timeline battles.")

    def go_to_timeline_battle(self):
        """Go to TimeLine battle screen and select battle."""
        self.game.select_mode(self.mode_name)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_LEAGUE_NOTIFICATION']):
            self.player.click_button(self.ui['TL_LEAGUE_NOTIFICATION'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_GET_READY_BUTTON']):
            self.player.click_button(self.ui['TL_GET_READY_BUTTON'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['TL_RESTRICTED_NOTIFICATION']):
                self.player.click_button(self.ui['TL_RESTRICTED_NOTIFICATION'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_SEARCH_BUTTON']):
                if wait_until(self.player.is_image_on_screen, timeout=1, ui_element=self.ui['TL_REPEAT_TOGGLE']):
                    logger.debug("Found REPEAT toggle active. Clicking it.")
                    self.player.click_button(self.ui['TL_REPEAT_TOGGLE'].button)
                self.select_team()
                self.player.click_button(self.ui['TL_SEARCH_BUTTON'].button)

    def search_new_opponent(self):
        """Search new opponents to minimize lose points."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_SEARCH_NEW_OPPONENT']):
            for _ in range(3):
                self.player.click_button(self.ui['TL_SEARCH_NEW_OPPONENT'].button)
                time.sleep(1)

    def fight(self):
        """Go to fight screen and fight."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_FIGHT_BUTTON']):
            self.player.click_button(self.ui['TL_FIGHT_BUTTON'].button)
            AutoBattleBot(self.game).fight()
            self.stages -= 1
            if self.stages > 0:
                self.press_repeat_button(repeat_button_ui='TL_REPEAT_BUTTON', start_button_ui='TL_FIGHT_BUTTON')
            else:
                self.press_home_button(home_button='TL_HOME_BUTTON')
