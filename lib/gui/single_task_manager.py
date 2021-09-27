from multiprocess.context import Process

import lib.game.missions as missions
import lib.game.routines as routines
import lib.logger as logging
from lib.game.battle_bot import ManualBattleBot
from lib.game.dispatch_mission import DispatchMission
from lib.game.game import Game
from lib.gui.helper import safe_process_stop, reset_emulator_and_logger
from lib.gui.threading import ThreadPool

logger = logging.get_logger(__name__)


class SingleTask:
    """Class for working with single task of execution."""

    def __init__(self, button, task_func, parameters):
        """Class initialization.

        :param lib.gui.helper.TwoStateButton button: button that activates task.
        :param function task_func: function to execute.
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
        """Executes function in safe thread."""
        logger.debug(f"Executing single task: {self.__class__.__name__} {self.task_func.__name__}")
        from lib.gui.widgets.main import MainWindow
        MainWindow.resume_recorder()
        worker = self.threads.run_thread(func=self._execute)
        worker.signals.finished.connect(self.run_and_stop_button.set_first_state)
        worker.signals.finished.connect(MainWindow.pause_recorder)
        self.run_and_stop_button.set_second_state()

    @safe_process_stop
    def abort(self):
        """Aborts function's execution."""
        if self.process:
            logger.debug("Task was forcibly stopped.")
            self.process.terminate()
        self.threads.thread_pool.clear()
        self.run_and_stop_button.set_first_state()
        from lib.gui.widgets.main import MainWindow
        MainWindow.pause_recorder()

    def _execute(self):
        """Executes function."""
        self.process = Process(target=self.task_func, kwargs=self.parameters)
        self.process.start()
        self.process.join()
        logger.debug("Task completed.")


class SingleTaskWithOptions:

    def __init__(self, button, task_func, task_options):
        """Class initialization.

        :param lib.gui.helper.TwoStateButton button: button that activates task.
        :param function task_func: function to execute.
        :param dict task_options: function's parameters by option's key.
        """
        self.run_and_stop_button = button
        self.task_func = task_func
        self.task_options = task_options
        self.threads = ThreadPool()
        self.process = None
        for task_name, task_parameters in task_options.items():
            def add_action(parameters):
                self.run_and_stop_button.add_action(task_name, lambda: self.execute(parameters))

            add_action(task_parameters)
        self.menu = self.run_and_stop_button.button.menu()
        self.run_and_stop_button.connect_second_state(self.abort)

    def execute(self, parameters):
        """Executes function in safe thread."""
        logger.debug(f"Executing single task: {self.__class__.__name__} {self.task_func.__name__} "
                     f"with parameters {parameters}")
        from lib.gui.widgets.main import MainWindow
        MainWindow.resume_recorder()
        worker = self.threads.run_thread(func=lambda: self._execute(parameters=parameters))
        worker.signals.finished.connect(self.run_and_stop_button.set_first_state)
        worker.signals.finished.connect(self._set_menu)
        worker.signals.finished.connect(MainWindow.pause_recorder)
        self._clear_menu()
        self.run_and_stop_button.set_second_state()

    def _clear_menu(self):
        """Clears button menu."""
        self.run_and_stop_button.button.setMenu(None)

    def _set_menu(self):
        """Sets button menu from cache."""
        self.run_and_stop_button.button.setMenu(self.menu)

    @safe_process_stop
    def abort(self):
        """Aborts function's execution."""
        if self.process:
            logger.debug("Task was forcibly stopped.")
            self.process.terminate()
        self.threads.thread_pool.clear()
        self._set_menu()
        self.run_and_stop_button.set_first_state()
        from lib.gui.widgets.main import MainWindow
        MainWindow.pause_recorder()

    def _execute(self, parameters):
        """Executes function."""
        self.process = Process(target=self.task_func, kwargs=parameters)
        self.process.start()
        self.process.join()
        logger.debug("Task completed.")


