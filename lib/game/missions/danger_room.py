import re
from lib.game.battle_bot import ManualBattleBot
from lib.game.missions.missions import Missions
from lib.functions import wait_until, r_sleep, convert_colors_in_image
import lib.logger as logging

logger = logging.get_logger(__name__)
character_popularity_regexp = re.compile(r"([0-9][0-9]?\.?[0-9]?[0-9])? ?%?")


class DangerRoom(Missions):
    """Class for working with Danger Room battles."""

    class MODE:

        NORMAL = "NORMAL"
        EXTREME = "EXTREME"

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        super().__init__(game, 'DANGER_ROOM_LABEL')

    @property
    def battle_over_conditions(self):
        def maintain_team():
            return self.emulator.is_ui_element_on_screen(self.ui['DANGER_ROOM_MAINTAIN_CURRENT_TEAM'])

        return [maintain_team]

    @property
    def disconnect_conditions(self):
        def game_canceled():
            if self.emulator.is_ui_element_on_screen(self.ui['DANGER_ROOM_GAME_CANCELED']):
                self.emulator.click_button(self.ui['DANGER_ROOM_GAME_CANCELED'].button)
                return True

        return super().disconnect_conditions + [game_canceled]

    def _close_rewards_notifications(self, timeout=3):
        """Close any rewards notifications.

        :param timeout: timeout of waiting for notifications.

        :return: True or False: were ads closed.
        """

        def close_notification(ui_element):
            if self.emulator.is_ui_element_on_screen(ui_element):
                self.emulator.click_button(ui_element.button)
                return True
            return False

        def close_notifications():
            return close_notification(ui_element=self.ui['DANGER_ROOM_WEEKLY_RESULTS_CLOSE']) or \
                   close_notification(ui_element=self.ui['DANGER_ROOM_WEEKLY_REWARDS_CLOSE'])

        for _ in range(timeout):
            notifications_closed = wait_until(close_notifications, timeout=1)
            logger.debug(f"Danger Room: rewards notifications was closed: {notifications_closed}")

    def open_danger_room(self):
        """Open Danger Room missions lobby."""
        self.game.get_mode(name=self.mode_name)
        self.game.select_mode(self.mode_name)
        self._close_rewards_notifications()
        return wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DANGER_ROOM_LABEL'])

    def _select_danger_room_mode(self, mode):
        """Select Danger Room's mode.

        :param mode: room's mode.

        :return: True or False: was mode selected properly.
        """
        if mode != self.MODE.NORMAL and mode != self.MODE.EXTREME:
            logger.error(f"Got wrong mode for battles: {mode}.")
            return False
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['DANGER_ROOM_LABEL']):
            logger.warning("Can't get in mission lobby.")
            return False
        if mode == self.MODE.NORMAL:
            logger.info("Starting NORMAL battle.")
            lobby_ui = self.ui['DANGER_ROOM_NORMAL_MODE_LOBBY']
            self.emulator.click_button(self.ui['DANGER_ROOM_NORMAL_MODE'].button)
        if mode == self.MODE.EXTREME:
            logger.info("Starting EXTREME battle.")
            lobby_ui = self.ui['DANGER_ROOM_EXTREME_MODE_LOBBY']
            self.emulator.click_button(self.ui['DANGER_ROOM_EXTREME_MODE'].button)

        self.emulator.click_button(self.ui['DANGER_ROOM_ENTER'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['DANGER_ROOM_NO_ENERGY'], timeout=3):
            logger.warning("Not enough energy. Can't get to room.")
            self.emulator.click_button(self.ui['DANGER_ROOM_NO_ENERGY'].button)
            return False
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['DANGER_ROOM_BLOCK_NOTICE'], timeout=5):
            logger.warning("You've been blocked after disconnect. Can't get to room.")
            self.emulator.click_button(self.ui['DANGER_ROOM_BLOCK_NOTICE'].button)
            return False
        if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=lobby_ui, timeout=15):
            logger.warning("Can't get in room's lobby. Probably stuck on loading. Trying to restart game.")
            if self.game.restart_game():
                self.open_danger_room()
                return self._select_danger_room_mode(mode=mode)
            return False
        return True

    def do_missions(self, times=0, mode=MODE.NORMAL):
        """Do missions."""
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions(times=self.stages, mode=mode)
            self.end_missions()

    def start_missions(self, times=0, mode=MODE.NORMAL):
        """Start Danger Room's missions.

        :param times: how many times to complete missions.
        :param mode: room's mode.
        """
        logger.info(f"Starting Danger Room for {self.stages} times on {mode} mode.")
        if not self.open_danger_room():
            logger.warning("Can't get in mission lobby.")
            return
        if not self._select_danger_room_mode(mode=mode):
            return
        while times > 0:
            if not self.press_start_button(start_button_ui='DANGER_ROOM_JOIN'):
                logger.error("Cannot start Danger Room battle, exiting.")
                return
            if not self._select_character_by_mode(mode=mode):
                logger.debug("Can't select character. Trying to select mode again.")
                self._check_game_canceled()
                if not self._select_danger_room_mode(mode=mode):
                    return
                continue
            self._start_manual_bot_for_danger_room()
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['DANGER_ROOM_LABEL'], timeout=10):
                logger.debug("Got disconnected. Returning to mission lobby.")
                if not self._select_danger_room_mode(mode=mode):
                    return
                continue
            self.emulator.click_button(self.ui['DANGER_ROOM_MAINTAIN_CURRENT_TEAM'].button)
            if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['DANGER_ROOM_BATTLE_INFO'],
                              timeout=10):
                logger.warning("Something went wrong after the battle.")
                return
            times -= 1
            self.close_mission_notifications()
            if times > 0:
                self.game.clear_modes()  # Clear mode in case we won battle and button changed its position
                self.press_repeat_button(mode=mode)
            else:
                self.press_home_button(home_button='DANGER_ROOM_HOME')
                self.close_after_mission_notifications()
        logger.info("No more stages.")

    def press_start_button(self, start_button_ui='DANGER_ROOM_JOIN'):
        """Press start button of the mission."""
        if self.emulator.is_ui_element_on_screen(self.ui[start_button_ui]):
            self.emulator.click_button(self.ui[start_button_ui].button)
            if wait_until(self._check_cancel_button, timeout=3):
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=self.ui['DANGER_ROOM_CHARACTER_SELECT_MENU'], timeout=180):
                    logger.debug("Successfully get to character selector.")
                    return True
                else:
                    logger.warning("Waiting too long to find team. Canceling and restarting search.")
                    self.emulator.click_button(self.ui['DANGER_ROOM_CANCEL_SEARCH'].button)
                    r_sleep(2)  # Waiting for Join button to enable
                    return self.press_start_button(start_button_ui=start_button_ui)
        logger.warning("Unable to join battle.")
        return False

    def press_repeat_button(self, repeat_button_ui='DANGER_ROOM_CONTINUE', start_button_ui=None, mode=None):
        """Press repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.emulator.click_button(self.ui[repeat_button_ui].button)
        while not self.emulator.is_ui_element_on_screen(ui_element=self.ui['DANGER_ROOM_ENTER']):
            self.close_after_mission_notifications(timeout=1)
        return self._select_danger_room_mode(mode=mode)

    def press_home_button(self, home_button='HOME_BUTTON'):
        """Press home button of the mission."""
        logger.debug(f"Clicking HOME button with UI Element: {home_button}.")
        self.emulator.click_button(self.ui[home_button].button)
        while not self.game.is_main_menu():
            if self.emulator.is_ui_element_on_screen(ui_element=self.ui['DANGER_EXIT_LOBBY_OK']):
                self.emulator.click_button(self.ui['DANGER_EXIT_LOBBY_OK'].button)
            self.close_after_mission_notifications(timeout=1)
        return True

    def _get_all_characters_info_for_normal_mode(self):
        """Get all characters and their popularity from selector.

        :return: sorted indexes of characters by popularity and character's images.
        """
        characters_popularity, characters_images = [], []
        for character_index in range(1, 7):
            character_ui = self.ui[f'DANGER_ROOM_CHARACTER_{character_index}']
            character_image = self.emulator.get_screen_image(rect=character_ui.button)
            characters_images.append(character_image)
            character_popularity_text = self.emulator.get_screen_text(ui_element=character_ui)
            full_match = character_popularity_regexp.fullmatch(character_popularity_text)
            if not full_match:
                logger.warning(f"Can't read character #{character_index} popularity, assuming it's 0.")
                character_popularity = 0
            else:
                character_popularity = full_match.group(1)
            characters_popularity.append(float(character_popularity))
        sorted_char_index = sorted(range(len(characters_popularity)), key=lambda k: characters_popularity[k])
        return sorted_char_index, characters_images

    def _get_all_characters_info_for_extreme_mode(self):
        """Get all available characters and their popularity from selector.

        :return: sorted indexes of non participated characters by popularity.
        """
        characters_popularity = []
        for character_index in range(1, 13):
            character_ui = self.ui[f'DANGER_ROOM_EXTREME_CHARACTER_{character_index}']
            character_participation_rect = [self.ui[f'DANGER_ROOM_EXTREME_CHARACTER_USED_{character_index}'].rect]
            character_participation_color = self.ui[f'DANGER_ROOM_EXTREME_CHARACTER_USED_{character_index}'].button
            color = (character_participation_color[0], character_participation_color[1],
                     character_participation_color[2])
            character_participation = self.emulator.is_color_similar(color=color, rects=character_participation_rect)
            if not character_participation:
                logger.debug(f"Character #{character_index} already participated, skipping.")
                characters_popularity.append(0)
                continue
            character_popularity_text = self.emulator.get_screen_text(ui_element=character_ui)
            full_match = character_popularity_regexp.fullmatch(character_popularity_text)
            if not full_match:
                logger.warning(f"Can't read character #{character_index} popularity, assuming it's 0.")
                character_popularity = 0
            else:
                character_popularity = full_match.group(1)
            characters_popularity.append(float(character_popularity))
        sorted_char_index = sorted(range(len(characters_popularity)), key=lambda k: characters_popularity[k])
        return sorted_char_index

    def _check_game_canceled(self):
        """Check if game was canceled."""
        if self.emulator.is_ui_element_on_screen(ui_element=self.ui['DANGER_ROOM_GAME_CANCELED']):
            logger.debug("Game was canceled. Returning to mission lobby.")
            self.emulator.click_button(self.ui['DANGER_ROOM_GAME_CANCELED'].button)
            return True
        if self.emulator.is_ui_element_on_screen(ui_element=self.ui['KICKED_FROM_THE_SYSTEM']):
            logger.debug("You've been kicked from the system. Returning to mission lobby.")
            self.emulator.click_button(self.ui['KICKED_FROM_THE_SYSTEM'].button)
            return True
        return False

    def _is_character_available(self, character_ui, character_image):
        """Check if character is available.

        :param character_ui: character's UI element.
        :param character_image: image of character.

        :return: True or False: is character available.
        """
        character_ui = character_ui.copy()
        character_ui.rect = None
        character_ui.threshold = 0.8
        character_ui.image = character_image
        character_ui.save_file += "_img"
        return self.emulator.is_image_on_screen(ui_element=character_ui)

    def _select_character_by_mode(self, mode):
        """Select character for Danger Room by mode."""
        if mode == self.MODE.NORMAL:
            return self._select_character_for_normal_mode()
        if mode == self.MODE.EXTREME:
            return self._select_character_for_extreme_mode()

    def _select_character_for_normal_mode(self):
        """Select best available character for NORMAL battle."""
        popular_character_indexes, characters_images = self._get_all_characters_info_for_normal_mode()
        while not self.emulator.is_ui_element_on_screen(ui_element=self.ui['DANGER_ROOM_BATTLE_BEGINS_SOON_NORMAL']):
            if self._check_game_canceled():
                return False
            best_character = None
            for character_index in popular_character_indexes:
                character_ui = self.ui[f'DANGER_ROOM_CHARACTER_{character_index + 1}']
                if self._is_character_available(character_ui=character_ui,
                                                character_image=characters_images[character_index]):
                    best_character = character_ui
            if not best_character and not self.emulator.is_ui_element_on_screen(
                    ui_element=self.ui['DANGER_ROOM_BATTLE_BEGINS_SOON_NORMAL']):
                logger.error("Can't find best character for NORMAL mode.")
                return False
            if best_character:
                logger.debug(f"Selecting character {best_character.name}")
                self.emulator.click_button(best_character.button)
                r_sleep(1)
        logger.debug("Battle is ready to begin.")
        return True

    def _select_character_for_extreme_mode(self):
        """Select best available character for EXTREME battle."""
        popular_character_indexes = self._get_all_characters_info_for_extreme_mode()
        while not self.emulator.is_ui_element_on_screen(ui_element=self.ui['DANGER_ROOM_BATTLE_BEGINS_SOON_EXTREME']):
            if self._check_game_canceled():
                return False
            best_character = None
            for character_index in popular_character_indexes:
                best_character = self.ui[f'DANGER_ROOM_EXTREME_CHARACTER_{character_index + 1}']
            if not best_character:
                logger.error("Can't find best character for mode.")
                return False
            logger.debug(f"Selecting character {best_character.name}")
            self.emulator.click_button(best_character.button)
            r_sleep(2)
        logger.debug("Battle is ready to begin.")
        return True

    def _start_manual_bot_for_danger_room(self):
        """Apply Danger Room's rules to ManualBattleBot and start it."""
        manual_bot = ManualBattleBot(self.game, self.battle_over_conditions, self.disconnect_conditions)
        old_is_battle = manual_bot.is_battle
        manual_bot.is_battle = lambda: old_is_battle() and not self.emulator.is_ui_element_on_screen(
            self.ui['DANGER_ROOM_BATTLE_REVIVE'])
        manual_bot.fight(move_around=True)

    def _check_cancel_button(self):
        """Returns if CANCEL button is on screen."""
        # Convert red colors to white because fancy UI is unreadable
        extreme_red_color = ([200, 0, 0], [255, 30, 30])
        image = self.emulator.get_screen_image(rect=self.ui['DANGER_ROOM_CANCEL_SEARCH'].rect)
        converted_image = convert_colors_in_image(image=image, colors=[extreme_red_color])
        return self.emulator.is_ui_element_on_screen(ui_element=self.ui['DANGER_ROOM_CANCEL_SEARCH'],
                                                     screen=converted_image)
