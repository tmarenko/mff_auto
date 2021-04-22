import re
from lib.functions import wait_until, is_strings_similar, r_sleep, confirm_condition_by_time
from lib.game import ui
from multiprocessing.pool import ThreadPool
from multiprocessing import cpu_count
import lib.logger as logging
logger = logging.get_logger(__name__)

cur_slash_max_regexp = re.compile(r"(\d*) ?/ ?(\d*)")
KEY_PAGE_UP = 33


class GameMode:
    """Class for working with game modes."""

    def __init__(self, name, stages=0, max_stages=0, ui_button=None, ui_board=None):
        self.name = name
        self.stages = stages
        self.max_stages = max_stages
        self.ui_button = ui_button
        self.ui_board = ui_board


class Game:
    """Class for working with main game methods."""

    ACQUIRE_HEROIC_QUEST_REWARDS = False

    def __init__(self, player, user_name=None):
        """Class initialization.

        :param lib.player.NoxWindow player: instance of game player.
        :param user_name: game user name.
        """
        self.player = player
        self._apply_decorators()
        self.ui = ui.load_ui_settings()
        self._mode_names = ui.load_game_modes()
        self._user_name = user_name
        self._current_energy, self._energy_max = 0, 0
        self._gold = 0
        self._boost = 0
        self.timeline_team = 1
        self.mission_team = 1
        self._modes = {}

    def _do_after_loading_circle_decorator(self, func):
        """Emulator's decorator to detect game's loading state."""
        def wrapped(*args, **kwargs):
            if self.is_loading_circle():
                r_sleep(1)
            return func(*args, **kwargs)
        return wrapped

    def _handle_network_error_decorator(self, func):
        """Emulator's decorator to detect network error notifications."""
        def wrapped(*args, **kwargs):
            if self.close_network_error_notification():
                r_sleep(1)
            return func(*args, **kwargs)
        return wrapped

    def _apply_decorators(self):
        """Apply game's decorator for Emulator."""
        # Store normal function to prevent recursive usage
        self._old_click_button = self.player.click_button
        self._old_is_ui_element_on_screen = self.player.is_ui_element_on_screen
        # Apply network decorator
        # TODO: restore as an optional setting
        # self.player.click_button = self._handle_network_error_decorator(self.player.click_button)
        # self.player.is_ui_element_on_screen = self._handle_network_error_decorator(
        #     self.player.is_ui_element_on_screen)
        # self.player.is_image_on_screen = self._handle_network_error_decorator(self.player.is_image_on_screen)
        # Apply loading decorator
        self.player.click_button = self._do_after_loading_circle_decorator(self.player.click_button)
        self.player.is_ui_element_on_screen = self._do_after_loading_circle_decorator(
            self.player.is_ui_element_on_screen)
        self.player.is_image_on_screen = self._do_after_loading_circle_decorator(self.player.is_image_on_screen)

    @staticmethod
    def get_current_and_max_values_from_text(text, regexp=cur_slash_max_regexp):
        """Get current and max value from text by regular expression."""
        result = regexp.findall(text)
        try:
            current_value = 0 if not result else int(result[0][0])
            max_value = 0 if not result else int(result[0][1])
        except ValueError:
            current_value = 0
            max_value = 0
        return current_value, max_value

    def _main_panel_visible(self):
        """Checks if you can see main panel with gold, energy, etc."""
        return self.player.is_image_on_screen(self.ui['GOLD_ICON'])

    @property
    def user_name(self):
        """Player's username."""
        if not self._user_name:
            if not self.is_main_menu():
                self.go_to_main_menu()
            self._user_name = self.player.get_screen_text(self.ui['USER_NAME'])
        return self._user_name

    @property
    def energy(self):
        """Game energy bar's value."""
        if self._main_panel_visible():
            energy = self.player.get_screen_text(self.ui['ENERGY']).replace(",", "")
            self._current_energy, self._energy_max = self.get_current_and_max_values_from_text(energy)
        return self._current_energy

    @property
    def energy_max(self):
        """Max value of energy."""
        if self._main_panel_visible():
            energy = self.player.get_screen_text(self.ui['ENERGY']).replace(",", "")
            self._current_energy, self._energy_max = self.get_current_and_max_values_from_text(energy)
        return self._energy_max

    @property
    def gold(self):
        """Game's gold value."""
        if self._main_panel_visible():
            self._gold = self.player.get_screen_text(self.ui['GOLD']).replace(",", "")
        return self._gold

    @property
    def boost(self):
        """Game boost points' value."""
        if self._main_panel_visible():
            self._boost = self.player.get_screen_text(self.ui['BOOST']).replace(",", "")
        return self._boost

    def get_all_modes(self):
        """Get information about all game modes."""
        if not self._modes:
            self.find_mode_on_content_status_board("ALL")

    def get_mode(self, name):
        """Get game mode by name."""
        if not self._modes or name not in self._modes:
            self.find_mode_on_content_status_board(mode_name=name)
            for empty_mode_name in [m_name for m_name in self._mode_names if m_name not in self._modes]:
                self._modes[empty_mode_name] = GameMode(name=empty_mode_name)
        return self._modes[name]

    def clear_modes(self):
        """Clear all game modes information."""
        self._modes = {}

    def set_timeline_team(self, team_number):
        """Set team for Timeline Battles."""
        if team_number < 1 or team_number > 5:
            logger.error("Timeline team: Team number should be between 1 and 5.")
        else:
            self.timeline_team = team_number

    def set_mission_team(self, team_number):
        """Set team for usual missions."""
        if team_number < 1 or team_number > 5:
            logger.error("Mission team: Team number should be between 1 and 5.")
        else:
            self.mission_team = team_number

    def is_main_menu(self):
        """Check if is current screen is main menu."""
        return self.player.is_ui_element_on_screen(self.ui['TEAM']) and self.player.is_ui_element_on_screen(
            self.ui['STORE'])

    def is_loading_circle(self):
        """Check if loading circle is on screen."""
        loading_circle_rects = [self.ui['LOADING_CIRCLE_1'].rect, self.ui['LOADING_CIRCLE_2'].rect,
                                self.ui['LOADING_CIRCLE_3'].rect, self.ui['LOADING_CIRCLE_4'].rect,
                                self.ui['LOADING_CIRCLE_5'].rect, self.ui['LOADING_CIRCLE_6'].rect,
                                self.ui['LOADING_CIRCLE_7'].rect, self.ui['LOADING_CIRCLE_8'].rect]
        loading_color = self.ui['LOADING_CIRCLE_1'].button
        return self.player.is_color_similar(color=(loading_color[0], loading_color[1], loading_color[2]),
                                            rects=loading_circle_rects)

    def go_to_main_menu(self):
        """Go to main menu screen."""
        if not self.is_main_menu():
            if self.player.is_image_on_screen(self.ui['HOME']):
                self.player.click_button(self.ui['HOME'].button)
                self.close_ads()
        return self.is_main_menu()

    def go_to_content_status_board(self):
        """Go to Content Status Board screen."""
        self.go_to_main_menu()
        if wait_until(self.is_main_menu, timeout=3):
            self.player.click_button(self.ui['CONTENT_STATUS_BOARD_BUTTON'].button)
            return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['CONTENT_STATUS_BOARD_LABEL'])

    def find_mode_on_content_status_board(self, mode_name):
        """Find game mode on Content Status Board.

        :param mode_name: mode's name.

        :return: GameMode: class representation of found game mode.
        """
        if not self.go_to_content_status_board():
            logger.error("Failed to open Content Status board.")
            return
        mode_from_board_1 = self.find_mode_on_board(mode_name=mode_name, board=self.ui['CONTENT_STATUS_BOARD_1'],
                                                    element=self.ui['CONTENT_STATUS_ELEMENT_1'], rows=3, cols=4)
        if mode_from_board_1:
            return mode_from_board_1
        else:
            self.player.drag(self.ui['CONTENT_STATUS_DRAG_FROM'].button, self.ui['CONTENT_STATUS_DRAG_TO'].button,
                             duration=0.2)
            r_sleep(1)
            return self.find_mode_on_board(mode_name=mode_name, board=self.ui['CONTENT_STATUS_BOARD_2'],
                                           element=self.ui['CONTENT_STATUS_ELEMENT_1'], rows=3, cols=4)

    def find_mode_on_board(self, mode_name, board, element, rows, cols):
        """Parse information from Content Status Board screen about game modes.
        Screen contains table of game modes with additional info.

        :param mode_name: mode's name.
        :param board: rectangle of Content Status Board.
        :param element: template of rectangle of game mode element. Contains only width/height information.
        :param rows: rows count of board's table.
        :param cols: cols count of board's table.

        :return: dictionary with information about game modes on board.
        """

        def chunk_items(items, chunk_size):
            for i in range(0, len(items), chunk_size):
                chunk = items[i:i + chunk_size]
                yield chunk
        self.player.get_screen_image()  # Store frame to cache for multi-threading the search
        offset = element.button
        elements = [(board.rect, ui.Rect(i * element.rect.width + i * offset.width,
                                         j * element.rect.height + j * offset.height,
                                         (i + 1) * element.rect.width + i * offset.width,
                                         (j + 1) * element.rect.height + j * offset.height))
                    for j in range(cols) for i in range(rows)]
        with ThreadPool() as pool:
            for chunk_element in chunk_items(items=elements, chunk_size=cpu_count()):
                modes = pool.starmap(self.get_mode_from_element, chunk_element)
                for mode in [non_empty_mode for non_empty_mode in modes if non_empty_mode]:
                    self._modes[mode.name] = mode
                    if mode.name == mode_name:
                        return mode

    def get_mode_from_element(self, board_rect, element_rect):
        """Get information about game mode from single game mode element.

        :param board_rect: rectangle of Content Status Board.
        :param element_rect: rectangle of single game mode element inside board.

        :return: dictionary with information about game mode inside element_rect.
        """
        # Getting global rects of elements
        element_ui = ui.UIElement('UI_BOARD_ELEMENT', text_rect=element_rect)
        element_ui.rect.parent = board_rect
        self.ui['CONTENT_STATUS_ELEMENT_LABEL'].rect.parent = element_ui.rect
        self.ui['CONTENT_STATUS_ELEMENT_STAGE'].rect.parent = element_ui.rect
        # Getting board image and element image. Use it for stage recognize
        board_image = self.player.get_screen_image(board_rect.value)
        element_image = self.player.get_image_from_image(board_image, element_ui)
        stage_label_image = self.player.get_image_from_image(element_image,
                                                             self.ui['CONTENT_STATUS_ELEMENT_LABEL'])
        stage_label = self.player.get_screen_text(self.ui['CONTENT_STATUS_ELEMENT_LABEL'], screen=stage_label_image)
        stage_counter_image = self.player.get_image_from_image(element_image,
                                                               self.ui['CONTENT_STATUS_ELEMENT_STAGE'])
        stage_counter_text = self.player.get_screen_text(self.ui['CONTENT_STATUS_ELEMENT_STAGE'],
                                                         screen=stage_counter_image)
        logger.debug(f"Stage: {stage_label}; stages: {stage_counter_text}")
        current_stages, max_stages = self.get_current_and_max_values_from_text(stage_counter_text)
        # Find mode and return info about stages and board
        for mode_name in self._mode_names:
            if is_strings_similar(mode_name, stage_label):
                game_mode = GameMode(name=mode_name, stages=current_stages, max_stages=max_stages,
                                     ui_button=element_ui.rect.global_rect, ui_board=board_rect.value)
                return game_mode

    def select_mode(self, name):
        """Select and open game mode from Content Status Board.

        :param name: game mode's name.
        """
        if not self.go_to_content_status_board():
            logger.error("Failed to open Content Status board.")
            return False
        mode = self._modes[name]
        if mode.ui_board == self.ui['CONTENT_STATUS_BOARD_2'].rect.value:
            logger.debug(f"Mode {name} is on second board. Dragging")
            self.player.drag(self.ui['CONTENT_STATUS_DRAG_FROM'].button, self.ui['CONTENT_STATUS_DRAG_TO'].button,
                             duration=0.4)
            r_sleep(1)
        self.player.click_button(mode.ui_button)
        return True

    def go_to_mission_selection(self):
        """Go to Missions screen."""
        self.go_to_main_menu()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ENTER_MISSIONS']):
            self.player.click_button(self.ui['ENTER_MISSIONS'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['SELECT_MISSION']):
                r_sleep(1)
                return True

    def go_to_challenge_selection(self):
        """DEPRECATED.

        Go to Challenges screen.
        """
        self.go_to_main_menu()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ENTER_MISSIONS']):
            self.player.click_button(self.ui['ENTER_MISSIONS'].button)
            r_sleep(1)
            self.player.click_button(self.ui['CHALLENGE_MISSIONS'].button)
            r_sleep(1)

    def go_to_arena(self):
        """DEPRECATED.

        Go to Arena screen.
        """
        self.go_to_main_menu()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ENTER_MISSIONS']):
            self.player.click_button(self.ui['ENTER_MISSIONS'].button)
            r_sleep(1)
            self.player.click_button(self.ui['ARENA_MISSIONS'].button)
            r_sleep(1)

    def go_to_coop(self):
        """Go to Co-op screen."""
        self.go_to_main_menu()
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ENTER_MISSIONS']):
            self.player.click_button(self.ui['ENTER_MISSIONS'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['COOP_MISSIONS']):
                self.player.click_button(self.ui['COOP_MISSIONS'].button)

    def go_to_challenges(self):
        """Go to Challenges screen."""
        self.go_to_main_menu()
        self.player.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_CHALLENGES']):
                self.player.click_button(self.ui['MAIN_MENU_CHALLENGES'].button)
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['CHALLENGES_STAGE_LABEL'])
            logger.warning("Can't find Challenges button in Main menu, exiting")
            self.player.click_button(self.ui['MAIN_MENU'].button)
        return False

    def go_to_lab(self):
        """Go to Lab screen."""
        self.go_to_main_menu()
        self.player.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_LAB']):
                self.player.click_button(self.ui['MAIN_MENU_LAB'].button)
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['LAB_LABEL'])
            logger.warning("Can't find Lab button in Main menu, exiting")
            self.player.click_button(self.ui['MAIN_MENU'].button)
        return False

    def go_to_comic_cards(self):
        """Go to Comic Cards screen."""
        self.go_to_main_menu()
        self.player.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_CARDS']):
                self.player.click_button(self.ui['MAIN_MENU_CARDS'].button)
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['CARDS_STAGE_LABEL'])
            logger.warning("Can't find Comic Cards button in Main menu, exiting")
            self.player.click_button(self.ui['MAIN_MENU'].button)
        return False

    def go_to_inventory(self):
        """Go to Inventory screen."""
        self.go_to_main_menu()
        self.player.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_INVENTORY']):
                self.player.click_button(self.ui['MAIN_MENU_INVENTORY'].button)
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['INVENTORY_STAGE_LABEL'])
            logger.warning("Can't find Inventory button in Main menu, exiting")
            self.player.click_button(self.ui['MAIN_MENU'].button)
        return False

    def go_to_friends(self):
        """Go to Friends screen."""
        self.go_to_main_menu()
        self.player.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_FRIENDS']):
                self.player.click_button(self.ui['MAIN_MENU_FRIENDS'].button)
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['FRIENDS_LABEL'])
            logger.warning("Can't find Friends button in Main menu, exiting")
            self.player.click_button(self.ui['MAIN_MENU'].button)
        return False

    def go_to_alliance(self):
        """Go to Alliance screen."""
        self.go_to_main_menu()
        self.player.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_ALLIANCE']):
                self.player.click_button(self.ui['MAIN_MENU_ALLIANCE'].button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['ALLIANCE_LEVEL_UP_NOTIFICATION']):
                    logger.debug("Closing Alliance level up notification.")
                    self.player.click_button(self.ui['ALLIANCE_LEVEL_UP_NOTIFICATION'].button)
                return wait_until(self.player.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['ALLIANCE_LABEL'])
            logger.warning("Can't find Alliance button in Main menu, exiting")
            self.player.click_button(self.ui['MAIN_MENU'].button)
        return False

    def go_to_epic_quests(self):
        """Go to Epic Quests screen."""
        if self.go_to_mission_selection():
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EPIC_QUEST_MISSIONS']):
                self.player.click_button(self.ui['EPIC_QUEST_MISSIONS'].button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['EQ_LABEL']):
                    r_sleep(1)
                    return True

    def restart_game(self, repeat_while=None):
        """Restart game.

        :param repeat_while: repeat closing game if condition is True.
        :return: True or False: was restart successful.
        """
        if self.player.restartable:
            self.close_game()
            if repeat_while:
                while repeat_while():
                    r_sleep(1)
                    self.close_game()
            return self.start_game()
        logger.warning(f"Current player {self.player.__class__.__name__} "
                       f"version {self.player.get_version()} does not support closing apps.")
        return False

    def close_game(self):
        """Close game.

        :return: True or False: was game closed.
        """
        logger.debug("Closing game.")
        self.player.close_current_app()
        r_sleep(2)

    def start_game(self):
        """Start game.

        :return: True or False: was game started.
        """
        def is_game_started():
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

        logger.debug("Starting game.")
        self.player.click_button(self.ui['GAME_APP'].button)
        if wait_until(confirm_condition_by_time, confirm_condition=is_game_started, timeout=120):
            logger.debug("Game started successfully.")
            return True
        logger.warning("Failed to start game")
        return False

    def close_subscription_selector(self):
        """Close Biometrics and X-Gene selector window."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['BIOMETRICS_NOTIFICATION']):
            self.player.click_button(self.ui['BIOMETRICS_NOTIFICATION'].button)
            return True
        if self.player.is_ui_element_on_screen(ui_element=self.ui['X_GENE_NOTIFICATION']):
            self.player.click_button(self.ui['X_GENE_NOTIFICATION'].button)
            return True
        return False

    def close_alliance_conquest(self):
        """Close Alliance Conquest notice window."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['ALLIANCE_CONQUEST_NOTIFICATION']):
            self.player.click_button(self.ui['ALLIANCE_CONQUEST_NOTIFICATION'].button)
            return True
        return False

    def close_alliance_conquest_results(self):
        """Close Alliance Conquest Results notification."""
        if self.player.is_ui_element_on_screen(self.ui['ALLIANCE_CONQUEST_REWARDS_ACQUIRE']):
            self.player.click_button(self.ui['ALLIANCE_CONQUEST_REWARDS_ACQUIRE'].button)
            return True
        if self.player.is_ui_element_on_screen(self.ui['ALLIANCE_CONQUEST_REWARDS_CLOSE']):
            self.player.click_button(self.ui['ALLIANCE_CONQUEST_REWARDS_CLOSE'].button)
            return True
        return False

    def close_maintenance_notice(self):
        """Close maintenance notice window."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['MAINTENANCE_NOTICE']):
            self.player.click_button(self.ui['MAINTENANCE_NOTICE'].button)
            return True
        return False

    def close_daily_rewards(self):
        """Close daily rewards window and notification about rewards."""
        if self.player.is_ui_element_on_screen(self.ui['MAIN_MENU_REWARDS']):
            self.player.click_button(self.ui['MAIN_MENU_REWARDS'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU_REWARDS_OK']):
                self.player.click_button(self.ui['MAIN_MENU_REWARDS_OK'].button)
                return True
        return False

    def close_battleworld_rewards(self):
        """Close BattleWorld rewards notification."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['MAIN_MENU_REWARDS_OK']):
            self.player.click_button(self.ui['MAIN_MENU_REWARDS_OK'].button)
            return True
        return False

    def close_news(self):
        """Close 'Don't Show Again' news on start of the game."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['NEWS_ON_START_GAME']):
            self.player.click_button(self.ui['NEWS_ON_START_GAME'].button)
            return True
        return False

    def close_ads(self, timeout=2):
        """Close any ads on main menu screen.

        :param timeout: timeout of waiting for ads.

        :return: True or False: were ads closed.
        """
        def close_ad(ad_ui):
            if self.player.is_ui_element_on_screen(ad_ui):
                self.player.click_button(ad_ui.button)
                if wait_until(self.player.is_ui_element_on_screen, timeout=1.5,
                              ui_element=self.ui['MAIN_MENU_AD_CLOSE']):
                    self.player.click_button(self.ui['MAIN_MENU_AD_CLOSE'].button)
                    return True
            return False

        def close_ads():
            return close_ad(self.ui['MAIN_MENU_AD']) or \
                   close_ad(self.ui['MAIN_MENU_AD_2']) or \
                   close_ad(self.ui['MAIN_MENU_AD_3']) or \
                   close_ad(self.ui['MAIN_MENU_AD_4']) or \
                   self.close_subscription_selector()

        result = False
        for _ in range(timeout):
            result = result or wait_until(close_ads, timeout=1)
        return result

    def close_complete_challenge_notification(self):
        """Close Complete Challenge notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['CHALLENGE_COMPLETE_NOTIFICATION']):
            self.player.click_button(self.ui['CHALLENGE_COMPLETE_NOTIFICATION'].button)
            return True
        return False

    def close_network_error_notification(self):
        """Close Network Error notification.

        :return: True or False: was notification closed.
        """
        if self._old_is_ui_element_on_screen(self.ui['NETWORK_ERROR_NOTIFICATION']):
            logger.warning("Network Error notification occurred, trying to restore connection.")
            self._old_click_button(self.ui['NETWORK_ERROR_NOTIFICATION'].button)
            return True
        return False
