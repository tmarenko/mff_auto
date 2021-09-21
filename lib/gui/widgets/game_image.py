from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy
from lib.gui.helper import Timer, screen_to_gui_image
from lib.game.ui.general import Rect, UIElement
import lib.logger as logging
import gc

logger = logging.get_logger(__name__)


class ScreenImageLabel(Timer):
    """Class for updating GUI label with game screen image."""

    click_ui = UIElement(name="GUI click")

    def __init__(self, widget, emulator):
        """Class initialization.

        :param PyQt5.QtWidgets.QLabel.QLabel widget: label widget for image.
        :param lib.emulators.android_emulator.AndroidEmulator emulator: instance of game emulator.
        """
        super().__init__()
        self.widget = widget
        self.widget.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.widget.mousePressEvent = self.screen_click_event
        self.emulator = emulator
        self.set_timer(self.update_image)
        self.scaled_width, self.scaled_height = None, None
        self.get_image_func = self.emulator.get_screen_image

    def update_image(self):
        """Updates image from emulator and handle emulator resize."""
        if not self.emulator.initialized:
            self.emulator.update_handlers()
            return
        self.emulator.update_window_rectangles()
        screen = self.get_image_func()
        pix_map = screen_to_gui_image(screen)
        scale_pix_map = pix_map.scaled(self.widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.scaled_width, self.scaled_height = scale_pix_map.width(), scale_pix_map.height()
        self.widget.setPixmap(scale_pix_map)
        gc.collect()  # Temp images easily can take over 500 MB of RAM

    def screen_click_event(self, event):
        """Click event on screen image."""
        if not self.emulator.initialized:
            return
        x, y = self.translate_coordinate_from_label_to_screen(x=event.pos().x(), y=event.pos().y())
        if x and y:
            click_rect = Rect(x / self.scaled_width, y / self.scaled_height,
                              x / self.scaled_width, y / self.scaled_height)
            self.click_ui.button_rect = click_rect
            logger.debug(f"Sending clicking event by coordinates {(x,y)}; rect: {click_rect.value}")
            self.emulator.click_button(self.click_ui)

    def translate_coordinate_from_label_to_screen(self, x, y):
        """Calculates coordinates inside game's screen label and translate them to scaled screen coordinates.

        :param float x: X coordinate.
        :param float y: Y coordinate.
        :return: X and Y coordinate according to actual game's screen.
        :rtype: tuple[float, float]
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
