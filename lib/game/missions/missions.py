import lib.logger as logging
from lib.functions import wait_until, is_strings_similar
from lib.game.battle_bot import AutoBattleBot
from lib.game.heroic_quests import HeroicQuests
logger = logging.get_logger(__name__)


class Missions:
    """Class for working with mission's methods."""

    class _DIFFICULTY_4:
        STAGE_1 = "DIFFICULTY_STAGE_1"
        STAGE_2 = "DIFFICULTY_STAGE_2"
        STAGE_3 = "DIFFICULTY_STAGE_3"
        STAGE_4 = "DIFFICULTY_STAGE_4"

    class _DIFFICULTY_6:
        STAGE_1 = "DIFFICULTY_STAGE_1"
        STAGE_2 = "DIFFICULTY_STAGE_2"
        STAGE_3 = "DIFFICULTY_STAGE_2_3"
        STAGE_4 = "DIFFICULTY_STAGE_2_4"
        STAGE_5 = "DIFFICULTY_STAGE_2_5"
        STAGE_6 = "DIFFICULTY_STAGE_2_6"

    def __init__(self, game, mode_label):
        """Class initialization.

        :param game.Game game: instance of the game.
        :param string mode_label: mission's game mode label.
        """
        self.player = game.player
        self.ui = game.ui
        self.game = game
        self.mode_name = game.ui[mode_label].text if mode_label else None

    @property
    def energy_cost(self):
        """Energy cost of the mission.

        :return: energy cost.
        """
        cost = self.player.get_screen_text(self.ui['ENERGY_COST'])
        return int(cost) if cost.isdigit() else None

    @property
    def boost_cost(self):
        """Boost points cost of the mission.

        :return: boost points cost.
        """
        cost = self.player.get_screen_text(self.ui['BOOST_COST'])
        return int(cost) if cost.isdigit() else None

    @property
    def stages_max(self):
        """Maximum stages of the mission."""
        mode = self.game.get_mode(self.mode_name)
        if mode:
            return mode.max_stages
        return 0

    @property
    def stages(self):
        """Available stages of the mission."""
        mode = self.game.get_mode(self.mode_name)
        if mode:
            return mode.stages
        return 0

    @stages.setter
    def stages(self, value):
        """Update available stages value."""
        mode = self.game.get_mode(self.mode_name)
        if mode:
            mode.stages = value

    @property
    def battle_over_conditions(self):
        def char_exp():
            return self.player.is_ui_element_on_screen(self.ui['CHAR_EXP'])

        def cannot_enter():
            return self.player.is_ui_element_on_screen(self.ui['CANNOT_ENTER'])

        def home_button():
            if self.player.is_image_on_screen(self.ui['HOME_BUTTON']) or \
                    self.player.is_image_on_screen(self.ui['HOME_BUTTON_POSITION_2']) or \
                    self.player.is_image_on_screen(self.ui['HOME_BUTTON_POSITION_3']):
                logger.debug("Found HOME button image on screen.")
                return True

        return [char_exp, cannot_enter, home_button, self.close_lvl_up_notification,
                self.close_stages_done_notification, self.close_items_def_notification, self.close_rank_up_notification,
                self.close_shield_lvl_up_notification, self.close_recruit_character_notification]

    @property
    def disconnect_conditions(self):
        def disconnect():
            if self.player.is_ui_element_on_screen(self.ui['DISCONNECT_FROM_SERVER']):
                self.player.click_button(self.ui['DISCONNECT_FROM_SERVER'].button)
                return True

        def new_opponent():
            if self.player.is_ui_element_on_screen(self.ui['DISCONNECT_NEW_OPPONENT']):
                self.player.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
                return True

        def kicked():
            if self.player.is_ui_element_on_screen(self.ui['KICKED_FROM_THE_SYSTEM']):
                self.player.click_button(self.ui['KICKED_FROM_THE_SYSTEM'].button)
                return True

        return [disconnect, new_opponent, kicked]

    def start_missions(self):
        """Start missions."""
        pass

    def end_missions(self):
        """End missions."""
        self.game.clear_modes()
        if not self.game.is_main_menu():
            self.game.player.click_button(self.ui['HOME'].button)
            self.close_after_mission_notifications()
            self.game.close_ads()

    def do_missions(self, times=None):
        """Do missions."""
        if times:
            self.stages = times
        if self.stages > 0:
            self.start_missions()
            self.end_missions()

    def select_team(self):
        """Select team for missions."""
        team_element = self.ui[f'SELECT_TEAM_{self.game.mission_team}']
        logger.debug(f"Selecting team: {team_element.name}")
        self.player.click_button(team_element.button)

    def repeat_mission(self, times):
        """Repeat missions.

        :param times: how many times to repeat.
        """
        for _ in range(times):
            if not self.press_start_button():
                logger.error("Cannot start missions while repeating them, exiting.")
                return
            AutoBattleBot(self.game, self.battle_over_conditions).fight()
            self.close_mission_notifications()
            repeat_button_ui = None
            if wait_until(self.player.is_image_on_screen, timeout=2,
                          ui_element=self.ui['REPEAT_BUTTON_IMAGE_POSITION_2']):
                repeat_button_ui = 'REPEAT_BUTTON_IMAGE_POSITION_2'
            else:
                if wait_until(self.player.is_image_on_screen, timeout=2,
                              ui_element=self.ui['REPEAT_BUTTON_IMAGE_POSITION_1']):
                    repeat_button_ui = 'REPEAT_BUTTON_IMAGE_POSITION_1'
            if repeat_button_ui:
                self.press_repeat_button(repeat_button_ui)

    def press_start_button(self, start_button_ui='START_BUTTON'):
        """Press start button of the mission.

        :return: was button clicked.
        """
        if self.player.is_ui_element_on_screen(self.ui[start_button_ui]):
            self.select_team()
            self.player.click_button(self.ui[start_button_ui].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=2, ui_element=self.ui['NOT_ENOUGH_ENERGY']):
                self.player.click_button(self.ui['NOT_ENOUGH_ENERGY'].button)
                return False
            if wait_until(self.player.is_ui_element_on_screen, timeout=2, ui_element=self.ui['INVENTORY_FULL']):
                self.player.click_button(self.ui['INVENTORY_FULL'].button)
                return False
            if wait_until(self.player.is_ui_element_on_screen, timeout=2,
                          ui_element=self.ui['ITEM_MAX_LIMIT_NOTIFICATION']):
                self.player.click_button(self.ui['ITEM_MAX_LIMIT_NOTIFICATION'].button)
            if wait_until(self.player.is_ui_element_on_screen, timeout=2,
                          ui_element=self.ui['DM_TICKET_NOTIFICATION']):
                self.player.click_button(self.ui['DM_TICKET_NOTIFICATION'].button)
            return True
        logger.warning("Unable to press START button.")
        return False

    def press_repeat_button(self, repeat_button_ui='REPEAT_BUTTON', start_button_ui='START_BUTTON'):
        """Press repeat button of the mission."""
        logger.debug(f"Clicking REPEAT button with UI Element: {repeat_button_ui}.")
        self.player.click_button(self.ui[repeat_button_ui].button)
        while not self.player.is_ui_element_on_screen(ui_element=self.ui[start_button_ui]):
            self.close_after_mission_notifications(timeout=1)
        return True

    def press_home_button(self, home_button='HOME_BUTTON'):
        """Press home button of the mission."""
        logger.debug("Clicking HOME button.")
        self.player.click_button(self.ui[home_button].button)
        while not self.game.is_main_menu():
            self.close_after_mission_notifications(timeout=1)
        return True

    def close_complete_challenge_notification(self):
        """Close Complete Challenge notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['CHALLENGE_COMPLETE_NOTIFICATION']):
            self.player.click_button(self.ui['CHALLENGE_COMPLETE_NOTIFICATION'].button)
            return True
        return False

    def close_lvl_up_notification(self):
        """Close LVL Up notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['LVL_UP_NOTIFICATION']):
            self.player.click_button(self.ui['LVL_UP_NOTIFICATION'].button)
            return True
        return False

    def close_stages_done_notification(self):
        """Close Stages Done notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['STAGES_DONE_NOTIFICATION']):
            self.player.click_button(self.ui['STAGES_DONE_NOTIFICATION'].button)
            return True
        return False

    def close_rank_up_notification(self):
        """Close Rank Up notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['RANK_UP_NOTIFICATION']):
            self.player.click_button(self.ui['RANK_UP_NOTIFICATION'].button)
            return True
        return False

    def close_items_def_notification(self):
        """Close Item's Definition notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['TAP_TO_CONTINUE']):
            self.player.click_button(self.ui['TAP_TO_CONTINUE'].button)
            return True
        return False

    def close_shield_lvl_up_notification(self):
        """Close S.H.I.E.L.D. LVL Up notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['SHIELD_LVL_UP_NOTIFICATION']):
            self.player.click_button(self.ui['SHIELD_LVL_UP_NOTIFICATION'].button)
            return True
        return False

    def close_recruit_character_notification(self):
        """Close Recruit Character notification.

        :return: True or False: was notification closed.
        """
        if self.player.is_ui_element_on_screen(self.ui['RECRUIT_CHARACTER_NOTIFICATION']):
            self.player.click_button(self.ui['RECRUIT_CHARACTER_NOTIFICATION'].button)
            return True
        return False

    def close_heroic_quest_notification(self):
        """Close Heroic Quest notification.

        :return: True or False: was notification closed.
        """
        heroic_quest = self.player.get_screen_text(self.ui['HQ_NOTIFICATION_OK'])
        # Use overlap less 0.25 because sometimes 'EPIC QUEST' is similar to 'HEROIC QUEST' with default overlap
        if is_strings_similar(self.ui['HQ_NOTIFICATION_OK'].text, heroic_quest, overlap=0.15):
            if self.game.ACQUIRE_HEROIC_QUEST_REWARDS:
                self.player.click_button(self.ui['HQ_NOTIFICATION_OPEN'].button)
                HeroicQuests(self.game).acquire_reward_and_return_back()
            else:
                self.player.click_button(self.ui['HQ_NOTIFICATION_OK'].button)
            return True
        return False

    def close_epic_quest_notification(self):
        """Close Epic Quest notification.

        :return: True or False: was notification closed.
        """
        epic_quest = self.player.get_screen_text(self.ui['EQ_NOTIFICATION_OK'])
        # Use overlap less 0.25 because sometimes 'EPIC QUEST' is similar to 'HEROIC QUEST' with default overlap
        if is_strings_similar(self.ui['EQ_NOTIFICATION_OK'].text, epic_quest, overlap=0.15):
            self.player.click_button(self.ui['EQ_NOTIFICATION_OK'].button)
            return True
        return False

    def close_mission_notifications(self, timeout=5):
        """Close all mission notifications after the battle.

        :param timeout: timeout of waiting for notifications.
        """
        def close_notifications():
            return self.close_lvl_up_notification() or \
                   self.close_stages_done_notification() or \
                   self.close_items_def_notification() or \
                   self.close_rank_up_notification() or \
                   self.close_shield_lvl_up_notification() or \
                   self.close_recruit_character_notification()

        for _ in range(timeout):
            notification_closed = wait_until(close_notifications, timeout=1)
            logger.debug(f"Notifications after end battle was closed: {notification_closed}")

    def close_after_mission_notifications(self, timeout=3):
        """Close after mission notifications outside of the battle.

        :param timeout: timeout of waiting for notifications.
        """
        def close_notifications():
            return self.close_complete_challenge_notification() or \
                   self.close_heroic_quest_notification() or \
                   self.close_epic_quest_notification()

        for _ in range(timeout):
            notification_closed = wait_until(close_notifications, timeout=1)
            logger.debug(f"After mission notifications was closed: {notification_closed}")

    def is_stage_startable(self):
        """Check if you can start stage safely.

        :return: True or False.
        """
        return bool(self.boost_cost)
