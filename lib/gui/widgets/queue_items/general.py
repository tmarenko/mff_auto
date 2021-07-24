from PyQt5.QtCore import Qt
from lib.gui.helper import reset_emulator_and_logger


class GameMode:
    """Class for working with game mode settings."""

    class ModeSetting:
        """Class for working with available settings for a game mode."""

        class Checkbox:

            def __init__(self, text, initial_state=True):
                from PyQt5.QtWidgets import QCheckBox
                self.widget = QCheckBox(text=text)
                self.widget.setCheckState(Qt.Checked if initial_state else Qt.Unchecked)

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                row_index = layout.rowCount()
                layout.setWidget(row_index, QFormLayout.LabelRole, self.widget)

            @property
            def value(self):
                return self.widget.isChecked()

            @value.setter
            def value(self, val):
                self.widget.setCheckState(Qt.Checked if val else Qt.Unchecked)

        class Spinbox:

            def __init__(self, text, initial_value=1, min=1, max=99):
                from PyQt5.QtWidgets import QSpinBox, QLabel
                self.widget_spinbox = QSpinBox()
                self.widget_label = QLabel(text=text)
                self.widget_spinbox.setMinimum(min)
                self.widget_spinbox.setMaximum(max)
                self.widget_spinbox.setValue(initial_value)

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                row_index = layout.rowCount()
                layout.setWidget(row_index, QFormLayout.LabelRole, self.widget_label)
                layout.setWidget(row_index, QFormLayout.SpanningRole, self.widget_spinbox)

            @property
            def value(self):
                return self.widget_spinbox.value()

            @value.setter
            def value(self, val):
                self.widget_spinbox.setValue(val)

        class Combobox:

            def __init__(self, text, values_dict):
                from PyQt5.QtWidgets import QComboBox, QLabel
                self.widget_combobox = QComboBox()
                self.widget_combobox.addItems(values_dict.keys())
                self.widget_label = QLabel(text=text)
                self.values_dict = values_dict

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                row_index = layout.rowCount()
                layout.setWidget(row_index, QFormLayout.LabelRole, self.widget_label)
                layout.setWidget(row_index, QFormLayout.SpanningRole, self.widget_combobox)

            @property
            def value(self):
                return self.values_dict[self.widget_combobox.currentText()]

            @value.setter
            def value(self, val):
                key = [k for k, v in self.values_dict.items() if v == val]
                self.widget_combobox.setCurrentText(key[0])

        class MultiCheckbox:

            def __init__(self, values_dict, initial_state=True):
                from PyQt5.QtWidgets import QCheckBox
                self.values_dict = values_dict
                self.widgets = [QCheckBox(text=text) for text in self.values_dict.keys()]
                for widget in self.widgets:
                    widget.setCheckState(Qt.Checked if initial_state else Qt.Unchecked)

            def add_to_layout(self, layout):
                from PyQt5.QtWidgets import QFormLayout
                for widget in self.widgets:
                    row_index = layout.rowCount()
                    layout.setWidget(row_index, QFormLayout.LabelRole, widget)

            @property
            def value(self):
                return [self.values_dict[widget.text()] for widget in self.widgets if widget.isChecked()]

            @value.setter
            def value(self, values):
                for widget in self.widgets:
                    if widget.text() in values:
                        widget.setCheckState(Qt.Checked)
                    else:
                        widget.setCheckState(Qt.Unchecked)

        def __init__(self, setting_type, setting_key, **kwargs):
            """Class initialization.

            :param setting_type: type of GUI element of setting.
            :param setting_key: setting's key (kwarg for game mode).
            :param kwargs: possible kwargs for GUI element of setting.
            """
            self.setting_type = setting_type
            self.setting_key = setting_key
            self.kwargs = kwargs
            self.gui_element = None
            self._value = None

        def render_gui(self):
            """Render GUI element of setting."""
            self.gui_element = self.setting_type(**self.kwargs)
            return self.gui_element

        @property
        def value(self):
            """Value of setting."""
            if self.gui_element:
                self._value = self.gui_element.value
            return {self.setting_key: self._value}

        @value.setter
        def value(self, value):
            """Set value of setting."""
            if not self.gui_element:
                self.render_gui()
            if value is not None:
                self._value = value
                self.gui_element.value = value

    def __init__(self, game, mode_name, mode_module, mode_name_formatted=None):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        :param str mode_name: name of mode.
        :param mode_module: class or module of game mode.
        """
        self.game = game
        self.mode_name = mode_name
        self.mode_module = mode_module
        self.mode_name_formatted = mode_name_formatted if mode_name_formatted else mode_name.title()
        self.mode_settings = []

    def render_executable(self):
        """Render function and settings for game mode."""
        game_mode = self.mode_module(self.game)

        @reset_emulator_and_logger(game=self.game)
        def do_missions(*args, **kwargs):
            return game_mode.do_missions(*args, **kwargs)

        return do_missions, self.render_execution_params()

    def render_gui_elements(self, parent_layout):
        """Render all GUI elements of all mode settings.

        :param parent_layout: parent layout for new created elements.
        """
        for setting in self.mode_settings:
            gui_element = setting.render_gui()
            gui_element.add_to_layout(layout=parent_layout)
            if setting.setting_key == "farm_shifter_bios" and not self.game.emulator.restartable:
                gui_element.widget.setEnabled(False)

        # Make "All stages" checkbox and "Stages" spinbox relatable
        all_stages = [setting.gui_element.widget for setting in self.mode_settings if
                      setting.setting_key == "all_stages"]
        stages = [(setting.gui_element.widget_label, setting.gui_element.widget_spinbox) for setting in
                  self.mode_settings if setting.setting_key == "times"]
        if all_stages and stages:
            all_stages_check_box, stages_label, stages_spin_box = all_stages[0], stages[0][0], stages[0][1]

            def all_stages_changed():
                """'All stages' checkbox event when value is changed"""
                checked = all_stages_check_box.isChecked()
                stages_label.setEnabled(not checked)
                stages_spin_box.setEnabled(not checked)

            all_stages_changed()
            all_stages_check_box.stateChanged.connect(all_stages_changed)

    def render_execution_params(self):
        """Returns execution parameters for game mode."""
        params = {}
        for setting in self.mode_settings:
            params.update(setting.value)
        return params

    def apply_params(self, params):
        """Apply parameters to mode's settings.

        :param params: dictionary of parameters.
        """
        for setting in self.mode_settings:
            if setting.setting_key in params.keys():
                setting.value = params[setting.setting_key]


class Action(GameMode):
    """Class for working with non-mission actions."""

    def __init__(self, game, action_name, action_executable):
        """Class initialization.

        :param lib.game.game.Game game: instance of game.
        :param str action_name: name of action.
        :param action_executable: function to execute.
        """
        super().__init__(game, action_name, None)
        self.action_executable = action_executable

    def render_executable(self):
        """Render function and settings for action."""
        action_executable = self.action_executable  # Only function without class reference (GUI cannot be pickled)

        @reset_emulator_and_logger(game=self.game)
        def action(*args, **kwargs):
            return action_executable(*args, **kwargs)

        return action, {**self.render_execution_params(), "action": True}


class Event(Action):
    """Class for working with in-game mission events."""

    def render_executable(self):
        """Render function and settings for event."""
        event_executable = self.action_executable  # Only function without class reference (GUI cannot be pickled)

        @reset_emulator_and_logger(game=self.game)
        def event(*args, **kwargs):
            return event_executable(*args, **kwargs)

        return event, {**self.render_execution_params(), "event": True}
