import time
import logging
from lib.functions import wait_until

logger = logging.getLogger(__name__)


class BattleBot:
    """Class for working with game battles."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.game = game
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
                    self.player.is_ui_element_on_screen(self.ui['CANNOT_ENTER']) or \
                    self.player.is_ui_element_on_screen(self.ui['SB_RANK_CHANGED']) or \
                    self.player.is_ui_element_on_screen(self.ui['SB_BATTLE_POINTS']) or \
                    self.player.is_ui_element_on_screen(self.ui['AB_YOUR_SCORE']) or \
                    self.player.is_ui_element_on_screen(self.ui['WB_SCORE']) or \
                    self.player.is_ui_element_on_screen(self.ui['WB_RESPAWN']):
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
        if wait_until(self.is_battle, timeout=60, period=1):
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


class LockedSkill(BattleBot):
    """Class for working with locked skills (T3 and Awakening skills)."""

    def __init__(self, game, skill_ui, skill_locked_ui, skill_label_ui):
        """Class initialization.

        :param game.Game game: instance of game.
        """
        super().__init__(game)
        self._locked = None
        self._skill = None
        self.history = {}
        self.skill_ui = skill_ui
        self.skill_locked_ui = skill_locked_ui
        self.skill_label_ui = skill_label_ui

    @property
    def locked(self):
        """Is skill locked property. Checking if locked version of the skill is on screen and storing result."""
        if self._locked is None:
            if not self.player.is_ui_element_on_screen(ui_element=self.ui[self.skill_label_ui]):
                logger.debug(f"{self.skill_label_ui} skill label is not on a screen. Character does not have him.")
                self._locked = True
            elif self.player.is_image_on_screen(ui_element=self.ui[self.skill_locked_ui]):
                logger.debug(f"{self.skill_locked_ui} skill is locked.")
                self._locked = True
            else:
                self._locked = False
        return self._locked

    @property
    def skill(self):
        """Skill ready image. Checking if it's not locked and ready to cast.

        :return: None or Image: image returned if skill is not locked and ready to cast.
        """
        if not self.locked and self._skill is None:
            self.check_skill_is_ready()
        return self._skill

    def check_skill_is_ready(self, max_repetitions=3, forced=False):
        """Check if skill is available and set it's image if it is.

        :param max_repetitions: max repetitions if "same" cooldown if skill cooldown is hard to read.
        :param forced: force to set skill available.
        """
        cool_down = self.player.get_screen_text(self.ui[self.skill_ui]) if not forced else False
        if cool_down:
            if cool_down in self.history:
                self.history[cool_down] += 1
            else:
                self.history[cool_down] = 1
            if self.history[cool_down] >= max_repetitions:
                logger.debug(f"Found text over {self.skill_ui} skill with {self.history[cool_down]} repetitions. "
                             f"Assuming that {self.skill_ui} is available.")
                cool_down = False
        if not cool_down:
            logger.debug(f"Found {self.skill_ui} skill image. Now available to cast.")
            self._skill = self.player.get_screen_image(rect=self.ui[self.skill_ui].rect)
            self.ui[self.skill_ui].image = self._skill
            self.ui[self.skill_ui].threshold = self.ui[self.skill_locked_ui].threshold

    def is_skill_available(self):
        """Check if skill is available to cast."""
        if self.skill is not None:
            return self.player.is_image_on_screen(self.ui[self.skill_ui])
        return False


class ManualBattleBot(BattleBot):
    """Class for working with manual battles."""

    def __init__(self, game):
        """Class initialization.

        :param game.Game game: instance of game.
        """
        super().__init__(game)
        self.skill_images = []
        self.current_character = None
        self.t3_skill = LockedSkill(game, skill_ui="SKILL_T3", skill_locked_ui="SKILL_T3_LOCKED",
                                    skill_label_ui="SKILL_T3_LABEL")
        self.skill_6 = LockedSkill(game, skill_ui="SKILL_6", skill_locked_ui="SKILL_6_LOCKED",
                                   skill_label_ui="SKILL_6_LABEL")

    def fight(self):
        """Start battle and use skills until the end of battle."""
        logger.info("Battle is started")
        first_time = False
        while not self.is_battle_over():
            if self.is_battle():
                if self.current_character is None:
                    self.load_character()
                if not self.skill_images:
                    self.load_skills()
                was_reloaded = self.reload_skills_if_character_dead()
                if first_time or was_reloaded:
                    best_available_skill = 5
                    first_time = False
                else:
                    best_available_skill = self.get_best_available_skill()
                if not best_available_skill:
                    time.sleep(0.1)
                    continue
                self.cast_skill(best_available_skill)
                time_to_sleep = 5 if best_available_skill in ["T3", "6"] else 1
                time.sleep(time_to_sleep)
            else:
                self.skip_cutscene()
        logger.info("Battle is over")

    def load_character(self):
        """Load character image."""
        logger.debug("Loading character image for the fight.")
        character_image = self.player.get_screen_image(rect=self.ui["CURRENT_CHARACTER"].rect)
        self.ui["CURRENT_CHARACTER"].image = character_image
        self.current_character = character_image

    def reload_skills_if_character_dead(self):
        """Reload skill info if current character is dead.

        :return True or False: was skills reloaded.
        """
        is_same_character = self.player.is_image_on_screen(ui_element=self.ui["CURRENT_CHARACTER"])
        if not is_same_character:
            logger.debug("Current character is dead. Switching to new one.")
            self.t3_skill = LockedSkill(self.game, skill_ui="SKILL_T3", skill_locked_ui="SKILL_T3_LOCKED",
                                        skill_label_ui="SKILL_T3_LABEL")
            self.skill_6 = LockedSkill(self.game, skill_ui="SKILL_6", skill_locked_ui="SKILL_6_LOCKED",
                                       skill_label_ui="SKILL_6_LABEL")
            self.load_character()
            self.load_skills()
            return True
        return False

    def load_skills(self):
        """Load images of skills without cooldown layout."""
        logger.debug("Loading skill's images for the fight.")
        for skill_id in range(1, 6):
            skill_image = self.player.get_screen_image(rect=self.ui[f"SKILL_{skill_id}"].rect)
            self.ui[f"SKILL_{skill_id}"].image = skill_image
            self.skill_images.append(skill_image)
        if not self.skill_6.locked:
            self.skill_6.check_skill_is_ready(forced=True)

    def is_skill_available(self, skill_id):
        """Check if skill is available to cast.
        
        :param skill_id: skill identifier.
        """
        return self.player.is_image_on_screen(self.ui[f"SKILL_{skill_id}"])

    def get_best_available_skill(self):
        """Get best available skill to cast.
        T3 -> 6 -> 5 -> 4 -> 3 -> 2 -> 1
        """
        if self.t3_skill.is_skill_available():
            return "T3"
        if self.skill_6.is_skill_available():
            return "6"
        for skill_id in reversed(range(1, 6)):
            if self.is_skill_available(skill_id=skill_id):
                return skill_id

    def cast_skill(self, skill_id, max_attempts=3):
        """Cast character's skill.

        :param skill_id: skill identifier.
        :param max_attempts: max attempts of trying to cast skill.

        :return: was skill casted.
        """
        logger.debug(f"Casting {skill_id}-th skill.")
        skill_ui = self.ui[f'SKILL_{skill_id}']
        self.player.click_button(skill_ui.button)
        attempts = 1
        time.sleep(0.05)
        while self.is_skill_available(skill_id) and self.is_battle():
            if attempts > max_attempts:
                return False
            else:
                attempts += 1
                self.player.click_button(skill_ui.button)
                time.sleep(0.05)
        return True

    def skip_cutscene(self):
        """Skip battle cutscene."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['SKIP_CUTSCENE']):
            logger.debug("Skipping cutscene.")
            self.player.click_button(self.ui['SKIP_CUTSCENE'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=0.2, period=0.1,
                      ui_element=self.ui['SKIP_TAP_THE_SCREEN']):
            logger.debug("Skipping TAP THE SCREEN.")
            self.player.click_button(self.ui['SKIP_TAP_THE_SCREEN'].button)
