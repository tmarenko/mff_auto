from lib.functions import wait_until
from lib.battle_bot import AutoBattleBot
from lib.missions import Missions
import re
import logging
import time

logger = logging.getLogger(__name__)

stages_regexp = re.compile(r"(\d*)/\d*")


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
            logger.error(f"Cannot start Epic Quest stage {stage_button}, exiting.")
            return 0
        auto_battle_bot = AutoBattleBot(self.game)
        ally_appeared = auto_battle_bot.wait_until_shifter_appeared() if farm_shifter_bios else True
        if ally_appeared:
            auto_battle_bot.fight()
            stage_num -= 1
            logger.debug(f"{stage_num} stages left to complete")
            self.close_mission_notifications()
            if stage_num > 0:
                self.press_repeat_button()
            else:
                self.press_home_button()
            return stage_num
        elif farm_shifter_bios and not ally_appeared:
            logger.info("No ally, restarting")
            if not self.game.restart_game():
                return 0
            self.game.select_mode(self.mode_name)
        return stage_num

    def do_missions(self, farm_shifter_bios=False):
        """Do missions.

        :param farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        if self.stages > 0:
            self.start_missions(farm_shifter_bios=farm_shifter_bios)
            self.end_missions()

    def start_missions(self, farm_shifter_bios=False):
        """Start missions.

        :param farm_shifter_bios: should game be restarted if shifter isn't appeared.
        """
        pass


class StupidXMen(EpicQuests):
    """Class for working with Epic Quest mission: Stupid X-Men."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_STUPID_X_MEN_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start Stupid X-Men missions."""
        logger.info(f"Stupid X-Men: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.stupid_x_men_stages
            logger.info(f"Stupid X-Men: Available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num + stage_2_num > self.stages:
                logging.debug(f"Stages count {self.stages} is lesser than available stages. Second stage is locked.")
                stage_2_num = 0
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.ui['EQ_STUPID_X_MEN_STAGE_1'].button, stage_1_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui['EQ_STUPID_X_MEN_STAGE_2'].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info("No more stages for Stupid X-Men.")

    @property
    def stupid_x_men_stages(self):
        """Stages of Stupid X-Men missions."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['EQ_STUPID_X_MEN_STAGE_LABEL']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
                stage_1 = self.player.get_screen_text(self.ui['EQ_STUPID_X_MEN_STAGE_1'])
                stage_2 = self.player.get_screen_text(self.ui['EQ_STUPID_X_MEN_STAGE_2'])
                stage_1_num = re.findall(stages_regexp, stage_1)
                stage_2_num = re.findall(stages_regexp, stage_2)
                try:
                    stage_1_int = int(stage_1_num[0])
                    stage_2_int = int(stage_2_num[0])
                except ValueError:
                    logger.critical(f"Stupid X-Men: cannot convert stages to integers: {stage_1} and {stage_2}")
                    stage_1_int = 0
                    stage_2_int = 0
                return stage_1_int, stage_2_int


class TheBigTwin(EpicQuests):
    """Class for working with Epic Quest mission: The Big Twin."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_THE_BIG_TWIN_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start The Big Twin missions."""
        farm_shifter_bios = False
        logger.info(f"The Big Twin: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.the_big_twin_stages
            logger.info(f"The Big Twin: Available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num + stage_2_num > self.stages:
                logging.debug(f"Stages count {self.stages} is lesser than available stages. Second stage is locked.")
                stage_2_num = 0
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.ui['EQ_THE_BIG_TWIN_STAGE_1'].button, stage_1_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui['EQ_THE_BIG_TWIN_STAGE_2'].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info("No more stages for The Big Twin.")

    @property
    def the_big_twin_stages(self):
        """Stages of The Big Twin missions."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['EQ_THE_BIG_TWIN_STAGE_LABEL']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
                stage_1 = self.player.get_screen_text(self.ui['EQ_THE_BIG_TWIN_STAGE_1'])
                stage_2 = self.player.get_screen_text(self.ui['EQ_THE_BIG_TWIN_STAGE_2'])
                stage_1_num = re.findall(stages_regexp, stage_1)
                stage_2_num = re.findall(stages_regexp, stage_2)
                try:
                    stage_1_int = int(stage_1_num[0])
                    stage_2_int = int(stage_2_num[0])
                except ValueError:
                    logger.critical(f"The Big Twin: cannot convert stages to integers: {stage_1} and {stage_2}")
                    stage_1_int = 0
                    stage_2_int = 0
                return stage_1_int, stage_2_int


class NewFaces(EpicQuests):
    """Class for working with Epic Quest mission: New Faces."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_NEW_FACES_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start New Faces missions."""
        farm_shifter_bios = False
        logger.info(f"New Faces: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.new_faces_stages
            logger.info(f"New Faces: Available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num + stage_2_num > self.stages:
                logging.debug(f"Stages count {self.stages} is lesser than available stages. Second stage is locked.")
                stage_2_num = 0
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.ui['EQ_NEW_FACES_STAGE_1'].button, stage_1_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui['EQ_NEW_FACES_STAGE_2'].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info("No more stages for New Faces.")

    @property
    def new_faces_stages(self):
        """Stages of New Faces missions."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['EQ_NEW_FACES_STAGE_LABEL']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
                stage_1 = self.player.get_screen_text(self.ui['EQ_NEW_FACES_STAGE_1'])
                stage_2 = self.player.get_screen_text(self.ui['EQ_NEW_FACES_STAGE_2'])
                stage_1_num = re.findall(stages_regexp, stage_1)
                stage_2_num = re.findall(stages_regexp, stage_2)
                try:
                    stage_1_int = int(stage_1_num[0])
                    stage_2_int = int(stage_2_num[0])
                except ValueError:
                    logger.critical(f"New Faces: cannot convert stages to integers: {stage_1} and {stage_2}")
                    stage_1_int = 0
                    stage_2_int = 0
                return stage_1_int, stage_2_int


class TwistedWorld(EpicQuests):
    """Class for working with Epic Quest mission: Twisted World."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_TWISTED_WORLD_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start Twisted World missions."""
        logger.info(f"Twisted World: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.twisted_world_stages
            logger.info(f"Twisted World: Available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num + stage_2_num > self.stages:
                logging.debug(f"Stages count {self.stages} is lesser than available stages. Second stage is locked.")
                stage_2_num = 0
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.ui['EQ_TWISTED_WORLD_STAGE_1'].button, stage_1_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui['EQ_TWISTED_WORLD_STAGE_2'].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info("No more stages for Twisted World.")

    @property
    def twisted_world_stages(self):
        """Stages of Twisted World missions."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['EQ_TWISTED_WORLD_STAGE_LABEL']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
                stage_1 = self.player.get_screen_text(self.ui['EQ_TWISTED_WORLD_STAGE_1'])
                stage_2 = self.player.get_screen_text(self.ui['EQ_TWISTED_WORLD_STAGE_2'])
                stage_1_num = re.findall(stages_regexp, stage_1)
                stage_2_num = re.findall(stages_regexp, stage_2)
                try:
                    stage_1_int = int(stage_1_num[0])
                    stage_2_int = int(stage_2_num[0])
                except ValueError:
                    logger.critical(f"Twisted World: cannot convert stages to integers: {stage_1} and {stage_2}")
                    stage_1_int = 0
                    stage_2_int = 0
                return stage_1_int, stage_2_int


class DarkDimension(EpicQuests):
    """Class for working with Epic Quest mission: Dark Dimension."""

    SATANA = "EQ_DARK_DIMENSION_STAGE_1"
    HELLSTORM = "EQ_DARK_DIMENSION_STAGE_2"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_DARK_DIMENSION_STAGE_LABEL')
        self.stages = super().stages

    def do_missions(self, stage=None):
        """Do missions.

        :param stage: mission stage name.
        """
        if self.stages > 0:
            self.start_missions(stage=stage)
            self.end_missions()

    def start_missions(self, stage=None):
        """Start Dark Dimension missions.

        :param stage: mission stage name.
        """
        logger.info(f"Dark Dimension: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            while self.stages > 0:
                self.stages = self.start_stage(self.ui[stage].button, self.stages)
        logger.info("No more stages for Dark Dimension.")


class BeginningOfTheChaos(EpicQuests):
    """Class for working with Epic Quest mission: Beginning Of The Chaos."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_BEGINNING_OF_THE_CHAOS_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start Beginning Of The Chaos missions."""
        logger.info(f"Beginning Of The Chaos: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_num = self.stages
            while stage_num > 0:
                stage_num = self.start_stage(self.ui['EQ_BEGINNING_OF_THE_CHAOS_STAGE_LABEL'].button, stage_num,
                                             farm_shifter_bios=farm_shifter_bios)
        logger.info("No more stages for Beginning Of The Chaos.")


class DoomsDay(EpicQuests):
    """Class for working with Epic Quest mission: Doom's Day."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_DOOMSDAY_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start Doom's Day missions."""
        logger.info(f"Doom's Day: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_num = self.stages
            while stage_num > 0:
                stage_num = self.start_stage(self.ui['EQ_DOOMSDAY_STAGE_LABEL'].button, stage_num,
                                             farm_shifter_bios=farm_shifter_bios)
        logger.info("No more stages for Doom's Day.")


class MutualEnemy(EpicQuests):
    """Class for working with Epic Quest mission: Mutual Enemy."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_MUTUAL_ENEMY_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start Mutual Enemy missions."""
        logger.info(f"Mutual Enemy: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_num = self.stages
            while stage_num > 0:
                stage_num = self.start_stage(self.ui['EQ_MUTUAL_ENEMY_STAGE_LABEL'].button, stage_num,
                                             farm_shifter_bios=farm_shifter_bios)
        logger.info("No more stages for Mutual Enemy.")


class VeiledSecret(EpicQuests):
    """Class for working with Epic Quest mission: Veiled Secret."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_VEILED_SECRET_STAGE_LABEL')
        self.stages = super().stages

    def start_missions(self, farm_shifter_bios=False):
        """Start Veiled Secret missions."""
        farm_shifter_bios = False
        logger.info(f"Veiled Secret: {self.stages} stages available")
        if self.stages > 0:
            self.game.select_mode(self.mode_name)
            stage_1_num, stage_2_num = self.veiled_secret_stages
            logger.info(f"Veiled Secret: Available stages: {stage_1_num} and {stage_2_num}")
            if stage_1_num > 0 or stage_2_num > 0:
                while stage_1_num > 0 and self.stages > 0:
                    stage_1_num = self.start_stage(self.ui['EQ_VEILED_SECRET_STAGE_1'].button, stage_1_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
                if self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui['EQ_VEILED_SECRET_STAGE_2'].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info("No more stages for Veiled Secret.")

    @property
    def veiled_secret_stages(self):
        """Stages of Veiled Secret missions."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['EQ_VEILED_SECRET_STAGE_LABEL']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
                stage_1 = self.player.get_screen_text(self.ui['EQ_VEILED_SECRET_STAGE_1'])
                stage_2 = self.player.get_screen_text(self.ui['EQ_VEILED_SECRET_STAGE_2'])
                stage_1_num = re.findall(stages_regexp, stage_1)
                stage_2_num = re.findall(stages_regexp, stage_2)
                try:
                    stage_1_int = int(stage_1_num[0])
                    stage_2_int = int(stage_2_num[0])
                except ValueError:
                    logger.critical(f"Veiled Secret: cannot convert stages to integers: {stage_1} and {stage_2}")
                    stage_1_int = 0
                    stage_2_int = 0
                return stage_1_int, stage_2_int


class MemoryMission(Missions):
    """Class for working with Epic Quest mission: Memory Mission."""

    MORDO = "EQ_MEMORY_MISSION_MORDO"
    WONG = "EQ_MEMORY_MISSION_WONG"
    ANCIENT_ONE = "EQ_MEMORY_MISSION_ANCIENT_ONE"
    KAECILIUS = "EQ_MEMORY_MISSION_KAECILIUS"
    DIFFICULTY = Missions._DIFFICULTY_6

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'EQ_MEMORY_MISSION_STAGE_LABEL')

    def do_missions(self, stage=None, difficulty=None):
        """Do missions.

        :param stage: name of UI element that contains info about Special Mission stage.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        """
        if self.stages > 0:
            self.start_missions(stage=stage, difficulty=difficulty)
            self.end_missions()

    def start_missions(self, stage=None, difficulty=None):
        """Start Memory Missions.

        :param stage: name of UI element that contains info about Special Mission stage.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        """
        self.game.select_mode(self.mode_name)
        logger.info(f"Memory Mission: {self.stages} stages available")
        if self.stages > 0:
            self.select_stage(stage=stage, difficulty=difficulty)
            while self.stages > 0 and self.is_stage_startable():
                if not self.press_start_button():
                    logger.error("Cannot start Memory Missions, exiting.")
                    return
                AutoBattleBot(self.game).fight()
                self.stages -= 1
                self.close_mission_notifications()
                if self.stages > 0:
                    self.press_repeat_button()
                else:
                    self.press_home_button()
        logger.info("No more stages for Memory Mission.")

    def select_stage(self, stage, difficulty):
        """Select Memory Mission's stage.

        :param stage: name of UI element that contains info about Memory Mission stage.
        :param difficulty: name of UI element that contains info about difficulty of stage.
        """
        if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['EQ_MEMORY_MISSION_STAGE_LABEL']):
            self.player.click_button(self.ui[stage].button)
            if "_2_" in self.ui[difficulty].name:
                logger.debug("Difficulty is referring from the bottom of list. Trying to scroll.")
                self.player.drag(self.ui['DIFFICULTY_DRAG_FROM'].button, self.ui['DIFFICULTY_DRAG_TO'].button)
                time.sleep(1)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui[difficulty]):
                self.player.click_button(self.ui[difficulty].button)
        return wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['START_BUTTON'])
