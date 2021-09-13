import re
import lib.logger as logging
from itertools import cycle
from lib.functions import wait_until, r_sleep, confirm_condition_by_time

logger = logging.get_logger(__name__)
t3_percentage_regexp = re.compile(r"([0-9][0-9]?\.?[0-9]? ?%?)")


class BattleBot:
    """Class for working with game battles."""

    def __init__(self, game, battle_over_conditions, disconnect_conditions=None):
        """Class initialization.

        :param game.Game game: instance of the game.
        """
        self.game = game
        self.ui = game.ui
        self.emulator = game.emulator
        self._is_battle_cached = None
        self._disconnected = False
        self._battle_over_conditions = battle_over_conditions if battle_over_conditions else []
        self._disconnect_conditions = disconnect_conditions if disconnect_conditions else []
        self._skip_tap_screen_high = self.ui['SKIP_TAP_THE_SCREEN'].copy()
        self._skip_tap_screen_high.threshold += 20
        self._skip_tap_screen_low = self.ui['SKIP_TAP_THE_SCREEN'].copy()
        self._skip_tap_screen_low.threshold -= 20

    def is_battle(self):
        """Check if battle is going.

        :return: True or False.
        """
        is_battle = self.emulator.is_image_on_screen(self.ui['MELEE_BUTTON'])
        self._is_battle_cached = is_battle
        return is_battle

    def is_battle_over(self):
        """Check if battle is over.

        :return: True or False.
        """
        for condition in self._disconnect_conditions:
            if condition():
                self._disconnected = True
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
        if self.emulator.is_ui_element_on_screen(ui_element=self.ui['SKIP_CUTSCENE']):
            logger.debug("Skipping cutscene.")
            self.emulator.click_button(self.ui['SKIP_CUTSCENE'].button)
        self.skip_tap_the_screen()
        self.skip_frost_beast()

    def skip_tap_the_screen(self):
        """Skip TAP SCREEN battle cutscene."""
        if self.emulator.is_ui_element_on_screen(ui_element=self.ui['SKIP_CUTSCENE']) or \
                self.emulator.is_ui_element_on_screen(ui_element=self._skip_tap_screen_high) or \
                self.emulator.is_ui_element_on_screen(ui_element=self._skip_tap_screen_low):
            logger.debug("Skipping TAP THE SCREEN.")
            self.emulator.click_button(self.ui['SKIP_TAP_THE_SCREEN'].button)

    def skip_frost_beast(self):
        """SKip Frost Beast cutscene."""
        if self.emulator.is_ui_element_on_screen(ui_element=self.ui['AB_FROST_BEAST_BATTLE_LABEL']):
            logger.debug("Skipping Frost Beast.")
            self.emulator.click_button(self.ui['AB_FROST_BEAST_BATTLE_LABEL'].button)


