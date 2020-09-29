from multiprocess.context import Process
from lib.game.game import Game
from lib.game.battle_bot import ManualBattleBot
from lib.game.routines import DailyTrivia, ShieldLab, ComicCards, CustomGear
from lib.game.missions.danger_room import DangerRoom
from lib.game.missions.invasion import WorldBossInvasion
from lib.game.missions.squad_battles import SquadBattles
from lib.gui.threading import ThreadPool
from lib.gui.helper import safe_process_stop, reset_player_and_logger
import lib.logger as logging

logger = logging.get_logger(__name__)


class SingleTask:
    """Class for working with single task of execution."""

    def __init__(self, button, task_func, parameters):
        """Class initialization.

        :param TwoStateButton button: button that activates task.
        :param task_func: function to execute.
        :param dict parameters: function's parameters.
        """
        self.run_and_stop_button = button
        self.task_func = task_func
        self.parameters = parameters
        self.threads = ThreadPool()
        self.process = None
        self.run_and_stop_button.connect_first_state(self.execute)
        self.run_and_stop_button.connect_second_state(self.abort)

    def execute(self):
        """Execute function in safe thread."""
        logger.debug(f"Executing single task: {self.__class__.__name__} {self.task_func.__name__}")
        worker = self.threads.run_thread(target=self._execute)
        worker.signals.finished.connect(self.run_and_stop_button.set_first_state)
        self.run_and_stop_button.set_second_state()

    @safe_process_stop
    def abort(self):
        """Abort function's execution."""
        if self.process:
            logger.debug("Task was forcibly stopped.")
            self.process.terminate()
        self.threads.thread_pool.clear()
        self.run_and_stop_button.set_first_state()

    def _execute(self):
        """Execute function."""
        self.process = Process(target=self.task_func, kwargs=self.parameters)
        self.process.start()
        self.process.join()
        logger.debug("Task completed.")


class AutoPlayTask(SingleTask):

    def __init__(self, button, game: Game):
        bot = ManualBattleBot(game, battle_over_conditions=None)

        @reset_player_and_logger(game=game)
        def fight(*args, **kwargs):
            return bot.fight(*args, **kwargs)

        super().__init__(button, fight, {"move_around": False})


class DailyTriviaTask(SingleTask):

    def __init__(self, button, game: Game):
        dt = DailyTrivia(game)

        @reset_player_and_logger(game=game)
        def do_trivia():
            return dt.do_trivia()

        super().__init__(button, do_trivia, {})


class WorldBossInvasionTask(SingleTask):

    def __init__(self, button, game: Game):
        wbi = WorldBossInvasion(game)

        @reset_player_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return wbi.do_missions(*args, **kwargs)

        super().__init__(button, do_missions, {})


class SquadBattleAllTask(SingleTask):

    def __init__(self, button, game: Game):
        sb = SquadBattles(game)

        @reset_player_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return sb.do_missions(*args, **kwargs)

        super().__init__(button, do_missions, {"mode": SquadBattles.MODE.ALL_BATTLES})


class DangerRoomOneBattleTask(SingleTask):

    def __init__(self, button, game: Game):
        dr = DangerRoom(game)

        @reset_player_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return dr.do_missions(*args, **kwargs)

        super().__init__(button, do_missions, {"times": 1})


class ShieldLabCollectAntimatterOneBattleTask(SingleTask):

    def __init__(self, button, game: Game):
        sl = ShieldLab(game)

        @reset_player_and_logger(game=game)
        def collect_antimatter():
            return sl.collect_antimatter()

        super().__init__(button, collect_antimatter, {})


class RestartGameTask(SingleTask):

    def __init__(self, button, game: Game):
        @reset_player_and_logger(game=game)
        def restart_game():
            return game.restart_game()

        if button:
            super().__init__(button, restart_game, {})
        else:
            self.abort = lambda: None


class ComicCardsTask(SingleTask):

    def __init__(self, button, game: Game):
        cc = ComicCards(game)

        @reset_player_and_logger(game=game)
        def upgrade_all_cards():
            return cc.upgrade_all_cards()

        super().__init__(button, upgrade_all_cards, {})


class CustomGearTask(SingleTask):

    def __init__(self, button, game: Game):
        cg = CustomGear(game)

        @reset_player_and_logger(game=game)
        def quick_upgrade_gear(*args, **kwargs):
            return cg.quick_upgrade_gear(*args, **kwargs)

        super().__init__(button, quick_upgrade_gear, {"times": 1})
