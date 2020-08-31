from lib.gui.helper import Timer
import lib.logger as logging


class QTextEditFileLogger(Timer):
    """Class for working with file logging in GUI."""

    def __init__(self, logger_widget):
        """Class initialization.

        :param QPlainTextEdit logger_widget: widget to write log's text.
        """
        super().__init__()
        self.widget = logger_widget
        self.scrollbar = self.widget.verticalScrollBar()
        self.set_timer(self.update_text)
        self.log_file = logging.fh.baseFilename
        self._old_txt_len = 0

    def update_text(self):
        """Update text on the widget."""
        with open(self.log_file, "r", encoding='utf-8') as log_file:
            text = log_file.read()
            text_len = len(text)
            if text_len > self._old_txt_len:
                self._old_txt_len = text_len
                self.widget.setPlainText(text)
                self.scrollbar.setValue(self.scrollbar.maximum())
