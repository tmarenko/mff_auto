import time
import threading
import random
import logging
from lib.functions import wait_until

logger = logging.getLogger(__name__)

SKILL_SLEEP = {1: 0.75, 2: 1, 3: 1, 4: 1.25, 5: 2.25}


class BattleBot:
    """Class for working with game battles."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.ui = game.ui
        self.player = game.player

    def is_battle(self):
        """Check if battle is on screen.

        :return: True or False.
        """
        return self.player.is_image_on_screen(self.ui['MELEE_BUTTON']) and not self.player.is_ui_element_on_screen(
            ui_element=self.ui['INVASION_FIGHT_WAITING_IN_BATTLE'])

    def is_battle_over(self):
        """Check if battle is over.

        :return: True or False.
        """
        if self.player.is_ui_element_on_screen(self.ui['DISCONNECT_FROM_SERVER']):
            self.player.click_button(self.ui['DISCONNECT_FROM_SERVER'].button)
            return True
        if self.player.is_ui_element_on_screen(self.ui['DISCONNECT_NEW_OPPONENT']):
            self.player.click_button(self.ui['DISCONNECT_NEW_OPPONENT'].button)
            return True
        if self.player.is_ui_element_on_screen(self.ui['KICKED_FROM_THE_SYSTEM']):
            self.player.click_button(self.ui['KICKED_FROM_THE_SYSTEM'].button)
            return True
        if not self.is_battle():
            if self.player.is_image_on_screen(self.ui['ONE_STAR_MISSION_COMPLETE']):
                return True
            if self.player.is_ui_element_on_screen(self.ui['CHAR_EXP']) or \
                    self.player.is_ui_element_on_screen(self.ui['LEGENDARY_SCORE']) or \
                    self.player.is_ui_element_on_screen(self.ui['COOP_COMPLETION']) or \
                    self.player.is_ui_element_on_screen(self.ui['TIMELINE_POINTS']) or \
                    self.player.is_ui_element_on_screen(self.ui['INVASION_SLOT_CHEST']) or \
                    self.player.is_ui_element_on_screen(self.ui['INVASION_FAILED']) or \
                    self.player.is_ui_element_on_screen(self.ui['CANNOT_ENTER']):
                return True
            if self.player.is_image_on_screen(self.ui['HOME_BUTTON']) or \
                    self.player.is_image_on_screen(self.ui['HOME_BUTTON_POSITION_2']) or \
                    self.player.is_image_on_screen(self.ui['HOME_BUTTON_POSITION_3']):
                logger.debug("Found HOME button image on screen.")
                return True
        return False


class AutoBattleBot(BattleBot):
    """Class for working with AutoPlay battles."""

    def fight(self):
        """Start battle and wait until the end."""
        if wait_until(self.is_battle, 60, period=1):
            logger.info("Battle is started")
        else:
            logger.warning("Can't find MELEE button on screen after starting a battle.")
        if not wait_until(self.player.is_image_on_screen, timeout=2, ui_element=self.ui['AUTOPLAY_TOGGLE']):
            logging.debug("Found AUTO PLAY toggle inactive. Clicking it.")
            self.player.click_button(self.ui['AUTOPLAY_TOGGLE'].button)
        while not self.is_battle_over():
            time.sleep(0.75)
        logger.info("Battle is over")

    def wait_until_shifter_appeared(self):
        """Wait until Ally or Enemy shifter appears."""
        logger.debug("Waiting for Shifter to appear.")
        while not self.is_battle():
            shifter_appeared = self.player.is_ui_element_on_screen(ui_element=self.ui['ALLY_APPEARED']) or \
                               self.player.is_ui_element_on_screen(ui_element=self.ui['ENEMY_APPEARED']) or \
                               self.player.is_ui_element_on_screen(ui_element=self.ui['ALLY_AND_ENEMY_APPEARED']) or \
                               self.player.is_ui_element_on_screen(ui_element=self.ui['ENEMY_AND_ALLY_APPEARED'])
            if shifter_appeared:
                logger.debug("Shifter appeared.")
                return True
            else:
                time.sleep(0.25)
        logger.debug("Shifter didn't appeared.")
        return False


class ManualBattleBot(BattleBot):
    """Class for working with manual battles."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of game.
        """
        super().__init__(game)
        self.cooldowns = {1: '', 2: '', 3: '', 4: '', 5: ''}

    def fight(self):
        """Start battle and use skills until the end of battle."""
        logger.info("Battle is started")
        while not self.is_battle_over():
            available_skills = [key for key, value in self.cooldowns.items() if not value]
            if not available_skills:
                time.sleep(0.05)
                continue
            if self.is_battle():
                skill_num = random.choice(available_skills)
                success = self.cast_skill(skill_num)
                delay = time.time() - success
                if success and SKILL_SLEEP[skill_num] > delay:
                    time.sleep(SKILL_SLEEP[skill_num] - delay)
            else:
                self.skip_cutscene()
        logger.info("Battle is over")
        self.cooldowns = {1: '', 2: '', 3: '', 4: '', 5: ''}

    def cast_skill(self, skill_num, max_attempts=3):
        """Cast character's skill.

        :param skill_num: skill number.
        :param max_attempts: max attempts of trying to cast skill.

        :return: time when skill has been casted.
        """
        logger.debug(f"Casting {skill_num}-th skill.")
        skill_ui = self.ui[f'SKILL_{skill_num}']
        self.player.click_button(skill_ui.button)
        attempts = 1
        time.sleep(0.05)
        while not self.player.get_screen_text(ui_element=skill_ui) and self.is_battle():
            if attempts > max_attempts:
                return False
            else:
                attempts += 1
                self.player.click_button(skill_ui.button)
                time.sleep(0.05)
        now = time.time()
        cooldown = self.player.get_screen_text(ui_element=skill_ui)
        if cooldown.isdigit() and int(cooldown) > 20:
            cooldown = "1"
        if cooldown.isdigit():
            self.cooldowns[skill_num] = cooldown
            threading.Thread(target=self._reduce_cooldown, args=[skill_num]).start()
        return now if not self.is_battle_over() else False

    def skip_cutscene(self):
        """Skip battle cutscene."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['SKIP_CUTSCENE']):
            logger.debug("Skipping cutscene.")
            self.player.click_button(self.ui['SKIP_CUTSCENE'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=0.2, period=0.1,
                      ui_element=self.ui['SKIP_TAP_THE_SCREEN']):
            logger.debug("Skipping TAP THE SCREEN.")
            self.player.click_button(self.ui['SKIP_TAP_THE_SCREEN'].button)

    def _reduce_cooldown(self, skill_num):
        """Reduce cooldown value of skill.

        :param skill_num: skill number.
        """
        while self and self.cooldowns[skill_num]:
            if not self.is_battle() and self.is_battle_over():
                self.cooldowns[skill_num] = ''
                return
            time.sleep(1)
            try:
                new_cooldown = int(self.cooldowns[skill_num]) - 1
                self.cooldowns[skill_num] = '' if new_cooldown <= 0 else str(new_cooldown)
            except ValueError:
                self.cooldowns[skill_num] = ''
