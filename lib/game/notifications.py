from lib.functions import wait_until, is_strings_similar
from lib.game.heroic_quests import HeroicQuests
import lib.logger as logging
from lib.game import ui

logger = logging.get_logger(__name__)


class Notifications:
    """Class for working with in-game notifications."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.game = game
        self.emulator = game.emulator

    def close_subscription_selector(self):
        """Close Biometrics and X-Gene selector window."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.BIOMETRICS_NOTIFICATION):
            self.emulator.click_button(ui.BIOMETRICS_NOTIFICATION)
            return True
        if self.emulator.is_ui_element_on_screen(ui_element=ui.X_GENE_NOTIFICATION):
            self.emulator.click_button(ui.X_GENE_NOTIFICATION)
            return True
        return False

    def close_alliance_conquest(self):
        """Close Alliance Conquest notice window."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.ALLIANCE_CONQUEST_NOTIFICATION):
            self.emulator.click_button(ui.ALLIANCE_CONQUEST_NOTIFICATION)
            return True
        return False

    def close_alliance_conquest_results(self):
        """Close Alliance Conquest Results notification."""
        if self.emulator.is_ui_element_on_screen(ui.ALLIANCE_CONQUEST_REWARDS_ACQUIRE):
            self.emulator.click_button(ui.ALLIANCE_CONQUEST_REWARDS_ACQUIRE)
            return True
        if self.emulator.is_ui_element_on_screen(ui.ALLIANCE_CONQUEST_REWARDS_CLOSE):
            self.emulator.click_button(ui.ALLIANCE_CONQUEST_REWARDS_CLOSE)
            return True
        return False

    def close_maintenance_notice(self):
        """Close maintenance notice window."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.MAINTENANCE_NOTICE):
            self.emulator.click_button(ui.MAINTENANCE_NOTICE)
            return True
        if self.emulator.is_ui_element_on_screen(ui_element=ui.MAINTENANCE_NOTICE_ACQUIRE):
            self.emulator.click_button(ui.MAINTENANCE_NOTICE_ACQUIRE)
            if wait_until(self.emulator.is_image_on_screen, ui_element=ui.MAINTENANCE_NOTICE_ACQUIRE_OK):
                self.emulator.click_button(ui.MAINTENANCE_NOTICE_ACQUIRE_OK)
                return True
        return False

    def close_daily_rewards(self):
        """Close daily rewards window and notification about rewards."""
        if self.emulator.is_ui_element_on_screen(ui.MAIN_MENU_REWARDS):
            self.emulator.click_button(ui.MAIN_MENU_REWARDS)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_REWARDS_OK):
                self.emulator.click_button(ui.MAIN_MENU_REWARDS_OK)
                return True
        return False

    def close_battleworld_rewards(self):
        """Close BattleWorld rewards notification."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.MAIN_MENU_REWARDS_OK):
            self.emulator.click_button(ui.MAIN_MENU_REWARDS_OK)
            return True
        return False

    def close_news(self):
        """Close 'Don't Show Again' news on start of the game."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.NEWS_ON_START_GAME):
            self.emulator.click_button(ui.NEWS_ON_START_GAME)
            return True
        return False

    def close_ads(self, timeout=2):
        """Close any ads on main menu screen.

        :param timeout: timeout of waiting for ads.

        :return: True or False: were ads closed.
        """

        def close_ad(ad_ui):
            if self.emulator.is_ui_element_on_screen(ad_ui):
                self.emulator.click_button(ad_ui)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.MAIN_MENU_AD_CLOSE):
                    self.emulator.click_button(ui.MAIN_MENU_AD_CLOSE)
                    return True
            return False

        def close_ads():
            return close_ad(ui.MAIN_MENU_AD) or \
                   close_ad(ui.MAIN_MENU_AD_2) or \
                   close_ad(ui.MAIN_MENU_AD_3) or \
                   close_ad(ui.MAIN_MENU_AD_4) or \
                   self.close_subscription_selector()

        result = False
        for _ in range(timeout):
            result = result or wait_until(close_ads, timeout=1)
        return result

    def close_complete_challenge_notification(self):
        """Close Complete Challenge notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.CHALLENGE_COMPLETE_NOTIFICATION):
            self.emulator.click_button(ui.CHALLENGE_COMPLETE_NOTIFICATION)
            return True
        return False

    def close_network_error_notification(self):
        """Close Network Error notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.NETWORK_ERROR_NOTIFICATION):
            logger.warning("Network Error notification occurred, trying to restore connection.")
            self.emulator.click_button(ui.NETWORK_ERROR_NOTIFICATION)
            return True
        return False

    def close_lvl_up_notification(self):
        """Close LVL Up notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.LVL_UP_NOTIFICATION):
            self.emulator.click_button(ui.LVL_UP_NOTIFICATION)
            return True
        return False

    def close_stages_done_notification(self):
        """Close Stages Done notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.STAGES_DONE_NOTIFICATION):
            self.emulator.click_button(ui.STAGES_DONE_NOTIFICATION)
            return True
        return False

    def close_rank_up_notification(self):
        """Close Rank Up notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.RANK_UP_NOTIFICATION_1):
            self.emulator.click_button(ui.RANK_UP_NOTIFICATION_1)
            return True
        if self.emulator.is_ui_element_on_screen(ui.RANK_UP_NOTIFICATION_2):
            self.emulator.click_button(ui.RANK_UP_NOTIFICATION_2)
            return True
        return False

    def close_items_def_notification(self):
        """Close Item's Definition notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.TAP_TO_CONTINUE):
            self.emulator.click_button(ui.TAP_TO_CONTINUE)
            return True
        return False

    def close_shield_lvl_up_notification(self):
        """Close S.H.I.E.L.D. LVL Up notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.SHIELD_LVL_UP_NOTIFICATION):
            self.emulator.click_button(ui.SHIELD_LVL_UP_NOTIFICATION)
            return True
        return False

    def close_recruit_character_notification(self):
        """Close Recruit Character notification.

        :return: True or False: was notification closed.
        """
        if self.emulator.is_ui_element_on_screen(ui.RECRUIT_CHARACTER_NOTIFICATION):
            self.emulator.click_button(ui.RECRUIT_CHARACTER_NOTIFICATION)
            return True
        return False

    def close_heroic_quest_notification(self):
        """Close Heroic Quest notification.

        :return: True or False: was notification closed.
        """
        heroic_quest = self.emulator.get_screen_text(ui.HQ_NOTIFICATION_OK)
        # Use overlap less 0.25 because sometimes 'EPIC QUEST' is similar to 'HEROIC QUEST' with default overlap
        if is_strings_similar(ui.HQ_NOTIFICATION_OK.text, heroic_quest, overlap=0.15):
            if self.game.ACQUIRE_HEROIC_QUEST_REWARDS:
                self.emulator.click_button(ui.HQ_NOTIFICATION_OPEN)
                HeroicQuests(self.game).acquire_reward_and_return_back()
            else:
                self.emulator.click_button(ui.HQ_NOTIFICATION_OK)
            return True
        return False

    def close_epic_quest_notification(self):
        """Close Epic Quest notification.

        :return: True or False: was notification closed.
        """
        epic_quest = self.emulator.get_screen_text(ui.EQ_NOTIFICATION_OK)
        # Use overlap less 0.25 because sometimes 'EPIC QUEST' is similar to 'HEROIC QUEST' with default overlap
        if is_strings_similar(ui.EQ_NOTIFICATION_OK.text, epic_quest, overlap=0.15):
            self.emulator.click_button(ui.EQ_NOTIFICATION_OK)
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
            return self.game.close_complete_challenge_notification() or \
                   self.close_heroic_quest_notification() or \
                   self.close_epic_quest_notification() or \
                   self.game.close_subscription_selector()

        for _ in range(timeout):
            notification_closed = wait_until(close_notifications, timeout=1)
            logger.debug(f"After mission notifications was closed: {notification_closed}")

    def close_squad_battle_rank_change_notification(self):
        """Close Squad Battle rank change notification."""
        if self.emulator.is_ui_element_on_screen(ui_element=ui.SB_RANK_CHANGED_1) or \
                self.emulator.is_ui_element_on_screen(ui_element=ui.SB_RANK_CHANGED_1):
            logger.info("Closing rank change notification.")
            self.emulator.click_button(ui.SB_RANK_CHANGED_1)
            return True
        return False

    def close_squad_battle_after_battle_notifications(self, timeout=10):
        """Close Squad Battle after battle notifications at the end of the battle.

        :param timeout: timeout of waiting for notifications.
        """
        for _ in range(timeout):
            notification_closed = wait_until(self.close_squad_battle_rank_change_notification, timeout=1)
            logger.debug(f"After Squad Battle notifications was closed: {notification_closed}")

    def close_daily_trivia_answer_notification(self, timeout=3):
        """Close Daily Trivia answer notifications.

        :param timeout: timeout of waiting for notifications.
        """
        def close_notifications():
            return self.game.close_complete_challenge_notification() or self.close_shield_lvl_up_notification()

        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.DAILY_TRIVIA_CLOSE_ANSWER):
            self.emulator.click_button(ui.DAILY_TRIVIA_CLOSE_ANSWER)
            notification_closed = wait_until(close_notifications, timeout=timeout)
            logger.debug(f"Complete challenge notifications was closed: {notification_closed}")
            return True
        else:
            logger.error("Something went wrong after selecting correct answer.")
