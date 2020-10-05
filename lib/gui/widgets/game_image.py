from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from lib.gui.helper import Timer, screen_to_gui_image
from lib.game.ui import Rect


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
        self.widget.mousePressEvent = self.screen_click_event
        self.player = player
        self.set_timer(self.update_image)
        self.scaled_width, self.scaled_height = None, None

    def update_image(self):
        """Update image from player and handle player resize."""
        if not self.player.initialized:
            self.player.update_windows()
            return
        self.player.update_windows_rect()
        screen = self.player.get_screen_image()
        pix_map = screen_to_gui_image(screen)
        scale_pix_map = pix_map.scaled(self.widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.scaled_width, self.scaled_height = scale_pix_map.width(), scale_pix_map.height()
        self.widget.setPixmap(scale_pix_map)

    def screen_click_event(self, event):
        """Click event on screen image."""
        if not self.player.initialized:
            return
        x, y = self.translate_coordinate_from_label_to_screen(x=event.pos().x(), y=event.pos().y())
        if x and y:
            click_rect = Rect(x / self.scaled_width, y / self.scaled_height,
                              x / self.scaled_width, y / self.scaled_height)
            self.player.click_button(click_rect)

    def translate_coordinate_from_label_to_screen(self, x, y):
        """Calculate coordinates inside game's screen label and translate them to scaled screen coordinates.

        :param x: X coordinate.
        :param y: Y coordinate.
        :return: X and Y coordinate according to actual game's screen.
        """
        def get_coordinate_inside_screen(point, screen_length, scaled_length):
            if screen_length > scaled_length:
                diff_length = screen_length - scaled_length
                if point > diff_length / 2 and point - diff_length / 2 < scaled_length:
                    return point - diff_length / 2

        label_width, label_height = self.widget.size().width(), self.widget.size().height()
        if label_width > self.scaled_width:
            x = get_coordinate_inside_screen(point=x, screen_length=label_width, scaled_length=self.scaled_width)
        if label_height > self.scaled_height:
            y = get_coordinate_inside_screen(point=y, screen_length=label_height, scaled_length=self.scaled_height)

        return x, y