class AutoBattleBot(BattleBot):
    """Class for working with AutoPlay battles."""

    _30_FPS = 1.0 / 30  # Awaiting for frame in 30FPS

    def fight(self):
        """Start battle and wait until the end."""
        if confirm_condition_by_time(confirm_condition=self.is_battle_over):
            logger.info("Battle is already over")
            return

        def wait_battle():
            self.skip_cutscene()
            return self.is_battle()

        if wait_until(wait_battle, timeout=60, period=1):
            logger.info("Battle is started")
        else:
            logger.warning("Can't find MELEE button on screen after starting a battle.")
        if not wait_until(self.emulator.is_image_on_screen, timeout=2, ui_element=self.ui['AUTOPLAY_TOGGLE']):
            logger.debug("Found AUTO PLAY toggle inactive. Clicking it.")
            self.emulator.click_button(self.ui['AUTOPLAY_TOGGLE'].button)
        while not self.is_battle_over():
            if not self.is_battle():
                self.skip_cutscene()
            r_sleep(self._30_FPS)
        r_sleep(1)  # Wait for end of the battle animations
        if self._disconnected:
            logger.debug("Disconnect condition was triggered.")
            return
        # Check for possible notifications after end of the battle
        if not wait_until(confirm_condition_by_time, confirm_condition=self.is_battle_over, timeout=10):
            return self.fight()
        logger.info("Battle is over")

    def wait_until_shifter_appeared(self):
        """Wait until Ally or Enemy shifter appears."""
        logger.debug("Waiting for Shifter to appear.")
        while not self.is_battle():
            shifter_appeared = self.emulator.is_ui_element_on_screen(ui_element=self.ui['ALLY_APPEARED']) or \
                               self.emulator.is_ui_element_on_screen(ui_element=self.ui['ENEMY_APPEARED']) or \
                               self.emulator.is_ui_element_on_screen(ui_element=self.ui['ALLY_AND_ENEMY_APPEARED']) or \
                               self.emulator.is_ui_element_on_screen(ui_element=self.ui['ENEMY_AND_ALLY_APPEARED'])
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
        self.emulator = game.emulator
        self._skill_locked = None
        self._skill_ready_image = None
        self.history = {}
        self.skill_ui = self.ui[skill_ui].copy() if self.ui.get(skill_ui) else None
        if isinstance(skill_locked_ui, str):
            skill_locked_ui = [skill_locked_ui]
        self.skill_locked_ui = [self.ui[name].copy() for name in skill_locked_ui if
                                self.ui.get(name)] if skill_locked_ui else None
        self.skill_label_ui = self.ui[skill_label_ui].copy() if self.ui.get(skill_label_ui) else None
        self.name = "_".join(self.skill_ui.name.split("_")[1:])

    @property
    def locked(self):
        """Is skill locked property. Checking if locked version of the skill is on screen and storing result."""
        if self._skill_locked is None:
            if self.skill_label_ui and not self.emulator.is_ui_element_on_screen(ui_element=self.skill_label_ui):
                logger.debug(f"{self.name} skill label is not on a screen. Character does not have him.")
                self._skill_locked = True
            elif self.skill_locked_ui:
                for locked_ui in self.skill_locked_ui:
                    if locked_ui and self.emulator.is_image_on_screen(locked_ui):
                        logger.debug(f"{self.name} skill is locked.")
                        self._skill_locked = True
                        return self._skill_locked
                self._skill_locked = False
            else:
                self._skill_locked = False
        return self._skill_locked

    @property
    def skill_image(self):
        """Skill ready image. Checking if it's not locked and ready to cast.

        :return: None or Image: image returned if skill is not locked and ready to cast.
        """
        if not self.locked and self._skill_ready_image is None:
            self.check_skill_is_ready()
        return self._skill_ready_image

    def is_not_locked_and_has_skill_image(self):
        """Check if skill is not locked and has skill image ready to cast."""
        return not self.locked and self._skill_ready_image is not None

    def check_skill_is_ready(self, max_repetitions=3, forced=False):
        """Check if skill is available and set it's image if it is.

        :param max_repetitions: max repetitions if "same" cooldown if skill cooldown is hard to read.
        :param forced: force to set skill available.
        """
        cool_down = self.emulator.get_screen_text(self.skill_ui) if not forced else False
        if not cool_down and not forced:
            cool_down = "EMPTY"
        if cool_down:
            if cool_down in self.history:
                self.history[cool_down] += 1
            else:
                self.history[cool_down] = 1
            if self.history[cool_down] >= max_repetitions:
                logger.debug(f"Found text over {self.name} skill with {self.history[cool_down]} repetitions. "
                             f"Assuming that {self.name} is available.")
                cool_down = False
        if not cool_down:
            if self.skill_ui.image is None:
                logger.debug(f"Got {self.name} skill image from screen. Now available to cast.")
                self._skill_ready_image = self.emulator.get_screen_image(rect=self.skill_ui.rect)
                self.skill_ui.image = self._skill_ready_image
                self.skill_ui.threshold = self.skill_locked_ui[0].threshold if self.skill_locked_ui else 0.8
            elif self.emulator.is_image_on_screen(self.skill_ui):
                logger.debug(f"Found {self.name} skill image on screen. Now available to cast.")
                self._skill_ready_image = self.skill_ui.image
                self._skill_locked = False
            else:
                logger.debug(f"No images of {self.name} skill on screen, locking.")
                self._skill_locked = True

    def is_skill_available(self):
        """Check if skill is available to cast."""
        if self.skill_image is not None:
            return self.emulator.is_image_on_screen(self.skill_ui)
        return False

    def cast_skill(self):
        """Cast character's skill.

        :return: was skill casted.
        """
        logger.debug(f"Casting {self.name} skill.")
        self.emulator.click_button(self.skill_ui.button, min_duration=0.01, max_duration=0.01)
        self.emulator.click_button(self.skill_ui.button, min_duration=0.03, max_duration=0.03)
        self.emulator.click_button(self.skill_ui.button, min_duration=0.1, max_duration=0.1)
        return not self.is_skill_available()


