from lib.functions import wait_until, r_sleep
from lib.game.battle_bot import AutoBattleBot
from lib.game.missions.missions import Missions
import lib.logger as logging

logger = logging.get_logger(__name__)


class EpicQuests(Missions):
    """Class for working with Epic Quests missions."""

    def __init__(self, game, mode_label):
        """Class initialization.

        :param game.Game game: instance of the game.
        :param string mode_label: mission's game mode label.
        """
        super().__init__(game, mode_label)

    def start_stage(self, stage_button, stage_num, farm_shifter_bios=False):
        """Start Epic Quests stage.

        :param stage_button: rect of button to start stage.
        :param stage_num: available stages count.
        :param farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        if not wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['START_BUTTON']):
            self.player.click_button(stage_button)
            wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['START_BUTTON'])
        if not self.press_start_button():
            logger.error(f"Cannot start Epic Quest stage {self.mode_name}, exiting.")
            return 0
        auto_battle_bot = AutoBattleBot(self.game, self.battle_over_conditions)
        ally_appeared = auto_battle_bot.wait_until_shifter_appeared() if farm_shifter_bios else True
        if farm_shifter_bios and not ally_appeared:
            logger.info("No ally, restarting")
            if self.game.restart_game(repeat_while=auto_battle_bot.is_battle):
                self.game.select_mode(self.mode_name)
                return stage_num

        auto_battle_bot.fight()
        stage_num -= 1
        logger.debug(f"{stage_num} stages left to complete")
        self.close_mission_notifications()
        if stage_num > 0:
            self.press_repeat_button()
        else:
            self.press_home_button()
        return stage_num

    def do_missions(self, times=None, farm_shifter_bios=False):
        """Do missions.

        :param times: how many stages to complete.
        :param farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(farm_shifter_bios=farm_shifter_bios)
            self.end_missions()

    def start_missions(self, farm_shifter_bios=False):
        """Start missions.

        :param farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        pass


class OneStageEpicQuest(EpicQuests):
    """Class for working with Epic Quests with one single stage."""

    def __init__(self, game, mode_label):
        """Class initialization.

        :param game.Game game: instance of the game.
        :param string mode_label: mission's game mode label.
        """
        super().__init__(game, mode_label)
        self.mode_label = mode_label

    def start_missions(self, farm_shifter_bios=False):
        """Start single stage missions."""
        logger.info(f"{self.mode_name}: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_num = self.stages
            while stage_num > 0:
                stage_num = self.start_stage(self.ui[self.mode_label].button, stage_num,
                                             farm_shifter_bios=farm_shifter_bios)
        logger.info(f"No more stages for {self.mode_name}.")


class TwoStageEpicQuest(EpicQuests):
    """Class for working with Epic Quests with two separate stages."""

    def __init__(self, game, mode_label, stage_1, stage_2):
        """Class initialization.

        :param game.Game game: instance of the game.
        :param string mode_label: mission's game mode label.
        """
        super().__init__(game, mode_label)
        self.mode_label = mode_label
        self.stage_1, self.stage_2 = stage_1, stage_2

    def start_missions(self, farm_shifter_bios=False):
        """Start two stages missions."""
        logger.info(f"{self.mode_name}: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.separate_stages
            logger.info(f"{self.mode_name}: available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num + stage_2_num > self.stages:
                logger.debug(f"Stages count {self.stages} is lesser than available stages. Second stage is locked.")
                stage_2_num = 0
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.ui[self.stage_1].button, stage_1_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if stage_2_num > 0 and self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui[self.stage_2].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info(f"No more stages for {self.mode_name}.")

    @property
    def separate_stages(self):
        """Stages of two stages missions."""
        if not wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui[self.mode_label]):
            logger.error(f"Can't find mission label: {self.mode_label}")
            return
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
            stage_1 = self.player.get_screen_text(self.ui[self.stage_1])
            stage_2 = self.player.get_screen_text(self.ui[self.stage_2])
            stage_1_current, _ = self.game.get_current_and_max_values_from_text(stage_1)
            stage_2_current, _ = self.game.get_current_and_max_values_from_text(stage_2)
            return stage_1_current, stage_2_current
        logger.error("Can't find `Recommended Lv` text in mission lobby.")


class TenStageEpicQuest(EpicQuests):
    """Class for working with Epic Quests with 10 stages (usual missions without difficulty)."""

    def __init__(self, game, mode_selector, mission_selector, mission_selector_label, stage_selector, stage_name=None):
        """Class initialization.

        :param game.Game game: instance of the game.
        :param mode_selector: UI element name of Epic Quest selector.
        :param mission_selector: UI element name of Epic Quest's mission selector.
        :param mission_selector_label: UI element name of Epic Quest's mission label.
        :param stage_selector: UI element name of Epic Quest's stage selector.
        :param stage_name: Epic Quest's stage name.
        """
        super().__init__(game, '')
        self.mode_selector = self.ui[mode_selector]
        self.mission_selector = self.ui[mission_selector]
        self.mission_selector_label = self.ui[mission_selector_label]
        self.stage_selector = self.ui[stage_selector]
        self.mode_name = stage_name if stage_name else self.stage_selector.text

    def select_epic_quest(self):
        """Select Epic Quest."""
        if self.game.go_to_epic_quests():
            if self.mode_selector.name in ['EQ_RISE_OF_X_MEN', 'EQ_SORCERER_SUPREME', 'EQ_X_FORCE']:
                logger.debug("Epic Quests is referring to the second page. Trying to scroll.")
                self.player.drag(self.ui['EQ_PAGE_DRAG_FROM'].button, self.ui['EQ_PAGE_DRAG_TO'].button)
                r_sleep(1)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.mode_selector):
                logger.debug(f"Selecting Epic Quest: {self.mode_selector.name}")
                self.player.click_button(self.mode_selector.button)
                return True

    def select_mission(self):
        """Select missions in Epic Quest."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.mission_selector):
            logger.debug(f"Selecting Epic Quest's mission: {self.mission_selector.name}")
            self.player.click_button(self.mission_selector.button)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.mission_selector_label) and wait_until(
                self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL'])

    def select_stage(self):
        """Select stage in missions in Epic Quest."""
        logger.debug(f"Selecting Epic Quest's stage: {self.stage_selector.name}")
        self.player.click_button(self.stage_selector.button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['START_BUTTON'])

    def start_missions(self, times=10, farm_shifter_bios=False):
        """Start stage missions."""
        logger.info(f"{self.mode_name}: {times} stages to complete.")
        if times:
            if self.select_epic_quest() and self.select_mission() and self.select_stage():
                while times > 0:
                    times = self.start_stage(self.stage_selector.button, times, farm_shifter_bios=farm_shifter_bios)
        logger.info(f"No more stages for {self.mode_name}.")

    def do_missions(self, times=10, farm_shifter_bios=False):
        """Do missions.

        :param times: how many stages to complete.
        :param farm_shifter_bios: DISABLED IN THIS MODE.
        """
        farm_shifter_bios = False
        if times > 0:
            self.start_missions(times=times, farm_shifter_bios=farm_shifter_bios)
            self.end_missions()


class TenStageWithDifficultyEpicQuest(TenStageEpicQuest):
    DIFFICULTY = None  # Setup this in child class to Missions._DIFFICULTY_4 or Missions._DIFFICULTY_6

    def select_stage(self, difficulty=6):
        """Select stage in missions in Epic Quest."""
        difficulty_ui = self.ui[self.get_difficulty_ui(difficulty)]
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.stage_selector):
            self.player.click_button(self.stage_selector.button)
            if "_2_" in difficulty_ui.name:
                logger.debug("Difficulty is referring from the bottom of list. Trying to scroll.")
                self.player.drag(self.ui['DIFFICULTY_DRAG_FROM'].button, self.ui['DIFFICULTY_DRAG_TO'].button)
                r_sleep(1)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=difficulty_ui):
                self.player.click_button(difficulty_ui.button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['START_BUTTON'])

    def select_mission(self):
        """Select missions in Epic Quest."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.mission_selector):
            logger.debug(f"Selecting Epic Quest's mission: {self.mission_selector.name}")
            self.player.click_button(self.mission_selector.button)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.mission_selector_label)

    def get_difficulty_ui(self, difficulty):
        """Get UI element's name from difficulty number."""
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
        logger.warning(f"Get wrong difficulty or class setup: class = {self.DIFFICULTY.__name__}, "
                       f"difficulty={difficulty}. Trying to use max difficulty.")
        return Missions._DIFFICULTY_6.STAGE_6

    def start_missions(self, times=10, difficulty=6, farm_shifter_bios=False):
        """Start stage missions."""
        logger.info(f"{self.mode_name}: {times} stages to complete.")
        if times:
            if self.select_epic_quest() and self.select_mission() and self.select_stage(difficulty=difficulty):
                while times > 0:
                    times = self.start_stage(self.stage_selector.button, times, farm_shifter_bios=farm_shifter_bios)
        logger.info(f"No more stages for {self.mode_name}.")

    def do_missions(self, times=10, difficulty=6, farm_shifter_bios=False):
        """Do missions.

        :param times: how many stages to complete.
        :param difficulty: difficulty of game mode.
        :param farm_shifter_bios: DISABLED IN THIS MODE.
        """
        farm_shifter_bios = False
        if times > 0:
            self.start_missions(times=times, difficulty=difficulty, farm_shifter_bios=farm_shifter_bios)
            self.end_missions()


