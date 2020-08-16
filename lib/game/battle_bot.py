import lib.logger as logging
from itertools import cycle
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class BattleBot:
    """Class for working with game battles."""

    def __init__(self, game, battle_over_conditions, disconnect_conditions=None):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.game = game
        self.ui = game.ui
        self.player = game.player
        self._is_battle_cached = None
        self._battle_over_conditions = battle_over_conditions if battle_over_conditions else []
        self._disconnect_conditions = disconnect_conditions if disconnect_conditions else []

    def is_battle(self):
        """Check if battle is going.

        :return: True or False.
        """
        is_battle = self.player.is_image_on_screen(self.ui['MELEE_BUTTON'])
        self._is_battle_cached = is_battle
        return is_battle

    def is_battle_over(self):
        """Check if battle is over.

        :return: True or False.
        """
        for condition in self._disconnect_conditions:
            if condition():
                return True
        is_battle = self.is_battle() if not self._is_battle_cached else self._is_battle_cached
        if not is_battle:
            for condition in self._battle_over_conditions:
                if condition():
                    return True
        self._is_battle_cached = None
        return False

    def skip_cutscene(self):
        """Skip battle cutscene."""
        if self.player.is_ui_element_on_screen(ui_element=self.ui['SKIP_CUTSCENE']):
            logger.debug("Skipping cutscene.")
            self.player.click_button(self.ui['SKIP_CUTSCENE'].button)
        if wait_until(self.player.is_ui_element_on_screen, timeout=0.2, period=0.1,
                      ui_element=self.ui['SKIP_TAP_THE_SCREEN']):
            logger.debug("Skipping TAP THE SCREEN.")
            self.player.click_button(self.ui['SKIP_TAP_THE_SCREEN'].button)


class AutoBattleBot(BattleBot):
    """Class for working with AutoPlay battles."""

    def fight(self):
        """Start battle and wait until the end."""
        if wait_until(self.is_battle, timeout=60, period=1):
            logger.info("Battle is started")
        else:
            logger.warning("Can't find MELEE button on screen after starting a battle.")
        if not wait_until(self.player.is_image_on_screen, timeout=2, ui_element=self.ui['AUTOPLAY_TOGGLE']):
            logger.debug("Found AUTO PLAY toggle inactive. Clicking it.")
            self.player.click_button(self.ui['AUTOPLAY_TOGGLE'].button)
        while not self.is_battle_over():
            if self.is_battle():
                r_sleep(0.75)
            else:
                self.skip_cutscene()
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
                r_sleep(0.25)
        logger.debug("Shifter didn't appeared.")
        return False


class LockedSkill:
    """Class for working with locked skills (T3 and Awakening skills)."""

    def __init__(self, game, skill_ui, skill_locked_ui, skill_label_ui):
        """Class initialization.

        :param game.Game game: instance of game.
        """
        self.ui = game.ui
        self.player = game.player
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
            elif self.player.is_image_on_screen(ui_element=self.ui['SKILL_T3_LOCKED']) or \
                    self.player.is_image_on_screen(ui_element=self.ui['SKILL_6_LOCKED']):
                logger.debug(f"{self.skill_ui} skill is locked.")
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
        if not cool_down and not forced:
            cool_down = "EMPTY"
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
            if self.ui[self.skill_ui].image is None:
                logger.debug(f"Got {self.skill_ui} skill image from screen. Now available to cast.")
                self._skill = self.player.get_screen_image(rect=self.ui[self.skill_ui].rect)
                self.ui[self.skill_ui].image = self._skill
                self.ui[self.skill_ui].threshold = self.ui[self.skill_locked_ui].threshold
            elif self.player.is_image_on_screen(self.ui[self.skill_ui]):
                logger.debug(f"Found {self.skill_ui} skill image on screen. Now available to cast.")
                self._skill = self.ui[self.skill_ui].image
            else:
                logger.debug(f"No images of {self.skill_ui} skill on screen, locking.")
                self._locked = True

    def is_skill_available(self):
        """Check if skill is available to cast."""
        if self.skill is not None:
            return self.player.is_image_on_screen(self.ui[self.skill_ui])
        return False


