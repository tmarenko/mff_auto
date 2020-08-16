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
        """Class initialization."""
        super(Worker, self).__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        if with_progress:
            self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        """Run worker."""
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

    def run_thread(self, target, with_progress=False):
        """Run thread.

        :param target: target to run.
        :param bool with_progress: connect `progress` callback to worker or not.
        :return Worker worker: thread's worker.
        """
        worker = Worker(func=target, with_progress=with_progress)
        self.thread_pool.start(worker)
        return worker
