from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions
from lib.game import ui
from lib.functions import wait_until, r_sleep
import lib.logger as logging

logger = logging.get_logger(__name__)


class TimelineBattle(Missions):
    """Class for working with TimeLine Battle missions."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='TIMELINE BATTLE')

    @property
    def battle_over_conditions(self):
        def points():
            return self.emulator.is_ui_element_on_screen(ui.TIMELINE_POINTS)

        return [points]

    def select_team(self):
        """Select team for missions."""
        team_element = ui.get_by_name(f'TL_SELECT_TEAM_{self.game.timeline_team}')
        logger.debug(f"Selecting team: {team_element.name}")
        self.emulator.click_button(team_element)

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
        logger.info(f"{self.stages} stages available")
        if self.stages > 0:
            if not self.open_timeline_battle():
                return
            while self.stages > 0:
                self._search_for_new_opponent(skip_opponent_count=skip_opponent_count)
                self._start_fight()
        logger.info("No more stages.")

    def open_timeline_battle(self):
        """Open TimeLine battle mission lobby and select battle."""
        self.game.select_mode(self.mode_name)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_NEW_SEASON_NOTIFICATION):
            logger.debug("Timeline Battle: found new season notification, closing.")
            self.emulator.click_button(ui.TL_NEW_SEASON_NOTIFICATION)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_LEAGUE_NOTIFICATION):
            logger.debug("Timeline Battle: found league notification, closing.")
            self.emulator.click_button(ui.TL_LEAGUE_NOTIFICATION)
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_GET_READY_BUTTON):
            logger.error("Timeline Battle: can't find GET READY button.")
            return False
        self.emulator.click_button(ui.TL_GET_READY_BUTTON)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_RESTRICTED_NOTIFICATION):
            logger.debug("Timeline Battle: found restricted character notification, closing.")
            self.emulator.click_button(ui.TL_RESTRICTED_NOTIFICATION)
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_SEARCH_BUTTON):
            logger.error("Timeline Battle: can't find SEARCH button.")
            return False
        if wait_until(self.emulator.is_image_on_screen, timeout=1, ui_element=ui.TL_REPEAT_TOGGLE):
            logger.debug("Found REPEAT toggle active. Clicking it.")
            self.emulator.click_button(ui.TL_REPEAT_TOGGLE)
        self.select_team()
        self.emulator.click_button(ui.TL_SEARCH_BUTTON)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_HONOR_TOKENS_LIMIT):
            # TODO: seems no longer shows up after 7.0.0 update
            logger.debug("Your Honor Tokens is more than 60000. Can't acquire more but still playing battle.")
            self.emulator.click_button(ui.TL_HONOR_TOKENS_LIMIT)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVENTORY_FULL):
            logger.warning("Your inventory is full, cannot start battle.")
            self.emulator.click_button(ui.INVENTORY_FULL)
            self.stages *= 0
            return False
        return True

    def _search_for_new_opponent(self, skip_opponent_count):
        """Search new opponents to minimize lose points.

        :param skip_opponent_count: how many opponents to skip before each battle.
        """
        if skip_opponent_count <= 0:
            return
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_SEARCH_NEW_OPPONENT):
            logger.debug(f"Skipping {skip_opponent_count} opponents.")
            for _ in range(skip_opponent_count):
                self.emulator.click_button(ui.TL_SEARCH_NEW_OPPONENT)
                r_sleep(1)

    def _start_fight(self):
        """Go to fight screen and fight."""
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.TL_FIGHT_BUTTON):
            logger.error("Can't find FIGHT button.")
        logger.debug("Starting the fight.")
        self.emulator.click_button(ui.TL_FIGHT_BUTTON)
        AutoBattleBot(self.game, self.battle_over_conditions).fight()
        r_sleep(1)  # Wait for button's animation
        self.stages -= 1
        if self.stages > 0:
            self.press_repeat_button(repeat_button_ui=ui.TL_REPEAT_BUTTON, start_button_ui=ui.TL_FIGHT_BUTTON)
        else:
            self.press_home_button(home_button=ui.TL_HOME_BUTTON)
