from functools import wraps
from time import sleep

from PyQt5.QtCore import QTimer, pyqtSignal, QObject
from PyQt5.QtGui import QIcon, QImage, QPixmap
from PyQt5.QtWidgets import QMenu


def set_default_icon(window, path="icon.ico"):
    """Sets default icon for window.

    :param PyQt5.QtWidgets.QWidget.QWidget window: window to set the icon.
    :param path: path to icon's image.
    """
    window.setWindowIcon(QIcon(path))


class ButtonSignals(QObject):
    """GUI signals for button."""

    first_state = pyqtSignal()
    second_state = pyqtSignal()


class TwoStateButton:
    """Class for working with one button that has two states."""

    class State:
        Zero = 0
        First = 1
        Second = 2

    def __init__(self, button):
        """Class initialization.

        :param PyQt5.QtWidgets.QPushButton.QPushButton button: instance of button.
        """
        self.button = button
        self.state = TwoStateButton.State.Zero
        self.signals = ButtonSignals()
        self.first_state_funcs = []
        self.second_state_funcs = []
        self.first_state_text = self.button.text()
        self.second_state_text = "Stop"
        self.set_first_state()

    def set_first_state_text(self, text):
        """Sets text for first state.

        :param str text: text of the button in first state.
        """
        self.first_state_text = text

    def set_second_state_text(self, text):
        """Sets text for second state.

        :param str text: text of the button in second state.
        """
        self.second_state_text = text

    def connect_first_state(self, func, *args, **kwargs):
        """Connects function to first state.

        :param function func: function to connect.
        """

        @wraps(func)
        def proxy_func():
            return func(*args, **kwargs)

        self.first_state_funcs.append(proxy_func)
        if self.state == TwoStateButton.State.First:
            self.button.clicked.connect(proxy_func)

    def connect_second_state(self, func, *args, **kwargs):
        """Connects function to second state.

        :param function func: function to connect.j
        """

        @wraps(func)
        def proxy_func():
            return func(*args, **kwargs)

        self.second_state_funcs.append(proxy_func)
        if self.state == TwoStateButton.State.Second:
            self.button.clicked.connect(proxy_func)

    def set_first_state(self):
        """Sets button to first state and reconnect functions."""
        if self.state == TwoStateButton.State.First:
            return
        self.state = TwoStateButton.State.First
        self.signals.first_state.emit()
        self.button.setText(self.first_state_text)
        for func in self.second_state_funcs:
            try_to_disconnect(self.button.clicked, func)
        for func in self.first_state_funcs:
            self.button.clicked.connect(func)

    def set_second_state(self):
        """Sets button to second state and reconnect functions."""
        if self.state == TwoStateButton.State.Second:
            return
        self.state = TwoStateButton.State.Second
        self.signals.second_state.emit()
        self.button.setText(self.second_state_text)
        for func in self.first_state_funcs:
            try_to_disconnect(self.button.clicked, func)
        for func in self.second_state_funcs:
            self.button.clicked.connect(func)

    def change_state(self):
        """Changes button's state."""
        if self.state == TwoStateButton.State.First:
            self.set_second_state()
        elif self.state == TwoStateButton.State.Second:
            self.set_first_state()

    def add_action(self, action_name, action_func):
        """Adds action menu to button as first state.

        :param str action_name: name of action.
        :param function action_func: function to execute.
        """
        menu = self.button.menu() if self.button.menu() else QMenu()
        action = menu.addAction(action_name)
        action.triggered.connect(action_func)
        for proxy_func in self.first_state_funcs:
            action.triggered.connect(proxy_func)
        self.button.setMenu(menu)


class Timer:
    """Class for working with GUI timers."""

    UPDATE_TIMER_MS = 150  # update timer (milliseconds)

    def __init__(self):
        """Class initialization."""
        self._update_timer = QTimer()

    def set_timer(self, func, timer_ms=UPDATE_TIMER_MS):
        """Sets function to timer.

        :param function func: function caller.
        :param int timer_ms: time in ms.
        """
        self._update_timer.timeout.connect(func)
        self._update_timer.start(timer_ms)


def safe_process_stop(func):
    """Decorator for safe process stopping."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except AttributeError:
            sleep(1)
            return wrapper(*args, **kwargs)

    return wrapper


def try_to_disconnect(signal, func=None):
    """Tries to disconnect function from signal.
    If there is nothing to disconnect then simply skips exception.
    """
    try:
        if func is not None:
            signal.disconnect(func)
        else:
            signal.disconnect()
    except TypeError:
        pass


def screen_to_gui_image(screen):
    """Converts screen image to PyQt image.

    :param numpy.ndarray screen: screen image.

    :rtype: PyQt5.QtGui.QPixmap.QPixmap
    """
    height, width, channel = screen.shape
    return QPixmap(QImage(screen.data, width, height, 3 * width, QImage.Format_RGB888))


def reset_emulator_and_logger(game):
    """Resets emulator screen and set file logger to existing file.

    :param lib.game.game.Game game: instance of game.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import lib.logger as logging
            if hasattr(game, "file_logger_name") and game.file_logger_name:
                logging.create_file_handler(file_name=game.file_logger_name)
            if not game.emulator.initialized:
                name = func.__name__ if not func.__closure__ else func.__closure__[0].cell_contents.__module__
                logging.get_logger(name).error(f"Can't find NoxWindow with name {game.emulator.name}.")
                return
            # Screen will never unlock itself inside side-process
            game.emulator.screen_locked = False
            # Clear `screen_elements` from EmulatorImageSource if it exists
            if hasattr(game.emulator, 'screen_elements') and game.emulator.screen_elements is not None:
                game.emulator.screen_elements[:] = []
            try:
                return func(*args, **kwargs)
            except BaseException as err:
                import traceback
                logging.root.error(f"{err}\n{traceback.format_exc()}")

        return wrapper

    return decorator
