import lib.logger as logging
from lib.functions import wait_until, r_sleep
from lib.game import ui
from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions

logger = logging.get_logger(__name__)


class EpicQuest(Missions):
    """Class for working with Epic Quest missions."""

    def __init__(self, game, mode_label):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        :param ui.UIElement mode_label: mission's game mode label UI element.
        """
        super().__init__(game, mode_name=mode_label.text)

    def start_stage(self, stage_button, stage_num, farm_shifter_bios=False):
        """Starts Epic Quests stage.

        :param ui.UIElement stage_button: rect of button to start stage.
        :param int stage_num: available stages count.
        :param bool farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.START_BUTTON):
            self.emulator.click_button(stage_button)
            wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.START_BUTTON)
        if not self.press_start_button():
            logger.error(f"Cannot start Epic Quest stage {self.mode_name}, exiting.")
            return 0
        auto_battle_bot = AutoBattleBot(self.game, self.battle_over_conditions)
        ally_appeared = auto_battle_bot.wait_until_shifter_appeared() if farm_shifter_bios else True
        if farm_shifter_bios and not ally_appeared:
            logger.info("No shifter, restarting.")
            if self.game.restart_game(repeat_while=auto_battle_bot.is_battle):
                self.game.select_mode(self.mode_name)
                return stage_num

        auto_battle_bot.fight()
        stage_num -= 1
        logger.debug(f"{stage_num} stages left to complete.")
        self.close_mission_notifications()
        if stage_num > 0:
            self.press_repeat_button()
        else:
            self.press_home_button()
        return stage_num

    def do_missions(self, times=None, farm_shifter_bios=False):
        """Does missions.

        :param int times: how many stages to complete.
        :param bool farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(farm_shifter_bios=farm_shifter_bios)
            self.end_missions()

    def start_missions(self, farm_shifter_bios=False):
        """Starts missions.

        :param bool farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        pass


class OneStageEpicQuest(EpicQuest):
    """Class for working with Epic Quests with one single stage."""

    def __init__(self, game, mode_label_ui):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        :param ui.UIElement mode_label_ui: mission's game mode label UI element.
        """
        super().__init__(game, mode_label_ui)
        self.mode_label_ui = mode_label_ui

    def start_missions(self, farm_shifter_bios=False):
        """Starts single stage missions."""
        logger.info(f"{self.mode_name}: {self.stages} stages available.")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_num = self.stages
            while stage_num > 0:
                stage_num = self.start_stage(self.mode_label_ui, stage_num, farm_shifter_bios=farm_shifter_bios)
        logger.info(f"No more stages for {self.mode_name}.")


class TwoStageEpicQuest(EpicQuest):
    """Class for working with Epic Quests with two separate stages."""

    def __init__(self, game, mode_label_ui, stage_1_ui, stage_2_ui):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        :param ui.UIElement mode_label_ui: mission's game mode label UI element.
        """
        super().__init__(game, mode_label_ui)
        self.mode_label_ui = mode_label_ui
        self.stage_1_ui, self.stage_2_ui = stage_1_ui, stage_2_ui

    def start_missions(self, farm_shifter_bios=False):
        """Starts two stages missions."""
        logger.info(f"{self.mode_name}: {self.stages} stages available.")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.separate_stages
            logger.info(f"{self.mode_name}: available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num + stage_2_num > self.stages:
                logger.debug(f"Stages count {self.stages} is lesser than available stages. Second stage is locked.")
                stage_2_num = 0
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.stage_1_ui, stage_1_num, farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if stage_2_num > 0 and self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.stage_2_ui, stage_2_num, farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info(f"No more stages for {self.mode_name}.")

    @property
    def separate_stages(self):
        """Stages of two stage missions."""
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.mode_label_ui):
            return logger.error(f"Can't find mission label: {self.mode_label_ui.name}.")
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.EQ_RECOMMENDED_LVL):
            stage_1 = self.emulator.get_screen_text(self.stage_1_ui)
            stage_2 = self.emulator.get_screen_text(self.stage_2_ui)
            stage_1_current, _ = self.game.get_current_and_max_values_from_text(stage_1)
            stage_2_current, _ = self.game.get_current_and_max_values_from_text(stage_2)
            return stage_1_current, stage_2_current
        logger.error(f"Can't find {ui.EQ_RECOMMENDED_LVL} in mission lobby.")


