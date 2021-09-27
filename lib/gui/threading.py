import sys
import traceback

from PyQt5.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot, QThreadPool

import lib.logger as logging

logger = logging.get_logger(__name__)


def trap_exc_during_debug(*args):
    """Error handler in PyQt GUI."""
    error_cls, error_exception, error_traceback = args
    error_msg = "\n".join((str(error_cls),
                           str(error_exception),
                           ''.join(traceback.format_tb(error_traceback))))
    logger.error(error_msg)


sys.excepthook = trap_exc_during_debug


class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    """Class for working with GUI thread's workers."""

    def __init__(self, func, with_progress, *args, **kwargs):
        """Class initialization.

        :param function func: function to run.
        :param with_progress: should worker emit progress into `progress_callback` signal.
        """
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        if with_progress:
            self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """Runs worker."""
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as err:
            traceback.print_exc()
            self.signals.error.emit((err, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


class ThreadPool:
    """Class for working with GUI threads."""

    def __init__(self):
        """Class initialization."""
        self.thread_pool = QThreadPool()

    def run_thread(self, func, on_finish=None, on_progress=None, on_error=None, on_result=None, with_progress=False):
        """Runs worker in thread.

        :param function func: function to run.
        :param function | list[function] on_finish: callbacks for 'finished' signal.
        :param function | list[function] on_progress: callbacks for 'progress' signal.
        :param function | list[function] on_error: callbacks for 'error' signal.
        :param function | list[function] on_result: callbacks for 'result' signal.
        :param bool with_progress: connect `progress` callback to worker or not.

        :return thread's worker.
        :rtype: lib.gui.threading.Worker
        """

        def connect_to_signal(signal: pyqtSignal, callbacks):
            if not callbacks:
                return
            if callable(callbacks):
                callbacks = [callbacks]
            for callback in callbacks:
                signal.connect(callback)

        worker = Worker(func=func, with_progress=with_progress)
        connect_to_signal(signal=worker.signals.finished, callbacks=on_finish)
        connect_to_signal(signal=worker.signals.progress, callbacks=on_progress)
        connect_to_signal(signal=worker.signals.error, callbacks=on_error)
        connect_to_signal(signal=worker.signals.result, callbacks=on_result)
        self.thread_pool.start(worker)
        return worker
