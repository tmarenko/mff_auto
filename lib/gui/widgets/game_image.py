from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from lib.gui.helper import Timer, screen_to_gui_image


class ScreenImageLabel(Timer):
    """Class for updating GUI label with game screen image."""

    def __init__(self, widget, player):
        """Class initialization.

        :param QtWidgets.QLabel widget: label widget for image.
        :param lib.player player: instance of game player.
        """
        super().__init__()
        self.widget = widget
        self.widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.player = player
        self.set_timer(self.update_image)

    def update_image(self):
        """Update image from player and handle player resize."""
        self.player.update_windows()
        if not self.player.initialized:
            return
        screen = self.player.get_screen_image()
        pix_map = screen_to_gui_image(screen)
        self.widget.setPixmap(pix_map.scaled(self.widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
