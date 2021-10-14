import lib.logger as logging
from lib.functions import wait_until
from lib.game import ui
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class Story(Missions):
    """Class for working with Story missions."""

    class STORY_MISSION:
        DIMENSIONAL_CLASH_NORMAL = ui.STORY_MISSION_DIMENSIONAL_CLASH_NORMAL
        DIMENSIONAL_CLASH_ULTIMATE = ui.STORY_MISSION_DIMENSIONAL_CLASH_ULTIMATE

    class STORY_STAGE:
        DIMENSIONAL_CLASH_1_1 = ui.STORY_MISSION_DIMENSIONAL_CLASH_1_1

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game, mode_name='STORY')

    @property
    def battle_over_conditions(self):
        def rewards():
            return self.emulator.is_ui_element_on_screen(ui.STORY_BATTLE_REWARDS)

        def home_button():
            if self.emulator.is_image_on_screen(ui.HOME_BUTTON) or \
                    self.emulator.is_image_on_screen(ui.HOME_BUTTON_POSITION_2) or \
                    self.emulator.is_image_on_screen(ui.HOME_BUTTON_POSITION_3):
                return True

        return [rewards, home_button]

    def open_story_missions(self):
        """Opens Story missions from Mission selector.

        :return: was mission lobby opened.
        :rtype: bool
        """
        if not self.game.go_to_mission_selection():
            return logger.error("Can't go into Mission selection.")
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORY_MISSION):
            self.emulator.click_button(ui.STORY_MISSION)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORY_LABEL)

    def _open_story_mission(self, story_mission):
        """Opens given Story mission from Story lobby.

        :param ui.UIElement story_mission: UI element that represent Story Mission.

        :rtype: bool
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=story_mission):
            logger.debug(f"Opening Story mission {story_mission}")
            self.emulator.click_button(story_mission)
            # TODO: normal start button
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.STORY_ULTIMATE_START_BUTTON)
        logger.error(f"Can't open Store mission {story_mission}")

    def _select_story_stage(self, story_stage):
        """Selects stage of Story mission.

        :param ui.UIElement story_stage: UI element that represent mission stage.
        """
        while not self.emulator.is_ui_element_on_screen(story_stage):
            # TODO: plus sign for next missions
            self.emulator.click_button(ui.STORY_STAGE_MINUS)

    def select_team(self):
        """Selects team for missions."""
        team_element = ui.get_by_name(f'STORY_SELECT_TEAM_{self.game.mission_team}')
        logger.debug(f"Selecting Story team: {team_element.name}")
        self.emulator.click_button(team_element)

    def do_missions(self, times=None, story_mission=None, story_stage=None):
        """Does missions.

        :param int times: how many stages to complete.
        :param ui.UIElement story_mission: UI element that represent Story Mission.
        :param ui.UIElement story_stage: UI element that represent mission stage.
        """
        self.start_missions(times=times, story_mission=story_mission, story_stage=story_stage)
        self.end_missions()

    def start_missions(self, times=0, story_mission=None, story_stage=None):
        """Starts Story mission."""
        if self.open_story_missions() and self._open_story_mission(story_mission=story_mission):
            logger.info(f"Starting Story {times} times.")
            while times > 0:
                self._select_story_stage(story_stage=story_stage)
                if not self.press_start_button():
                    return
                ManualBattleBot(self.game, self.battle_over_conditions).fight(move_around=True)
                times -= 1
                if times > 0:
                    self.press_repeat_button(repeat_button_ui=ui.STORY_REPEAT_BUTTON,
                                             start_button_ui=ui.STORY_ULTIMATE_START_BUTTON)
                else:
                    self.press_home_button(home_button=ui.STORY_HOME_BUTTON)
        logger.info("No more stages.")

    def press_start_button(self, start_button_ui=ui.STORY_ULTIMATE_START_BUTTON):
        """Presses start button of the mission."""
        if self.emulator.is_ui_element_on_screen(start_button_ui):
            self.select_team()
            self.emulator.click_button(start_button_ui)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2, ui_element=ui.NOT_ENOUGH_ENERGY):
                self.emulator.click_button(ui.NOT_ENOUGH_ENERGY)
                logger.warning(f"Not enough energy for starting mission, current energy: {self.game.energy}")
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2, ui_element=ui.INVENTORY_FULL):
                self.emulator.click_button(ui.INVENTORY_FULL)
                logger.warning("Your inventory is full, cannot start mission.")
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                          ui_element=ui.STORY_UNUSABLE_CHARACTER_NOTICE):
                self.emulator.click_button(ui.STORY_UNUSABLE_CHARACTER_NOTICE)
                logger.warning("Your team has unusable characters (not 70lvl/T3/Ascended), cannot start mission.")
                return False
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2, ui_element=ui.STORY_DAILY_REWARD_NOTICE):
                self.emulator.click_button(ui.STORY_DAILY_REWARD_NOTICE)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=2,
                          ui_element=ui.ITEM_MAX_LIMIT_NOTIFICATION):
                self.emulator.click_button(ui.ITEM_MAX_LIMIT_NOTIFICATION)
            return True
        logger.error(f"Unable to press {start_button_ui} button.")
        return False