class TenStageEpicQuest(EpicQuest):
    """Class for working with Epic Quests with 10 stages (usual missions without difficulty)."""

    def __init__(self, game, mode_selector_ui, mission_selector_ui, mission_selector_label_ui, stage_selector_ui,
                 stage_name=None):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        :param ui.UIElement mode_selector_ui: UI element of Epic Quest selector.
        :param ui.UIElement mission_selector_ui: UI element of Epic Quest's mission selector.
        :param ui.UIElement mission_selector_label_ui: UI element of Epic Quest's mission label.
        :param ui.UIElement stage_selector_ui: UI element of Epic Quest's stage selector.
        :param str stage_name: Epic Quest's stage name.
        """
        super().__init__(game, mode_label=mode_selector_ui)
        self.mode_selector_ui = mode_selector_ui
        self.mission_selector_ui = mission_selector_ui
        self.mission_selector_label_ui = mission_selector_label_ui
        self.stage_selector_ui = stage_selector_ui
        self.mode_name = stage_name if stage_name else self.stage_selector_ui.text

    def _select_epic_quest(self):
        """Selects Epic Quest."""
        if self.game.go_to_epic_quests():
            if self.mode_selector_ui in [ui.EQ_RISE_OF_X_MEN, ui.EQ_SORCERER_SUPREME, ui.EQ_X_FORCE]:
                logger.debug("Epic Quests is referring to the second page. Trying to scroll.")
                self.emulator.drag(ui.EQ_PAGE_DRAG_FROM, ui.EQ_PAGE_DRAG_TO)
                r_sleep(1)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.mode_selector_ui):
                logger.debug(f"Selecting Epic Quest: {self.mode_selector_ui.name}.")
                self.emulator.click_button(self.mode_selector_ui)
                return True

    def _select_mission(self):
        """Selects missions in Epic Quest."""
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.mission_selector_ui):
            logger.debug(f"Selecting Epic Quest's mission: {self.mission_selector_ui.name}")
            self.emulator.click_button(self.mission_selector_ui)
            mission_label_on_screen = wait_until(self.emulator.is_ui_element_on_screen,
                                                 ui_element=self.mission_selector_label_ui)
            # Usually 10 stage epic contains only button selector except Blindsided mission with mission's text
            stage_selector_ui = self.stage_selector_ui if self.stage_selector_ui.text else ui.EQ_RECOMMENDED_LVL
            return mission_label_on_screen and wait_until(self.emulator.is_ui_element_on_screen,
                                                          ui_element=stage_selector_ui)

    def _select_stage(self):
        """Selects stage in missions in Epic Quest."""
        logger.debug(f"Selecting Epic Quest's stage: {self.stage_selector_ui.name}")
        self.emulator.click_button(self.stage_selector_ui)
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.START_BUTTON)

    def start_missions(self, times=10, farm_shifter_bios=False):
        """Starts stage missions."""
        logger.info(f"{self.mode_name}: {times} stages to complete.")
        if times:
            if self._select_epic_quest() and self._select_mission() and self._select_stage():
                while times > 0:
                    times = self.start_stage(self.stage_selector_ui, times, farm_shifter_bios=farm_shifter_bios)
        logger.info(f"No more stages for {self.mode_name}.")

    def do_missions(self, times=10, farm_shifter_bios=False):
        """Does missions.

        :param int times: how many stages to complete.
        :param bool farm_shifter_bios: DISABLED IN THIS MODE.
        """
        farm_shifter_bios = False
        if times > 0:
            self.start_missions(times=times, farm_shifter_bios=farm_shifter_bios)
            self.end_missions()


class TenStageWithDifficultyEpicQuest(TenStageEpicQuest):
    DIFFICULTY = None  # Setup this in child class to Missions._DIFFICULTY_4 or Missions._DIFFICULTY_6

    def _select_stage(self, difficulty=6):
        """Selects stage in missions in Epic Quest."""
        difficulty_ui = ui.get_by_name(self._get_difficulty_ui(difficulty))
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.stage_selector_ui):
            self.emulator.click_button(self.stage_selector_ui)
            if "_2_" in difficulty_ui.name:  # TODO: that's not good at all
                logger.debug("Difficulty is referring from the bottom of list. Trying to scroll.")
                self.emulator.drag(ui.DIFFICULTY_DRAG_FROM, ui.DIFFICULTY_DRAG_TO)
                r_sleep(1)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=difficulty_ui):
                self.emulator.click_button(difficulty_ui)
        return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.START_BUTTON)

    def _select_mission(self):
        """Selects missions in Epic Quest."""
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.mission_selector_ui):
            logger.debug(f"Selecting Epic Quest's mission: {self.mission_selector_ui.name}")
            self.emulator.click_button(self.mission_selector_ui)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.mission_selector_label_ui)

    def _get_difficulty_ui(self, difficulty):
        """Gets UI element's name from difficulty number."""
        if self.DIFFICULTY == Missions._DIFFICULTY_4:
            if difficulty == 1:
                return Missions._DIFFICULTY_4.STAGE_1
            if difficulty == 2:
                return Missions._DIFFICULTY_4.STAGE_2
            if difficulty == 3:
                return Missions._DIFFICULTY_4.STAGE_3
            if difficulty == 4:
                return Missions._DIFFICULTY_4.STAGE_4
        if self.DIFFICULTY == Missions._DIFFICULTY_6:
            if difficulty == 1:
                return Missions._DIFFICULTY_6.STAGE_1
            if difficulty == 2:
                return Missions._DIFFICULTY_6.STAGE_2
            if difficulty == 3:
                return Missions._DIFFICULTY_6.STAGE_3
            if difficulty == 4:
                return Missions._DIFFICULTY_6.STAGE_4
            if difficulty == 5:
                return Missions._DIFFICULTY_6.STAGE_5
            if difficulty == 6:
                return Missions._DIFFICULTY_6.STAGE_6
        logger.warning(f"Got wrong difficulty or class setup: class = {self.DIFFICULTY.__name__}, "
                       f"difficulty={difficulty}. Trying to use max difficulty.")
        return Missions._DIFFICULTY_6.STAGE_6

    def start_missions(self, times=10, difficulty=6, farm_shifter_bios=False):
        """Starts stage missions."""
        logger.info(f"{self.mode_name}: {times} stages to complete.")
        if times:
            if self._select_epic_quest() and self._select_mission() and self._select_stage(difficulty=difficulty):
                while times > 0:
                    times = self.start_stage(self.stage_selector_ui, times, farm_shifter_bios=farm_shifter_bios)
        logger.info(f"No more stages for {self.mode_name}.")

    def do_missions(self, times=10, difficulty=6, farm_shifter_bios=False):
        """Does missions.

        :param int times: how many stages to complete.
        :param int difficulty: difficulty of game mode.
        :param bool farm_shifter_bios: DISABLED IN THIS MODE.
        """
        farm_shifter_bios = False
        if times > 0:
            self.start_missions(times=times, difficulty=difficulty, farm_shifter_bios=farm_shifter_bios)
            self.end_missions()


