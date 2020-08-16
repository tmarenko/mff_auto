from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt
from lib.gui.helper import Timer


class ScreenImageLabel(Timer):
    """Class for updating GUI label with game screen image."""

    FULL_SCREEN_RECT = (0, 0, 1, 1)

    def __init__(self, widget, player):
        """Class initialization.

        :param QtWidgets.QLabel widget: label widget for image.
        :param lib.player player: instance of game player.
        """
        super().__init__()
        self.widget = widget
        self.player = player
        self.size = self.widget.size()
        self.set_timer(self.update_image)

    def update_image(self):
        """Update image from player and handle player resize."""
        self.player.update_windows()
        if not self.player.hwnd:
            return
        # TODO: try to use last frame
        image = self.player.get_screen_image(rect=self.FULL_SCREEN_RECT)
        height, width, channel = image.shape
        pix_map = QPixmap(QImage(image.data, width, height, 3 * width, QImage.Format_RGB888))
        self.widget.setPixmap(pix_map.scaled(self.size, Qt.IgnoreAspectRatio, Qt.SmoothTransformation))