class ManualBattleBot(BattleBot):
    """Class for working with manual battles."""

    SKILL_TIMEOUTS = {
        "1": 1, "2": 1, "3": 1,
        "4": 1.5,
        "5": 2,
        "6": 6, "T3": 6
    }

    def __init__(self, game, battle_over_conditions, disconnect_conditions=None):
        """Class initialization.

        :param game.Game game: instance of game.
        """
        super().__init__(game, battle_over_conditions, disconnect_conditions)
        self._init_skills()
        self.current_character = None
        self.BEST_DEFAULT_SKILL = None
        self.cached_available_skill = None
        self.moving_positions = cycle(["MOVE_AROUND_POS_DOWN", "MOVE_AROUND_POS_LEFT",
                                       "MOVE_AROUND_POS_UP", "MOVE_AROUND_POS_RIGHT"])
        self.moving_position_from = next(self.moving_positions)

    def _init_base_skills(self):
        self.skill_1 = LockedSkill(self.game, "SKILL_1", skill_label_ui=None, skill_locked_ui=None)
        self.skill_2 = LockedSkill(self.game, "SKILL_2", skill_label_ui="SKILL_2_LABEL", skill_locked_ui=None)
        self.skill_3 = LockedSkill(self.game, "SKILL_3", skill_label_ui="SKILL_3_LABEL", skill_locked_ui=None)
        self.skill_4 = LockedSkill(self.game, "SKILL_4", skill_label_ui="SKILL_4_LABEL", skill_locked_ui=None)
        self.skill_5 = LockedSkill(self.game, "SKILL_5", skill_label_ui="SKILL_5_LABEL", skill_locked_ui=None)
        self.base_skills = [self.skill_1, self.skill_2, self.skill_3, self.skill_4, self.skill_5]

    def _init_skills(self):
        self._init_base_skills()
        self.current_bonus_skill = None
        self.t3_skill = LockedSkill(self.game, "SKILL_T3", ["SKILL_T3_LOCKED", "SKILL_6_LOCKED"], "SKILL_T3_LABEL")
        self.awakening_skill = LockedSkill(self.game, "SKILL_6", ["SKILL_6_LOCKED", "SKILL_T3_LOCKED"], "SKILL_6_LABEL")
        self.coop_skill = LockedSkill(self.game, "SKILL_COOP", skill_locked_ui=None, skill_label_ui=None)
        self.danger_room_skill = LockedSkill(self.game, "SKILL_DANGER_ROOM", skill_locked_ui=None, skill_label_ui=None)

    def fight(self, move_around=False):
        """Start battle and use skills until the end of battle.

        :param move_around: move around if skills are unavailable to cast.
        """
        logger.info("Battle is started")
        while not self.is_battle_over():
            if self.is_battle():
                if self.current_character is None:
                    self.load_character()
                    self.load_skills()
                self.reload_skills_if_character_dead()
                if self.get_available_bonus_skill():
                    self.current_bonus_skill.cast_skill()

                best_available_skill = self.get_best_available_skill()
                if not best_available_skill:
                    continue
                if best_available_skill.cast_skill():
                    logger.debug(f"Successfully casted {best_available_skill.name} skill.")
                    time_to_sleep = self.SKILL_TIMEOUTS[str(best_available_skill.name)]
                    r_sleep(time_to_sleep)
                    # Check T3 and bonus skill only after successful cast
                    if not self.t3_skill.locked and not self.t3_skill.is_not_locked_and_has_skill_image():
                        self.t3_skill.check_skill_is_ready()
                    if self.current_bonus_skill and not self.current_bonus_skill.locked:  # Check pseudo lock
                        if not self.current_bonus_skill.is_not_locked_and_has_skill_image():
                            self.current_bonus_skill.check_skill_is_ready()
                else:
                    self.cached_available_skill = self.BEST_DEFAULT_SKILL
                    if move_around:
                        self.move_character()
                        self.move_character()
            else:
                self.skip_cutscene()
                r_sleep(0.75)
        r_sleep(1)  # Wait for end of the battle animations
        logger.info("Battle is over")

    def move_character(self):
        """Move character around."""
        logger.debug("Moving around.")
        next_position_from, next_position_to = self.moving_position_from, next(self.moving_positions)
        self.emulator.drag(from_rect=self.ui[next_position_from].button, to_rect=self.ui[next_position_to].button,
                           duration=0.5)
        self.moving_position_from = next_position_to

    def load_character(self):
        """Load character image."""
        logger.debug("Loading character image for the fight.")
        character_image = self.emulator.get_screen_image(rect=self.ui["CURRENT_CHARACTER"].rect)
        self.ui["CURRENT_CHARACTER"].image = character_image
        self.current_character = character_image

    def reload_skills_if_character_dead(self):
        """Reload skill info if current character is dead.

        :return True or False: was skills reloaded.
        """
        is_same_character = self.emulator.is_image_on_screen(ui_element=self.ui["CURRENT_CHARACTER"])
        if not is_same_character:
            logger.debug("Current character is dead. Switching to new one.")
            r_sleep(1.1, radius_modifier=1.0)  # Wait for skill "reload" animation
            self._init_skills()
            self.load_character()
            self.load_skills()
            return True
        return False

    def load_skills(self):
        """Load images of skills without cooldown layout."""
        logger.debug("Loading skill's images for the fight.")
        for skill in self.base_skills:
            if not skill.locked:
                skill.check_skill_is_ready(forced=True)
                self.cached_available_skill = skill

        if not self.awakening_skill.locked or self.t3_skill.locked:
            t3_percentage_text = self.emulator.get_screen_text(self.t3_skill.skill_ui)
            is_t3 = t3_percentage_regexp.fullmatch(t3_percentage_text)
            if not self.awakening_skill.locked and not is_t3:
                logger.debug(f"Cannot find T3 percentage (got {t3_percentage_text}). Assuming 6th skill as Awakening.")
                self.awakening_skill.check_skill_is_ready(forced=True)
                self.cached_available_skill = self.awakening_skill
                self.t3_skill._skill_locked = True
            if not self.t3_skill.locked and is_t3:
                logger.debug(f"Found T3 percentage on skill = {t3_percentage_text}. Assuming 6th skill as T3.")
                self.awakening_skill._skill_locked = True
            if not self.awakening_skill.locked and not self.t3_skill.locked:
                logger.warning("Two skills on the same position are not locked. "
                               "Something wrong, assuming 6th skill as T3.")
                self.t3_skill._skill_locked = False
                self.awakening_skill._skill_locked = True

        self.BEST_DEFAULT_SKILL = self.cached_available_skill

        non_locked_skill_found = False
        for skill in reversed(self.base_skills):
            if not skill.locked:
                non_locked_skill_found = True
            if skill.locked and non_locked_skill_found:
                logger.debug(f"Skill {skill.name} in between was found as locked. Something interrupt skill loading."
                             f"Reloading skills again.")
                self._init_base_skills()
                r_sleep(1)
                return self.load_skills()

        locked_base_skills = [skill for skill in self.base_skills if skill.locked]
        unlocked_base_skills = [skill for skill in self.base_skills if not skill.locked]
        if locked_base_skills and unlocked_base_skills:
            last_skill = unlocked_base_skills[-1]
            last_skill._skill_locked = True
            last_skill._skill_ready_image = None
            logger.debug(f"Locking base skill {last_skill.name} because previous skills locked as well.")

    def get_available_bonus_skill(self):
        """Get available bonus skill and save it.

        :return: LockedSkill available bonus skill to cast.
        """
        if self.current_bonus_skill is None:
            self.current_bonus_skill = False  # Pseudo lock skill of no COOP or Danger Room
            self.coop_skill.check_skill_is_ready(forced=True)
            if self.coop_skill.is_not_locked_and_has_skill_image():
                self.current_bonus_skill = self.coop_skill
            else:
                percentage_text = self.emulator.get_screen_text(self.danger_room_skill.skill_ui)
                is_danger_room = t3_percentage_regexp.fullmatch(percentage_text)
                if is_danger_room:
                    logger.debug(f"Found percentage on Danger Room skill = {percentage_text}.")
                    self.current_bonus_skill = self.danger_room_skill

        if self.current_bonus_skill and self.current_bonus_skill.is_not_locked_and_has_skill_image():
            if self.current_bonus_skill.is_skill_available():
                return self.current_bonus_skill

    def get_best_available_skill(self):
        """Get best available skill to cast.
        cached skill -> T3 -> 6 -> 5 -> 4 -> 3 -> 2 -> 1

        :return: LockedSkill best available skill to cast.
        """
        if self.cached_available_skill and self.cached_available_skill.is_skill_available():
            skill = self.cached_available_skill
            self.cached_available_skill = None
            return skill
        if self.t3_skill.is_not_locked_and_has_skill_image() and self.t3_skill.is_skill_available():
            return self.t3_skill
        if self.awakening_skill.is_skill_available():
            return self.awakening_skill
        for skill in reversed(self.base_skills):
            if skill.is_skill_available():
                return skill
