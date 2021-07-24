from PyQt5.QtWidgets import QListWidgetItem, QDialog, QToolButton, QMenu
from PyQt5.QtCore import Qt
import lib.gui.designes.queue_editor_window as design
from lib.gui.helper import set_default_icon
from lib.gui.widgets.queue_items import GameMode, get_actions, get_events, get_missions, get_missions_dict
import lib.logger as logging

logger = logging.get_logger(__name__)


class QueueItem(QListWidgetItem):
    """Class for working with queue item as a widget."""

    def __init__(self, func, parameters, mode_name, mode_name_formatted=None):
        """Class initialization.

        :param func: function to execute in queue.
        :param parameters: function's parameters.
        :param str mode_name: name of game mode.
        """
        super().__init__()
        self.func = func
        self.parameters = parameters
        self.execution_parameters = self.clear_parameters()
        self.mode_name = mode_name
        self.mode_name_formatted = mode_name_formatted if mode_name_formatted else mode_name.title()
        self.setText(self.name)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Checked)
        self.setToolTip(self.name)

    def clear_parameters(self):
        parameters = self.parameters.copy()
        if "all_stages" in parameters.keys():
            if parameters["all_stages"] is True:
                parameters.pop("times")  # Remove `times` kwarg if doing All stages
            parameters.pop("all_stages")  # Remove `all_stages` kwarg anyway
        if "action" in parameters.keys():
            parameters.pop("action")
        if "event" in parameters.keys():
            parameters.pop("event")
        return parameters

    def get_executor(self):
        """Get function with parameters to execute."""
        if self.is_checked:
            return self.func, self.execution_parameters
        return None, None

    @property
    def is_checked(self):
        """Is item checked to execute."""
        return self.checkState() == Qt.Checked

    def set_checked(self, checked=True):
        """Set checked state to item."""
        state = Qt.Checked if checked else Qt.Unchecked
        self.setCheckState(state)

    @property
    def name(self):
        """Get queue item's name for GUI."""
        additional_text = ''
        if self.parameters.get("action"):
            hour_offset = self.parameters.get("hour_offset")
            if hour_offset:
                additional_text += f"[-{hour_offset} hour(s)]"
            return f"[Action] {self.mode_name.title()} {additional_text}"
        if self.parameters.get("event"):
            return f"[Event] {self.mode_name.title()} {additional_text}"
        farm_bios = self.parameters.get("farm_shifter_bios")
        battle = self.parameters.get("battle")
        mission_mode = self.parameters.get("mode")
        times = self.parameters.get("times")
        if farm_bios:
            additional_text += " [Bio]"
        if battle:
            additional_text += f" [{battle.replace('_', ' ').title()}]"
        if mission_mode:
            additional_text += f" [{mission_mode.replace('_', ' ').title()}]"
        if times and not self.parameters.get("all_stages"):
            additional_text += f" [{times} stages]"
        else:
            additional_text += " [All stages]"
        return f"{self.mode_name.title()} -{additional_text}"


class QueueItemEditor(QDialog, design.Ui_Dialog):
    """Class for working with editing elements of queue list."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        """
        super().__init__()
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())
        set_default_icon(window=self)
        self.game = game
        self.setWindowModality(Qt.ApplicationModal)
        self.events = get_events(game)
        self.actions = get_actions(game)
        self.missions = get_missions(game)
        self.modes = [*self.events, *self.actions, *self.missions]
        self.queue_item = None
        self.current_mode = None
        self.editor_button_box.accepted.connect(self.render_queue_item)

        menu_dict = {
            "[ACTIONS]": self.actions,
            "[EVENTS]": self.events,
            **get_missions_dict(self.missions)
        }
        menu = QMenu()
        self.populate_menu(menu=menu, dictionary=menu_dict)
        self.select_mode_tool_button.setPopupMode(QToolButton.InstantPopup)
        self.select_mode_tool_button.setMenu(menu)

    def clear_form_layout(self):
        """Clear Form Layout from mode's GUI elements."""
        for _ in range(self.formLayout.count()):
            from PyQt5.QtWidgets import QWidgetItem
            item = self.formLayout.itemAt(0)
            if isinstance(item, QWidgetItem):
                widget = item.widget()
                self.formLayout.removeWidget(widget)
                widget.setParent(None)

    def select_mode(self, mode):
        """Select GameMode from Tool Button Selector."""
        self.select_mode_tool_button.setText(mode.mode_name)
        self.current_mode = mode
        self.clear_form_layout()
        self.current_mode.render_gui_elements(parent_layout=self.formLayout)

    def populate_menu(self, menu, dictionary):
        """Populate Selector's menu with dictionary of game modes.

        :param menu: menu to populate.
        :param dictionary: dictionary of game modes.
        """

        def add_mode_to_menu(menu_obj, mode):
            action = menu_obj.addAction(mode.mode_name_formatted)
            action.triggered.connect(lambda: self.select_mode(mode))

        for menu_key, menu_val in dictionary.items():
            if isinstance(menu_val, list):
                sub_menu = menu.addMenu(menu_key)
                for value in menu_val:
                    if isinstance(value, GameMode):
                        add_mode_to_menu(sub_menu, value)
            if isinstance(menu_val, dict):
                sub_menu = menu.addMenu(menu_key)
                self.populate_menu(sub_menu, menu_val)
            if isinstance(menu_val, GameMode):
                add_mode_to_menu(menu, menu_val)

    @staticmethod
    def from_result_item(game, queue_item):
        """Create editor from queue item.

        :param lib.game.game.Game game: instance of game.
        :param QueueItem queue_item: queue item.
        """
        editor = QueueItemEditor(game)
        editor.queue_item = queue_item
        mode = [mode for mode in editor.modes if mode.mode_name == queue_item.mode_name]
        if mode:
            editor.current_mode = mode[0]
            editor.select_mode(editor.current_mode)
            editor.current_mode.apply_params(queue_item.parameters)
            return editor
        logger.error(f"Error during creating Item Editor from item instance for mode: {queue_item.mode_name}.")

    @staticmethod
    def from_settings(game, settings):
        """Create editor from JSON-settings similar to 'GameMode.QueueItemSettings'.

        :param lib.game.game.Game game: instance of game.
        :param dict settings: dictionary of settings.
        """
        editor = QueueItemEditor(game)
        mode = [mode for mode in editor.modes if mode.mode_name == settings.get("mode_name")]
        if mode:
            editor.current_mode = mode[0]
            editor.current_mode.apply_params(settings)
            return editor
        logger.error(f"Error during creating Item Editor from item instance with settings: {settings}.")

    def render_queue_item(self):
        """Render queue item."""
        if self.current_mode:
            function, parameters = self.current_mode.render_executable()
            self.queue_item = QueueItem(func=function, parameters=parameters, mode_name=self.current_mode.mode_name,
                                        mode_name_formatted=self.current_mode.mode_name_formatted)
            return self.queue_item
