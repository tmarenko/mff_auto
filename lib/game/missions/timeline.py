from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, r_sleep
import lib.logger as logging

logger = logging.get_logger(__name__)


class TimelineBattle(Missions):
    """Class for working with TimeLine Battles."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'TL_LABEL')

    @property
    def battle_over_conditions(self):
        def points():
            return self.player.is_ui_element_on_screen(self.ui['TIMELINE_POINTS'])

        return [points]

    def select_team(self):
        """Select team for missions."""
        team_element = self.ui[f'TL_SELECT_TEAM_{self.game.timeline_team}']
        logger.debug(f"Selecting team: {team_element.name}")
        self.player.click_button(team_element.button)

    def do_missions(self, times=None, skip_opponent_count=0):
        """Do missions."""
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(skip_opponent_count=skip_opponent_count)
            self.end_missions()

    def start_missions(self, skip_opponent_count=0):
        """Start TimeLine Battles.

        :param skip_opponent_count: how many opponents to skip before each battle.
        """
        logger.info(f"Timeline Battle: {self.stages} stages available")
        if self.stages > 0:
            if not self.go_to_timeline_battle():
                return
            while self.stages > 0:
                self.search_new_opponent(skip_opponent_count=skip_opponent_count)
                self.fight()
        logger.info("No more stages for timeline battles.")

    def go_to_timeline_battle(self):
        """Go to TimeLine battle screen and select battle."""
        self.game.select_mode(self.mode_name)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_NEW_SEASON_NOTIFICATION']):
            logger.debug("Timeline Battle: found new season notification, closing.")
            self.player.click_button(self.ui['TL_NEW_SEASON_NOTIFICATION'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_LEAGUE_NOTIFICATION']):
            logger.debug("Timeline Battle: found league notification, closing.")
            self.player.click_button(self.ui['TL_LEAGUE_NOTIFICATION'].button)
        if not wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_GET_READY_BUTTON']):
            logger.error("Timeline Battle: can't find GET READY button.")
            return False
        self.player.click_button(self.ui['TL_GET_READY_BUTTON'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_RESTRICTED_NOTIFICATION']):
            logger.debug("Timeline Battle: found restricted character notification, closing.")
            self.player.click_button(self.ui['TL_RESTRICTED_NOTIFICATION'].button)
        if not wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_SEARCH_BUTTON']):
            logger.error("Timeline Battle: can't find SEARCH button.")
            return False
        if wait_until(self.player.is_image_on_screen, timeout=1, ui_element=self.ui['TL_REPEAT_TOGGLE']):
            logger.debug("Found REPEAT toggle active. Clicking it.")
            self.player.click_button(self.ui['TL_REPEAT_TOGGLE'].button)
        self.select_team()
        self.player.click_button(self.ui['TL_SEARCH_BUTTON'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_HONOR_TOKENS_LIMIT']):
            logger.debug("Your Honor Tokens is more than 60000. Can't acquire more but still playing battle.")
            self.player.click_button(self.ui['TL_HONOR_TOKENS_LIMIT'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['INVENTORY_FULL']):
            logger.warning("Your inventory is full, cannot start battle.")
            self.player.click_button(self.ui['INVENTORY_FULL'].button)
            self.stages *= 0
            return False
        return True

    def search_new_opponent(self, skip_opponent_count):
        """Search new opponents to minimize lose points.

        :param skip_opponent_count: how many opponents to skip before each battle.
        """
        if skip_opponent_count <= 0:
            return
        logger.debug(f"Timeline Battle: skipping {skip_opponent_count} opponents.")
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_SEARCH_NEW_OPPONENT']):
            for _ in range(skip_opponent_count):
                self.player.click_button(self.ui['TL_SEARCH_NEW_OPPONENT'].button)
                r_sleep(1)

    def fight(self):
        """Go to fight screen and fight."""
        if not wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['TL_FIGHT_BUTTON']):
            logger.error("Timeline Battle: can't find FIGHT button.")
        logger.debug("Timeline Battle: starting the fight.")
        self.player.click_button(self.ui['TL_FIGHT_BUTTON'].button)
        AutoBattleBot(self.game, self.battle_over_conditions).fight()
        r_sleep(1)  # Wait for button's animation
        self.stages -= 1
        if self.stages > 0:
            self.press_repeat_button(repeat_button_ui='TL_REPEAT_BUTTON', start_button_ui='TL_FIGHT_BUTTON')
        else:
            self.press_home_button(home_button='TL_HOME_BUTTON')