class StupidXMen(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Stupid X-Men."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_STUPID_X_MEN_STAGE_LABEL,
                         stage_1_ui=ui.EQ_STUPID_X_MEN_STAGE_1, stage_2_ui=ui.EQ_STUPID_X_MEN_STAGE_2)


class TheBigTwin(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: The Big Twin."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_THE_BIG_TWIN_STAGE_LABEL,
                         stage_1_ui=ui.EQ_THE_BIG_TWIN_STAGE_1, stage_2_ui=ui.EQ_THE_BIG_TWIN_STAGE_2)


class TwistedWorld(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Twisted World."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_TWISTED_WORLD_STAGE_LABEL,
                         stage_1_ui=ui.EQ_TWISTED_WORLD_STAGE_1, stage_2_ui=ui.EQ_TWISTED_WORLD_STAGE_2)


class VeiledSecret(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Veiled Secret."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_VEILED_SECRET_STAGE_LABEL,
                         stage_1_ui=ui.EQ_VEILED_SECRET_STAGE_1, stage_2_ui=ui.EQ_VEILED_SECRET_STAGE_2)


class TheFault(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: The Fault."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_THE_FAULT_STAGE_LABEL,
                         stage_1_ui=ui.EQ_THE_FAULT_STAGE_1, stage_2_ui=ui.EQ_THE_FAULT_STAGE_2)