class StupidXMen(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Stupid X-Men."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_STUPID_X_MEN_STAGE_LABEL',
                         stage_1='EQ_STUPID_X_MEN_STAGE_1', stage_2='EQ_STUPID_X_MEN_STAGE_2')


class TheBigTwin(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: The Big Twin."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_THE_BIG_TWIN_STAGE_LABEL',
                         stage_1='EQ_THE_BIG_TWIN_STAGE_1', stage_2='EQ_THE_BIG_TWIN_STAGE_2')


class TwistedWorld(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Twisted World."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_TWISTED_WORLD_STAGE_LABEL',
                         stage_1='EQ_TWISTED_WORLD_STAGE_1', stage_2='EQ_TWISTED_WORLD_STAGE_2')


class VeiledSecret(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Veiled Secret."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_VEILED_SECRET_STAGE_LABEL',
                         stage_1='EQ_VEILED_SECRET_STAGE_1', stage_2='EQ_VEILED_SECRET_STAGE_2')


class TheFault(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: The Fault."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_THE_FAULT_STAGE_LABEL',
                         stage_1='EQ_THE_FAULT_STAGE_1', stage_2='EQ_THE_FAULT_STAGE_2')


class BeginningOfTheChaos(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Beginning Of The Chaos."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_BEGINNING_OF_THE_CHAOS_STAGE_LABEL')


class DoomsDay(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Doom's Day."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_DOOMSDAY_STAGE_LABEL')


class MutualEnemy(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Mutual Enemy."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_MUTUAL_ENEMY_STAGE_LABEL')


class FateOfTheUniverse(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Fate of the Universe."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_FATE_OF_THE_UNIVERSE_STAGE_LABEL')


class PlayingHero(OneStageEpicQuest):
    """Class for working with Epic Quest mission: Playing Hero."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_PLAYING_HERO_STAGE_LABEL')


class GoldenGods(TwoStageEpicQuest):
    """Class for working with Epic Quest mission: Golden Gods."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game=game, mode_label='EQ_GOLDEN_GODS_STAGE_LABEL',
                         stage_1='EQ_GOLDEN_GODS_STAGE_1', stage_2='EQ_GOLDEN_GODS_STAGE_2')


class StingOfTheScorpion(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Sting Of The Scorpion."""

    def __init__(self, game):
        super().__init__(game, 'EQ_DARK_REIGN', 'EQ_REFORMED_ROGUES', 'EQ_REFORMED_ROGUES_LABEL',
                         'EQ_NORMAL_STAGE_1', 'Sting Of The Scorpion')


class SelfDefenseProtocol(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Self-Defense Protocol."""

    def __init__(self, game):
        super().__init__(game, 'EQ_DARK_REIGN', 'EQ_REFORMED_ROGUES', 'EQ_REFORMED_ROGUES_LABEL',
                         'EQ_NORMAL_STAGE_2', 'Self-Defense Protocol')


class DangerousSisters(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Dangerous Sisters."""

    def __init__(self, game):
        super().__init__(game, 'EQ_GALACTIC_IMPERATIVE', 'EQ_UNEXPECTED_INTRUDER', 'EQ_UNEXPECTED_INTRUDER_LABEL',
                         'EQ_NORMAL_STAGE_1', 'Dangerous Sisters')


class CosmicRider(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Cosmic Rider."""

    def __init__(self, game):
        super().__init__(game, 'EQ_GALACTIC_IMPERATIVE', 'EQ_UNEXPECTED_INTRUDER', 'EQ_UNEXPECTED_INTRUDER_LABEL',
                         'EQ_NORMAL_STAGE_2', 'Cosmic Rider')


class InhumanPrincess(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Inhuman Princess."""

    def __init__(self, game):
        super().__init__(game, 'EQ_FIRST_FAMILY', 'EQ_NEW_FACES', 'EQ_NEW_FACES_LABEL',
                         'EQ_NORMAL_STAGE_1', 'Inhuman Princess')


class MeanAndGreen(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Mean & Green."""

    def __init__(self, game):
        super().__init__(game, 'EQ_FIRST_FAMILY', 'EQ_NEW_FACES', 'EQ_NEW_FACES_LABEL',
                         'EQ_NORMAL_STAGE_2', 'Mean & Green')


class DarkAdvent(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Dark Advent."""

    def __init__(self, game):
        super().__init__(game, 'EQ_SORCERER_SUPREME', 'EQ_DARK_DIMENSION', 'EQ_DARK_DIMENSION_LABEL',
                         'EQ_NORMAL_STAGE_1', 'Dark Advent')


class IncreasingDarkness(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Increasing Darkness."""

    def __init__(self, game):
        super().__init__(game, 'EQ_SORCERER_SUPREME', 'EQ_DARK_DIMENSION', 'EQ_DARK_DIMENSION_LABEL',
                         'EQ_NORMAL_STAGE_2', 'Increasing Darkness')


class Blindsided(TenStageEpicQuest):
    """Class for working with Epic Quest mission stages: Blindsided."""

    def __init__(self, game):
        super().__init__(game, 'EQ_RISE_OF_X_MEN', 'EQ_TRACKING', 'EQ_TRACKING_LABEL',
                         'EQ_BLINDSIDED', 'Blindsided')


class LegacyOfBlood(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Legacy Of Blood."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_DARK_REIGN', 'EQ_CUTTHROAT_COMPANIONS', 'EQ_CUTTHROAT_COMPANIONS_LABEL',
                         'EQ_LEGACY_OF_BLOOD')


class QuantumPower(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Quantum Power."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_GALACTIC_IMPERATIVE', 'EQ_SPACE_PRISON', 'EQ_SPACE_PRISON_LABEL', 'EQ_QUANTUM_POWER')


class WingsOfDarkness(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Wings of Darkness."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_GALACTIC_IMPERATIVE', 'EQ_SPACE_PRISON', 'EQ_SPACE_PRISON_LABEL',
                         'EQ_WINGS_OF_DARKNESS')


class ClobberinTime(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Cloberrin' Time."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_FIRST_FAMILY', 'EQ_LIKE_BROTHERS', 'EQ_LIKE_BROTHERS_LABEL',
                         'EQ_CLOBBERIN_TIME')


class Hothead(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Hot Head."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_FIRST_FAMILY', 'EQ_LIKE_BROTHERS', 'EQ_LIKE_BROTHERS_LABEL',
                         'EQ_HOTHEAD')


class AwManThisGuy(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: 'Aw, Man. This Guy?'."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_X_FORCE', 'EQ_MESSY_FRIENDS', 'EQ_MESSY_FRIENDS_LABEL',
                         'EQ_AW_MAN_THIS_GUY')


class DominoFalls(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Domino Falls."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_X_FORCE', 'EQ_MESSY_FRIENDS', 'EQ_MESSY_FRIENDS_LABEL',
                         'EQ_DOMINO_FALLS')


class GoingRogue(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Going Rogue."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_RISE_OF_X_MEN', 'EQ_TRACKING', 'EQ_TRACKING_LABEL',
                         'EQ_GOING_ROGUE')


class FriendsAndEnemies(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Friends and Enemies."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_RISE_OF_X_MEN', 'EQ_TRACKING', 'EQ_TRACKING_LABEL',
                         'EQ_FRIENDS_AND_ENEMIES')


class WeatheringTheStorm(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Weathering The Storm."""

    DIFFICULTY = Missions._DIFFICULTY_4

    def __init__(self, game):
        super().__init__(game, 'EQ_RISE_OF_X_MEN', 'EQ_TRACKING', 'EQ_TRACKING_LABEL',
                         'EQ_WEATHERING_THE_STORM')


class RoadToMonastery(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Road to the Monastery."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, 'EQ_SORCERER_SUPREME', 'EQ_MEMORY_MISSION', 'EQ_MEMORY_MISSION_LABEL',
                         'EQ_ROAD_TO_MONASTERY')


class MysteriousAmbush(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Mysterious Ambush."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, 'EQ_SORCERER_SUPREME', 'EQ_MEMORY_MISSION', 'EQ_MEMORY_MISSION_LABEL',
                         'EQ_MYSTERIOUS_AMBUSH')


class MonasteryInTrouble(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Monastery in Trouble."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, 'EQ_SORCERER_SUPREME', 'EQ_MEMORY_MISSION', 'EQ_MEMORY_MISSION_LABEL',
                         'EQ_MONASTERY_IN_TROUBLE')


class PowerOfTheDark(TenStageWithDifficultyEpicQuest):
    """Class for working with Epic Quest mission stages: Power of the Dark."""

    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        super().__init__(game, 'EQ_SORCERER_SUPREME', 'EQ_MEMORY_MISSION', 'EQ_MEMORY_MISSION_LABEL',
                         'EQ_POWER_OF_THE_DARK')
