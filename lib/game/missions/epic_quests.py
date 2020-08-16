from lib.functions import wait_until
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
            logger.error(f"Cannot start Epic Quest stage {stage_button}, exiting.")
            return 0
        auto_battle_bot = AutoBattleBot(self.game, self.battle_over_conditions)
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
                if self.game.is_main_menu():
                    self.game.select_mode(self.mode_name)
                while stage_2_num > 0 and self.stages > 0:
                    stage_2_num = self.start_stage(self.ui[self.stage_2].button, stage_2_num,
                                                   farm_shifter_bios=farm_shifter_bios)
                    self.stages = stage_1_num + stage_2_num
        logger.info(f"No more stages for {self.mode_name}.")

    @property
    def separate_stages(self):
        """Stages of two stages missions."""
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui[self.mode_label]):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_RECOMMENDED_LVL']):
                stage_1 = self.player.get_screen_text(self.ui[self.stage_1])
                stage_2 = self.player.get_screen_text(self.ui[self.stage_2])
                stage_1_current, _ = self.game.get_current_and_max_values_from_text(stage_1)
                stage_2_current, _ = self.game.get_current_and_max_values_from_text(stage_2)
                return stage_1_current, stage_2_current
            logger.error("Can't find `Recommended Lv` text in mission lobby.")
            return
        logger.error(f"Can't find mission label: {self.mode_label}")


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