class AutoPlayTask(SingleTask):

    def __init__(self, button, game: Game):
        bot = ManualBattleBot(game, battle_over_conditions=None)

        @reset_emulator_and_logger(game=game)
        def fight(*args, **kwargs):
            return bot.fight(*args, **kwargs)

        super().__init__(button, fight, {"move_around": False})


class DailyTriviaTask(SingleTask):

    def __init__(self, button, game: Game):
        dt = routines.DailyTrivia(game)

        @reset_emulator_and_logger(game=game)
        def do_trivia():
            return dt.do_trivia()

        super().__init__(button, do_trivia, {})


class WorldBossInvasionTask(SingleTask):

    def __init__(self, button, game: Game):
        wbi = missions.WorldBossInvasion(game)

        @reset_emulator_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return wbi.do_missions(*args, **kwargs)

        super().__init__(button, do_missions, {})


class SquadBattleAllTask(SingleTask):

    def __init__(self, button, game: Game):
        sb = missions.SquadBattle(game)

        @reset_emulator_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return sb.do_missions(*args, **kwargs)

        super().__init__(button, do_missions, {"mode": missions.SquadBattle.MODE.ALL_BATTLES})


class DangerRoomOneBattleTask(SingleTaskWithOptions):

    def __init__(self, button, game: Game):
        dr = missions.DangerRoom(game)

        @reset_emulator_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return dr.do_missions(*args, **kwargs)

        super().__init__(button, task_func=do_missions, task_options={
            "NORMAL mode": {"times": 1, "mode": dr.MODE.NORMAL},
            "EXTREME mode": {"times": 1, "mode": dr.MODE.EXTREME}
        })


class RestartGameTask(SingleTask):

    def __init__(self, button, game: Game):
        @reset_emulator_and_logger(game=game)
        def restart_game():
            return game.restart_game()

        if button:
            super().__init__(button, restart_game, {})
        else:
            self.abort = lambda: None


class ComicCardsTask(SingleTask):

    def __init__(self, button, game: Game):
        cc = routines.ComicCards(game)

        @reset_emulator_and_logger(game=game)
        def upgrade_all_cards():
            return cc.upgrade_all_cards()

        super().__init__(button, upgrade_all_cards, {})


class CustomGearTask(SingleTaskWithOptions):

    def __init__(self, button, game: Game):
        cg = routines.CustomGear(game)

        @reset_emulator_and_logger(game=game)
        def quick_upgrade_gear(*args, **kwargs):
            return cg.quick_upgrade_gear(*args, **kwargs)

        super().__init__(button, task_func=quick_upgrade_gear, task_options={
            "Upgrade 1 gear": {"times": 1},
            "Upgrade ALL gear": {"times": 999}
        })


class DispatchMissionAcquireTask(SingleTask):

    def __init__(self, button, game: Game):
        dm = DispatchMission(game)

        @reset_emulator_and_logger(game=game)
        def acquire_all_rewards():
            return dm.acquire_all_rewards()

        super().__init__(button, acquire_all_rewards, {})


class EnhancePotentialTask(SingleTaskWithOptions):

    def __init__(self, button, game: Game):
        ep = routines.EnhancePotential(game)

        @reset_emulator_and_logger(game=game)
        def enhance_potential(*args, **kwargs):
            return ep.enhance_potential(*args, **kwargs)

        super().__init__(button, task_func=enhance_potential, task_options={
            "Use Black Anti-Matter / Phoenix Feather": {"target_success_rate": 10.0,
                                                        "material_to_use": (ep.BLACK_ANTI_MATTER,
                                                                            ep.NORN_STONE_OF_CHAOS)},
            "Use Norn Stone of Chaos / M'kraan Crystal": {"target_success_rate": 10.0,
                                                          "material_to_use": (ep.NORN_STONE_OF_CHAOS,
                                                                              ep.BLACK_ANTI_MATTER)}
        })


class ShadowlandAllFloorsTask(SingleTask):

    def __init__(self, button, game: Game):
        sl = missions.Shadowland(game)

        @reset_emulator_and_logger(game=game)
        def do_missions(*args, **kwargs):
            return sl.do_missions(*args, **kwargs)

        super().__init__(button, do_missions, {})
