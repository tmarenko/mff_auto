from lib.gui.helper import Timer


class QTextEditFileLogger(Timer):
    """Class for working with file logging in GUI."""

    def __init__(self, all_logger_widget, info_logger_widget, error_logger_widget, log_file):
        """Class initialization.

        :param PyQt5.QtWidgets.QPlainTextEdit.QPlainTextEdit all_logger_widget: widget to write all log's text.
        :param PyQt5.QtWidgets.QPlainTextEdit.QPlainTextEdit info_logger_widget: widget to write INFO logs.
        :param PyQt5.QtWidgets.QPlainTextEdit.QPlainTextEdit error_logger_widget: widget to write ERROR/WARNING logs.
        :param str log_file: name of the log-file to read from.
        """
        super().__init__()
        self.all_widget = all_logger_widget
        self.info_widget = info_logger_widget
        self.error_widget = error_logger_widget
        self.set_timer(self.update_text)
        self.log_file = log_file
        self._old_txt_len = 0

    def update_text(self):
        """Updates text on the widget."""

        def update_by_filter(all_text, widget, text_filters):
            new_text = "\n".join([line for line in all_text.split("\n") if any(s in line for s in text_filters)])
            widget.setPlainText(new_text)
            widget.verticalScrollBar().setValue(widget.verticalScrollBar().maximum())

        with open(self.log_file, "r", encoding='utf-8') as log_file:
            text = log_file.read()
            text_len = len(text)
            if text_len > self._old_txt_len:
                self._old_txt_len = text_len
                self.all_widget.setPlainText(text)
                self.all_widget.verticalScrollBar().setValue(self.all_widget.verticalScrollBar().maximum())
                update_by_filter(all_text=text, widget=self.info_widget, text_filters=("- INFO - ",))
                update_by_filter(all_text=text, widget=self.error_widget, text_filters=("- ERROR - ", "- WARNING -"))
