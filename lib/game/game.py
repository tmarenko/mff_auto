import re

import lib.logger as logging
from lib.functions import wait_until, is_strings_similar, r_sleep, confirm_condition_by_time
from lib.game import ui
from lib.game.data.game_modes import game_modes
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)

cur_slash_max_regexp = re.compile(r"(\d*) ?/ ?(\d*)")
KEY_PAGE_UP = 33


class GameMode:
    """Class for working with game modes."""

    def __init__(self, name, stages=0, max_stages=0, ui_button=None, ui_board=None):
        """Class initialization.

        :param str name: name of game mode. See `lib.game.data.game_modes.game_modes` variable for reference.
        :param int stages: current number of completed stages (missions) in this game mode.
        :param int max_stages: max number of available stages (missions) to complete in this game mode.
        :param ui.UIElement ui_button: button from Content Status Board to enter in this game mode.
        :param tuple[float, float, float, float] ui_board: rectangle that represents Content Status Board #1 or #2.
            Needed to determine whether the Content Status Board should be dragged in order to access this game mode.
        """
        self.name = name
        self.stages = stages
        self.max_stages = max_stages
        self.ui_button = ui_button
        self.ui_board = ui_board


class Game(Notifications):
    """Class for working with main game methods."""

    ACQUIRE_HEROIC_QUEST_REWARDS = False

    def __init__(self, emulator, user_name=None):
        """Class initialization.

        :param lib.emulators.android_emulator.AndroidEmulator emulator: instance of game emulator.
        :param str user_name: game user name.
        """
        self.emulator = emulator
        self._apply_decorators()
        self._mode_names = game_modes
        self._user_name = user_name
        self._current_energy, self._energy_max = 0, 0
        self._gold = 0
        self._boost = 0
        self.timeline_team = 1
        self.mission_team = 1
        self._modes = {}
        super().__init__(self)

    def _do_after_loading_circle_decorator(self, func):
        """Decorator that waits when there is loading circle on screen.

        :param function func: function that should not be executed when loading circle is on screen.
        """

        def wrapped(*args, **kwargs):
            if self.is_loading_circle():
                r_sleep(1)
            return func(*args, **kwargs)

        return wrapped

    def _handle_network_error_decorator(self, func):
        """Decorator that detects network error notifications.

        :param function func: function that should not be executed when network error notifications is on screen.
        """

        def wrapped(*args, **kwargs):
            if self.close_network_error_notification():
                r_sleep(1)
            return func(*args, **kwargs)

        return wrapped

    def _apply_decorators(self):
        """Applies decorators for current Android Emulator."""
        # Store normal function to prevent recursive usage
        self._old_click_button = self.emulator.click_button
        self._old_is_ui_element_on_screen = self.emulator.is_ui_element_on_screen
        # Apply network decorator
        # TODO: restore as an optional setting
        # self.emulator.click_button = self._handle_network_error_decorator(self.emulator.click_button)
        # self.emulator.is_ui_element_on_screen = self._handle_network_error_decorator(
        #     self.emulator.is_ui_element_on_screen)
        # self.emulator.is_image_on_screen = self._handle_network_error_decorator(self.emulator.is_image_on_screen)
        # Apply loading decorator
        self.emulator.click_button = self._do_after_loading_circle_decorator(self.emulator.click_button)
        self.emulator.is_ui_element_on_screen = self._do_after_loading_circle_decorator(
            self.emulator.is_ui_element_on_screen)
        self.emulator.is_image_on_screen = self._do_after_loading_circle_decorator(self.emulator.is_image_on_screen)

    @staticmethod
    def get_current_and_max_values_from_text(text, regexp=cur_slash_max_regexp):
        """Gets current and max value from text by regular expression.
        For example, for `15/30` will return (15, 30)

        :param str text: text from which the values will be extracted.
        :param typing.Pattern regexp: compiled regular expression used for extraction.

        :return: current and max values in the text.
        :rtype: tuple[int, int]
        """
        result = regexp.findall(text)
        try:
            current_value = 0 if not result else int(result[0][0])
            max_value = 0 if not result else int(result[0][1])
        except ValueError:
            current_value = 0
            max_value = 0
        return current_value, max_value

    def _main_panel_visible(self):
        """Checks if gold icon is seen on the screen. Usually it means that in-game main panel is visible."""
        return self.emulator.is_image_on_screen(ui.GOLD_ICON)

    @property
    def user_name(self):
        """Property for player's username.

        :rtype: str
        """
        if not self._user_name:
            if not self.is_main_menu():
                self.go_to_main_menu()
            self._user_name = self.emulator.get_screen_text(ui.USER_NAME)
        return self._user_name

    @property
    def energy(self):
        """Property for in-game energy bar's value.

        :rtype: int
        """
        if self._main_panel_visible():
            energy = self.emulator.get_screen_text(ui.ENERGY).replace(",", "")
            self._current_energy, self._energy_max = self.get_current_and_max_values_from_text(energy)
        return self._current_energy

    @property
    def energy_max(self):
        """Property for max value of energy counter.

        :rtype: int
        """
        if self._main_panel_visible():
            energy = self.emulator.get_screen_text(ui.ENERGY).replace(",", "")
            self._current_energy, self._energy_max = self.get_current_and_max_values_from_text(energy)
        return self._energy_max

    @property
    def gold(self):
        """Property for in-game gold value.

        :rtype: int
        """
        if self._main_panel_visible():
            self._gold = self.emulator.get_screen_text(ui.GOLD).replace(",", "")
        return self._gold

    @property
    def boost(self):
        """Property for in-game boost points' value.

        :rtype: int
        """
        if self._main_panel_visible():
            self._boost = self.emulator.get_screen_text(ui.BOOST).replace(",", "")
        return self._boost

    def get_all_modes(self):
        """Gets all game modes from Content Status Board."""
        if not self._modes:
            self.find_mode_on_content_status_board("ALL")

    def get_mode(self, name):
        """Gets game mode by name from `self._modes`.
        If game mode isn't in `self._modes` then tries to find it from Content Status Board.

        :param str name: name of the game mode.

        :rtype: GameMode
        """
        if not self._modes or name not in self._modes:
            self.find_mode_on_content_status_board(mode_name=name)
            for empty_mode_name in [m_name for m_name in self._mode_names if m_name not in self._modes]:
                self._modes[empty_mode_name] = GameMode(name=empty_mode_name)
        return self._modes[name]

    def update_mode(self, mode):
        """Updates GameMode object.
        This way object will be shared between processes if `self._modes` was created by multiprocessing manager.

        :param GameMode mode: game mode object to update.
        """
        self._modes[mode.name] = mode

    def clear_modes(self):
        """Clears all game modes information."""
        self._modes.clear()

    def set_timeline_team(self, team_number):
        """Sets team for Timeline Battles.

        :param int team_number: team number to set.
        """
        if team_number < 1 or team_number > 5:
            return logger.error("Timeline team: Team number should be between 1 and 5.")
        self.timeline_team = team_number

    def set_mission_team(self, team_number):
        """Sets team for usual missions.

        :param int team_number: team number to set.
        """
        if team_number < 1 or team_number > 5:
            return logger.error("Mission team: Team number should be between 1 and 5.")
        self.mission_team = team_number

    def is_main_menu(self):
        """Checks if main menu screen is opened by looking for `TEAM` and `STORE` labels."""
        return self.emulator.is_ui_element_on_screen(ui.TEAM) and self.emulator.is_ui_element_on_screen(ui.STORE)

    def is_loading_circle(self):
        """Checks if loading circle is on screen. Looks for colors in special places."""
        loading_circle_rects = [ui.LOADING_CIRCLE_1.image_rect, ui.LOADING_CIRCLE_2.image_rect,
                                ui.LOADING_CIRCLE_3.image_rect, ui.LOADING_CIRCLE_4.image_rect,
                                ui.LOADING_CIRCLE_5.image_rect, ui.LOADING_CIRCLE_6.image_rect,
                                ui.LOADING_CIRCLE_7.image_rect, ui.LOADING_CIRCLE_8.image_rect]
        return self.emulator.is_color_similar(color=ui.LOADING_CIRCLE_1.image_color, rects=loading_circle_rects)

    def go_to_main_menu(self):
        """Goes to main menu screen."""
        if not self.is_main_menu():
            if self.emulator.is_image_on_screen(ui.HOME):
                self.emulator.click_button(ui.HOME)
                self.close_ads()
            else:
                logger.error("Can't go to main menu, HOME button is missing.")
        return self.is_main_menu()

    def go_to_content_status_board(self):
        """Goes to Content Status Board screen."""
        self.go_to_main_menu()
        if wait_until(self.is_main_menu):
            self.emulator.click_button(ui.CONTENT_STATUS_BOARD_BUTTON)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CONTENT_STATUS_BOARD_LABEL)

    def find_mode_on_content_status_board(self, mode_name):
        """Finds game mode on Content Status Board.

        :param str mode_name: name of game mode.
        """
        if not self.go_to_content_status_board():
            return logger.error("Failed to open Content Status board.")
        mode = self.find_mode_on_board(mode_name=mode_name, board=ui.CONTENT_STATUS_BOARD_1, rows=3, cols=4)
        if mode:
            self.go_to_main_menu()
            return mode
        self.emulator.swipe(ui.CONTENT_STATUS_DRAG_FROM, ui.CONTENT_STATUS_DRAG_TO, duration=0.2)
        r_sleep(1)
        mode = self.find_mode_on_board(mode_name=mode_name, board=ui.CONTENT_STATUS_BOARD_2, rows=3, cols=4)
        if mode:
            self.go_to_main_menu()
            return mode

    def find_mode_on_board(self, mode_name, board, rows, cols):
        """Parses information from Content Status Board screen about game modes.
        Creates pieces of board's elements for each element at (row, col) in Content Status Board and tries to parse it.

        :param str mode_name: name of game mode.
        :param ui.UIElement board: UI element that represents current Content Status Board.
        :param int rows: rows count of board's table.
        :param int cols: cols count of board's table.

        :rtype: GameMode
        """
        self.emulator.get_screen_image()  # Store frame to cache for multi-threading the search
        element = ui.CONTENT_STATUS_ELEMENT_1  # Element contain button rectangle of local position and it's offset
        for col in range(cols):
            for row in range(rows):
                element_rect = ui.Rect(row * element.button_rect.width + row * element.offset.width,
                                       col * element.button_rect.height + col * element.offset.height,
                                       (row + 1) * element.button_rect.width + row * element.offset.width,
                                       (col + 1) * element.button_rect.height + col * element.offset.height)
                mode = self.get_mode_from_element(board_rect=board.button_rect, element_rect=element_rect)
                if mode:
                    self._modes[mode.name] = mode
                    if mode.name == mode_name:
                        return mode

    def get_mode_from_element(self, board_rect, element_rect):
        """Gets information about game mode from single game mode element.
        `element_rect` rectangle is made from coordinates that are local inside any Content Status Board rectangle.
        In order to obtain info about element, method creates temporary UI element
        and calculates `element_rect` local coordinates into global coordinates inside `board_rect`.

        :param ui.Rect board_rect: rectangle that represents current Content Status Board.
            See `ui.CONTENT_STATUS_BOARD_1` or `ui.CONTENT_STATUS_BOARD_2` for reference.
        :param ui.Rect element_rect: rectangle of single game mode element inside board.
            See `ui.CONTENT_STATUS_ELEMENT_1` for reference.

        :rtype: GameMode
        """

        def create_global_copy(ui_element: ui.UIElement, parent_rect: ui.Rect):
            copy_ui = ui_element.copy()
            copy_ui.text_rect.parent = parent_rect
            copy_ui.text_rect = copy_ui.text_rect.global_rect
            return copy_ui

        # Getting global rects of elements
        element_ui = ui.UIElement(name='UI_BOARD_ELEMENT')
        element_ui.button_rect = element_rect
        element_ui.button_rect.parent = board_rect
        label_ui = create_global_copy(ui_element=ui.CONTENT_STATUS_ELEMENT_LABEL, parent_rect=element_ui.button_rect)
        stage_ui = create_global_copy(ui_element=ui.CONTENT_STATUS_ELEMENT_STAGE, parent_rect=element_ui.button_rect)

        stage_label = self.emulator.get_screen_text(label_ui)
        stage_counter_text = self.emulator.get_screen_text(stage_ui)
        logger.debug(f"Stage: {stage_label}; stages: {stage_counter_text}")
        current_stages, max_stages = self.get_current_and_max_values_from_text(stage_counter_text)
        # Find mode and return info about stages and board
        for mode_name in self._mode_names:
            if is_strings_similar(mode_name, stage_label):
                game_mode = GameMode(name=mode_name, stages=current_stages, max_stages=max_stages,
                                     ui_button=element_ui, ui_board=board_rect.value)
                return game_mode

    def select_mode(self, name):
        """Selects and opens game mode from Content Status Board by it's name.

        :param str name: game mode's name.
        """
        mode = self.get_mode(name=name)
        if not self.go_to_content_status_board():
            logger.error("Failed to open Content Status board.")
            return False
        if mode.ui_board == ui.CONTENT_STATUS_BOARD_2.button_rect.value:
            logger.debug(f"Mode {name} is on second board. Dragging")
            self.emulator.swipe(ui.CONTENT_STATUS_DRAG_FROM, ui.CONTENT_STATUS_DRAG_TO, duration=0.4)
            r_sleep(1)
        self.emulator.click_button(mode.ui_button)
        return True

    def go_to_mission_selection(self):
        """Goes to Missions screen."""
        self.go_to_main_menu()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ENTER_MISSIONS):
            self.emulator.click_button(ui.ENTER_MISSIONS)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.SELECT_MISSION):
                r_sleep(1)
                return True

    def go_to_coop(self):
        """Goes to Co-op screen."""
        self.go_to_main_menu()
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ENTER_MISSIONS):
            self.emulator.click_button(ui.ENTER_MISSIONS)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.COOP_MISSIONS):
                self.emulator.click_button(ui.COOP_MISSIONS)

    def go_to_challenges(self):
        """Goes to Challenges screen."""
        self.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_CHALLENGES):
                self.emulator.click_button(ui.MAIN_MENU_CHALLENGES)
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CHALLENGES_STAGE_LABEL)
            logger.error("Can't find Challenges button in Main menu, exiting")
            self.emulator.click_button(ui.MAIN_MENU)
        return False

    def go_to_comic_cards(self):
        """Goes to Comic Cards screen."""
        self.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_CARDS):
                self.emulator.click_button(ui.MAIN_MENU_CARDS)
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CARDS_STAGE_LABEL)
            logger.error("Can't find Comic Cards button in Main menu, exiting")
            self.emulator.click_button(ui.MAIN_MENU)
        return False

    def go_to_inventory(self):
        """Goes to Inventory screen."""
        self.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_INVENTORY):
                self.emulator.click_button(ui.MAIN_MENU_INVENTORY)
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INVENTORY_STAGE_LABEL)
            logger.error("Can't find Inventory button in Main menu, exiting")
            self.emulator.click_button(ui.MAIN_MENU)
        return False

    def go_to_friends(self):
        """Goes to Friends screen."""
        self.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_FRIENDS):
                self.emulator.click_button(ui.MAIN_MENU_FRIENDS)
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.FRIENDS_LABEL)
            logger.error("Can't find Friends button in Main menu, exiting")
            self.emulator.click_button(ui.MAIN_MENU)
        return False

    def go_to_alliance(self):
        """Goes to Alliance screen."""
        self.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_ALLIANCE):
                self.emulator.click_button(ui.MAIN_MENU_ALLIANCE)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ALLIANCE_LEVEL_UP_NOTIFICATION):
                    logger.debug("Closing Alliance level up notification.")
                    self.emulator.click_button(ui.ALLIANCE_LEVEL_UP_NOTIFICATION)
                self.close_after_mission_notifications()
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ALLIANCE_LABEL)
            logger.error("Can't find Alliance button in Main menu, exiting")
            self.emulator.click_button(ui.MAIN_MENU)
        return False

    def go_to_inbox(self):
        """Goes to Inbox screen."""
        self.go_to_main_menu()
        self.emulator.click_button(ui.MAIN_MENU)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU):
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_INBOX):
                self.emulator.click_button(ui.MAIN_MENU_INBOX)
                return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.INBOX_LABEL)
            logger.error("Can't find Inbox button in Main menu, exiting")
            self.emulator.click_button(ui.MAIN_MENU)
        return False

    def go_to_epic_quests(self):
        """Goes to Epic Quests screen."""
        if self.go_to_mission_selection():
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.EPIC_QUEST_MISSIONS):
                self.emulator.click_button(ui.EPIC_QUEST_MISSIONS)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.EQ_LABEL):
                    r_sleep(1)
                    return True

    def go_to_dispatch_mission(self):
        """Goes to Dispatch Mission screen."""
        if self.go_to_mission_selection():
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DISPATCH_MISSION):
                self.emulator.click_button(ui.DISPATCH_MISSION)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DISPATCH_MISSION_LABEL):
                    r_sleep(1)
                    return True

    def restart_game(self):
        """Restarts the game.

        :return: was restart successful or not.
        :rtype: bool
        """
        if not self.emulator.restartable:
            return logger.warning("You need to connect Android Debug Bridge to your emulator first.")
        self.clear_modes()
        if self.emulator.close_marvel_future_fight():
            return self.start_game()
        logger.error("Failed to close the game.")

    def start_game(self):
        """Starts the game.

        :return: was game started or not.
        :rtype: bool
        """
        if not self.emulator.restartable:
            return logger.warning("You need to connect Android Debug Bridge to your emulator first.")

        def download_update():
            if self.emulator.is_ui_element_on_screen(ui_element=ui.DOWNLOAD_UPDATE):
                logger.info("Downloading the update.")
                self.emulator.click_button(ui.DOWNLOAD_UPDATE)

        def is_game_started():
            download_update()
            is_main_menu = self.is_main_menu()
            is_main_menu or \
            self.close_news() or \
            self.close_daily_rewards() or \
            self.close_alliance_conquest() or \
            self.close_alliance_conquest_results() or \
            self.close_battleworld_rewards() or \
            self.close_maintenance_notice() or \
            self.close_ads(timeout=1)
            return is_main_menu

        if self.emulator.start_marvel_future_fight():
            if wait_until(confirm_condition_by_time, confirm_condition=is_game_started, timeout=120):
                logger.debug("Game started successfully.")
                return True
        logger.error("Failed to start the game.")