class ManualBattleBot(BattleBot):
    """Class for working with manual battles."""

    DEFAULT_SKILL = 5  # best non locked skill
    T3_SKILL = "T3"
    AWAKENING_SKILL = "6"
    COOP_SKILL = "COOP"
    SKILL_TIMEOUTS = {
        "1": 1, "2": 1, "3": 1,
        "4": 1.5,
        "5": 2,
        "6": 6, "T3": 6,
        "COOP": 0
    }

    def __init__(self, game, battle_over_conditions, disconnect_conditions=None):
        """Class initialization.

        :param game.Game game: instance of game.
        """
        super().__init__(game, battle_over_conditions, disconnect_conditions)
        self.skill_images = []
        self.current_character = None
        self.t3_skill = LockedSkill(self.game, skill_ui="SKILL_T3", skill_locked_ui="SKILL_T3_LOCKED",
                                    skill_label_ui="SKILL_T3_LABEL")
        self.awakening_skill = LockedSkill(self.game, skill_ui="SKILL_6", skill_locked_ui="SKILL_6_LOCKED",
                                           skill_label_ui="SKILL_6_LABEL")
        self.coop_skill = LockedSkill(self.game, skill_ui="SKILL_COOP", skill_locked_ui="SKILL_COOP",
                                      skill_label_ui=None)
        self.cached_available_skill = self.DEFAULT_SKILL
        self.moving_positions = cycle(["MOVE_AROUND_POS_DOWN", "MOVE_AROUND_POS_LEFT",
                                       "MOVE_AROUND_POS_UP", "MOVE_AROUND_POS_RIGHT"])
        self.moving_position_from = next(self.moving_positions)
        self.shadowland_loaded = False

    def fight(self, move_around=False):
        """Start battle and use skills until the end of battle.

        :param move_around: move around if skills are unavailable to cast.
        """
        logger.info("Battle is started")
        while not self.is_battle_over():
            if self.is_battle():
                if self.current_character is None:
                    self.load_character()
                if not self.skill_images:
                    self.load_skills()
                if self.reload_skills_if_character_dead():
                    self.cached_available_skill = self.DEFAULT_SKILL

                best_available_skill = self.get_best_available_skill()
                if not best_available_skill:
                    continue
                if self.cast_skill(best_available_skill):
                    logger.debug(f"Successfully casted {best_available_skill} skill.")
                    time_to_sleep = self.SKILL_TIMEOUTS[str(best_available_skill)]
                    r_sleep(time_to_sleep)
                else:
                    self.cached_available_skill = self.DEFAULT_SKILL
                    if move_around:
                        self.move_character()
                        self.move_character()
            else:
                self.skip_cutscene()
                self.shadowland_loaded = False
        logger.info("Battle is over")

    def move_character(self):
        """Move character around."""
        logger.debug("Moving around.")
        next_position_from, next_position_to = self.moving_position_from, next(self.moving_positions)
        self.player.drag(from_rect=self.ui[next_position_from].button, to_rect=self.ui[next_position_to].button,
                         duration=0.5)
        self.moving_position_from = next_position_to

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
            self.awakening_skill = LockedSkill(self.game, skill_ui="SKILL_6", skill_locked_ui="SKILL_6_LOCKED",
                                               skill_label_ui="SKILL_6_LABEL")
            self.load_character()
            self.load_skills()
            return True
        return False

    def load_skills(self):
        """Load images of skills without cooldown layout."""
        if self.player.is_ui_element_on_screen(self.ui['SHADOWLAND_FLOOR']) and not self.shadowland_loaded:
            logger.debug("Shadowland's floor was found. Awaiting start battle animation.")
            self.shadowland_loaded = True
            r_sleep(4)
        logger.debug("Loading skill's images for the fight.")
        t3_badge = self.game.player.is_image_on_screen(self.game.ui['T3_BADGE_1']) or \
                   self.game.player.is_image_on_screen(self.game.ui['T3_BADGE_2'])
        for skill_id in range(1, 6):
            skill_image = self.player.get_screen_image(rect=self.ui[f"SKILL_{skill_id}"].rect)
            self.ui[f"SKILL_{skill_id}"].image = skill_image
            self.skill_images.append(skill_image)
        if not self.awakening_skill.locked and not t3_badge:
            logger.debug("Cannot find T3 badge on character's icon. Assuming 6th skill as Awakening.")
            self.awakening_skill.check_skill_is_ready(forced=True)
            self.cached_available_skill = self.AWAKENING_SKILL
            self.t3_skill._locked = True
        if not self.t3_skill.locked and t3_badge:
            logger.debug("Found T3 badge on character's icon. Assuming 6th skill as T3.")
            self.awakening_skill._locked = True
        if not self.awakening_skill.locked and not self.t3_skill.locked:
            logger.warning("Two skills on the same position are not locked. Something wrong, assuming 6th skill as T3.")
            self.t3_skill._locked = False
            self.awakening_skill._locked = True

        self.coop_skill._locked = self.player.is_image_on_screen(ui_element=self.ui['SKILL_COOP'])
        self.coop_skill.check_skill_is_ready(forced=True)

    def is_skill_available(self, skill_id):
        """Check if skill is available to cast.

        :param skill_id: skill identifier.
        """
        return self.player.is_image_on_screen(self.ui[f"SKILL_{skill_id}"])

    def get_best_available_skill(self):
        """Get best available skill to cast.
        cached skill -> T3 -> 6 -> COOP -> 5 -> 4 -> 3 -> 2 -> 1
        """
        if self.cached_available_skill and self.is_skill_available(skill_id=self.cached_available_skill):
            skill = self.cached_available_skill
            self.cached_available_skill = None
            return skill
        if self.t3_skill.is_skill_available():
            return self.T3_SKILL
        if self.awakening_skill.is_skill_available():
            return self.AWAKENING_SKILL
        if self.coop_skill.is_skill_available():
            return self.COOP_SKILL
        for skill_id in reversed(range(1, 6)):
            if self.is_skill_available(skill_id=skill_id):
                return skill_id

    def cast_skill(self, skill_id):
        """Cast character's skill.

        :param skill_id: skill identifier.
        :return: was skill casted.
        """
        logger.debug(f"Casting {skill_id}-th skill.")
        skill_ui = self.ui[f'SKILL_{skill_id}']
        self.player.click_button(skill_ui.button, min_duration=0.01, max_duration=0.01)
        self.player.click_button(skill_ui.button, min_duration=0.03, max_duration=0.03)
        self.player.click_button(skill_ui.button, min_duration=0.1, max_duration=0.1)
        return not self.is_skill_available(skill_id=skill_id)