class BeginningOfTheChaos(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Beginning Of The Chaos."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_BEGINNING_OF_THE_CHAOS_STAGE_LABEL)


class DoomsDay(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Doom's Day."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_DOOMSDAY_STAGE_LABEL)


class MutualEnemy(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Mutual Enemy."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_MUTUAL_ENEMY_STAGE_LABEL)


class FateOfTheUniverse(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Fate of the Universe."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_FATE_OF_THE_UNIVERSE_STAGE_LABEL)


class PlayingHero(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Playing Hero."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_PLAYING_HERO_STAGE_LABEL)


class GoldenGods(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Golden Gods."""

    def __init__(self, game):
        super().__init__(game=game, mode_label_ui=ui.EQ_GOLDEN_GODS_STAGE_LABEL,
                         stage_1_ui=ui.EQ_GOLDEN_GODS_STAGE_1, stage_2_ui=ui.EQ_GOLDEN_GODS_STAGE_2)


class StingOfTheScorpion(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Sting Of The Scorpion."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_DARK_REIGN, ui.EQ_REFORMED_ROGUES, ui.EQ_REFORMED_ROGUES_LABEL,
                         ui.EQ_NORMAL_STAGE_1, 'Sting Of The Scorpion')


class SelfDefenseProtocol(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Self-Defense Protocol."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_DARK_REIGN, ui.EQ_REFORMED_ROGUES, ui.EQ_REFORMED_ROGUES_LABEL,
                         ui.EQ_NORMAL_STAGE_2, 'Self-Defense Protocol')


class DangerousSisters(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Dangerous Sisters."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_GALACTIC_IMPERATIVE, ui.EQ_UNEXPECTED_INTRUDER,
                         ui.EQ_UNEXPECTED_INTRUDER_LABEL, ui.EQ_NORMAL_STAGE_1, 'Dangerous Sisters')


class CosmicRider(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Cosmic Rider."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_GALACTIC_IMPERATIVE, ui.EQ_UNEXPECTED_INTRUDER,
                         ui.EQ_UNEXPECTED_INTRUDER_LABEL, ui.EQ_NORMAL_STAGE_2, 'Cosmic Rider')


class InhumanPrincess(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Inhuman Princess."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_FIRST_FAMILY, ui.EQ_NEW_FACES, ui.EQ_NEW_FACES_LABEL,
                         ui.EQ_NORMAL_STAGE_1, 'Inhuman Princess')


class MeanAndGreen(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Mean & Green."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_FIRST_FAMILY, ui.EQ_NEW_FACES, ui.EQ_NEW_FACES_LABEL,
                         ui.EQ_NORMAL_STAGE_2, 'Mean & Green')


class DarkAdvent(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Dark Advent."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_SORCERER_SUPREME, ui.EQ_DARK_DIMENSION, ui.EQ_DARK_DIMENSION_LABEL,
                         ui.EQ_NORMAL_STAGE_1, 'Dark Advent')


class IncreasingDarkness(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Increasing Darkness."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_SORCERER_SUPREME, ui.EQ_DARK_DIMENSION, ui.EQ_DARK_DIMENSION_LABEL,
                         ui.EQ_NORMAL_STAGE_2, 'Increasing Darkness')


class Blindsided(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Blindsided."""

    def __init__(self, game):
        super().__init__(game, ui.EQ_RISE_OF_X_MEN, ui.EQ_TRACKING, ui.EQ_TRACKING_LABEL,
                         ui.EQ_BLINDSIDED, 'Blindsided')


class LegacyOfBlood(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Legacy Of Blood."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_DARK_REIGN, ui.EQ_CUTTHROAT_COMPANIONS,
                         ui.EQ_CUTTHROAT_COMPANIONS_LABEL, ui.EQ_LEGACY_OF_BLOOD)


class QuantumPower(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Quantum Power."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_GALACTIC_IMPERATIVE, ui.EQ_SPACE_PRISON, ui.EQ_SPACE_PRISON_LABEL,
                         ui.EQ_QUANTUM_POWER)


class WingsOfDarkness(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Wings of Darkness."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_GALACTIC_IMPERATIVE, ui.EQ_SPACE_PRISON, ui.EQ_SPACE_PRISON_LABEL,
                         ui.EQ_WINGS_OF_DARKNESS)


class ClobberinTime(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Cloberrin' Time."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_FIRST_FAMILY, ui.EQ_LIKE_BROTHERS, ui.EQ_LIKE_BROTHERS_LABEL,
                         ui.EQ_CLOBBERIN_TIME)


class Hothead(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Hot Head."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_FIRST_FAMILY, ui.EQ_LIKE_BROTHERS, ui.EQ_LIKE_BROTHERS_LABEL,
                         ui.EQ_HOTHEAD)


class AwManThisGuy(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: 'Aw, Man. This Guy?'."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_X_FORCE, ui.EQ_MESSY_FRIENDS, ui.EQ_MESSY_FRIENDS_LABEL,
                         ui.EQ_AW_MAN_THIS_GUY)


class DominoFalls(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Domino Falls."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_X_FORCE, ui.EQ_MESSY_FRIENDS, ui.EQ_MESSY_FRIENDS_LABEL,
                         ui.EQ_DOMINO_FALLS)


class GoingRogue(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Going Rogue."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_RISE_OF_X_MEN, ui.EQ_TRACKING, ui.EQ_TRACKING_LABEL,
                         ui.EQ_GOING_ROGUE)


class FriendsAndEnemies(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Friends and Enemies."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_RISE_OF_X_MEN, ui.EQ_TRACKING, ui.EQ_TRACKING_LABEL,
                         ui.EQ_FRIENDS_AND_ENEMIES)


class WeatheringTheStorm(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Weathering The Storm."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, ui.EQ_RISE_OF_X_MEN, ui.EQ_TRACKING, ui.EQ_TRACKING_LABEL,
                         ui.EQ_WEATHERING_THE_STORM)


class RoadToMonastery(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Road to the Monastery."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, ui.EQ_SORCERER_SUPREME, ui.EQ_MEMORY_MISSION, ui.EQ_MEMORY_MISSION_LABEL,
                         ui.EQ_ROAD_TO_MONASTERY)


class MysteriousAmbush(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Mysterious Ambush."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, ui.EQ_SORCERER_SUPREME, ui.EQ_MEMORY_MISSION, ui.EQ_MEMORY_MISSION_LABEL,
                         ui.EQ_MYSTERIOUS_AMBUSH)


class MonasteryInTrouble(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Monastery in Trouble."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, ui.EQ_SORCERER_SUPREME, ui.EQ_MEMORY_MISSION, ui.EQ_MEMORY_MISSION_LABEL,
                         ui.EQ_MONASTERY_IN_TROUBLE)


class PowerOfTheDark(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Power of the Dark."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, ui.EQ_SORCERER_SUPREME, ui.EQ_MEMORY_MISSION, ui.EQ_MEMORY_MISSION_LABEL,
                         ui.EQ_POWER_OF_THE_DARK)
