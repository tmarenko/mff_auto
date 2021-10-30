import regex

import lib.logger as logging
from lib.functions import wait_until
from lib.game import ui
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)


class ComicCards(Notifications):
    """Class for working with Comic Cards."""

    def upgrade_all_cards(self):
        """Upgrades all available Comic Cards."""
        self.game.go_to_comic_cards()
        logger.info("Comic Cards: upgrading all available cards.")
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CARDS_UPGRADE_ALL):
            self.emulator.click_button(ui.CARDS_UPGRADE_ALL)
            for card_index in range(1, 6):
                card_select_ui = ui.get_by_name(f'CARDS_SELECT_GRADE_{card_index}')
                self.emulator.click_button(card_select_ui)
                logger.debug(f"Comic Cards: starting to upgrade UI Element {card_select_ui}")
                if not wait_until(self.emulator.is_image_on_screen, ui_element=card_select_ui):
                    logger.warning("Comic Cards: can't select card's grade.")
                    continue
                logger.debug(f"Comic Cards: successfully selected UI Element {card_select_ui}")
                self.emulator.click_button(ui.CARDS_SELECT_GRADE)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CARDS_UPGRADE_CONFIRM):
                    self.emulator.click_button(ui.CARDS_UPGRADE_CONFIRM)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=10,
                                  ui_element=ui.CARDS_UPGRADE_RESULTS_OK):
                        logger.debug(f"Comic Cards: successfully upgraded UI Element {card_select_ui}")
                        self.emulator.click_button(ui.CARDS_UPGRADE_RESULTS_OK)
                        wait_until(self.emulator.is_image_on_screen, ui_element=card_select_ui)
                        continue
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CARDS_UPGRADE_ALL_CANCEL):
            self.emulator.click_button(ui.CARDS_UPGRADE_ALL_CANCEL)
            self.close_after_mission_notifications()
            self.game.go_to_main_menu()


class CustomGear(Notifications):
    """Class for working with Custom Gear."""

    def __init__(self, game):
        """Class initialization.

        :param lib.game.game.Game game: instance of the game.
        """
        super().__init__(game)
        self.is_quick_toggle = None

    def quick_upgrade_gear(self, times=0):
        """Upgrades custom gear via `Quick Upgrade` function.

        :param times: how many times to upgrade.
        """
        self.game.go_to_inventory()
        logger.info(f"Custom Gear: upgrading gear {times} times.")
        self.emulator.click_button(ui.INVENTORY_UPGRADE_TAB)
        self.emulator.click_button(ui.INVENTORY_CUSTOM_GEAR_TAB)
        if not wait_until(self.is_custom_gear_tab, timeout=3, period=1):
            logger.error("Can't get into Custom Gear tab.")
            return self.game.go_to_main_menu()
        if not self.try_to_select_gear_for_upgrade():
            logger.warning("Custom Gear: can't select gear for upgrade, probably you have none, exiting.")
            return self.game.go_to_main_menu()
        if not self.toggle_quick_upgrade():
            logger.error(f"Custom Gear: can't find {ui.CUSTOM_GEAR_QUICK_UPGRADE} button, exiting.")
            return self.game.go_to_main_menu()
        for _ in range(times):
            if not self.try_to_select_gear_for_upgrade():
                logger.warning("Custom Gear: can't select gear for upgrade, probably you have none, exiting.")
                self.game.go_to_main_menu()
                break
            self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CUSTOM_GEAR_QUICK_UPGRADE_CONFIRM):
                logger.debug("Custom Gear: confirming upgrading.")
                self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE_CONFIRM)
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.CUSTOM_GEAR_QUICK_UPGRADE_INCLUDE_UPGRADED):
                    logger.debug("Custom Gear: confirming to use upgraded gear.")
                    self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE_INCLUDE_UPGRADED)
                self.close_upgrade_result()
            else:
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.CUSTOM_GEAR_NO_MATERIALS):
                    logger.info("Custom Gear: you have no materials for gear upgrade.")
                    self.emulator.click_button(ui.CUSTOM_GEAR_NO_MATERIALS)
                    break

        # `self.is_quick_toggle is False` not working o_O
        if self.is_quick_toggle is not None and not self.is_quick_toggle:
            logger.debug("Custom Gear: returning Quick Upgrade toggle to inactive.")
            self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE)
        self.game.go_to_main_menu()

    def is_custom_gear_tab(self):
        """Checks if Custom Gear tab is opened."""
        return self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE) or \
               self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_ENHANCE) or \
               self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_CHANGE_OPTION)

    def toggle_quick_upgrade(self):
        """Toggles Quick Upgrade toggle."""
        self.is_quick_toggle = self.emulator.is_image_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE)
        if not self.is_quick_toggle:
            logger.debug("Custom Gear: found Quick Upgrade toggle inactive. Clicking it.")
            self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE)
            wait_until(self.emulator.is_image_on_screen, ui_element=ui.CUSTOM_GEAR_QUICK_UPGRADE_TOGGLE)
        return self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE)

    def close_upgrade_result(self):
        """Closes upgrade's result notification."""

        def is_results_window():
            return self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1) or \
                   self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2)

        if wait_until(is_results_window, timeout=10):
            if self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1):
                self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_1)
            if self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2):
                self.emulator.click_button(ui.CUSTOM_GEAR_QUICK_UPGRADE_RESULTS_2)
            self.close_after_mission_notifications()
        if is_results_window() or not self.emulator.is_ui_element_on_screen(ui.INVENTORY_CONVERT_BUTTON):
            return self.close_upgrade_result()
        logger.debug("Custom Gear: successfully upgraded custom gear.")

    def try_to_select_gear_for_upgrade(self):
        """Tries to select gear for upgrade from inventory."""
        if self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_CHANGE_OPTION):
            self.emulator.click_button(ui.CUSTOM_GEAR_1)
        return not self.emulator.is_ui_element_on_screen(ui.CUSTOM_GEAR_CHANGE_OPTION)


class Iso8(Notifications):
    """Class for working with ISO-8."""

    INVENTORY_ROW = 3
    INVENTORY_COL = 6

    class ISO8_TYPE:
        POWERFUL = "ISO8_POWERFUL_TAB"
        AMPLIFYING = "ISO8_AMPLIFYING_TAB"
        IMPREGNABLE = "ISO8_IMPREGNABLE_TAB"
        ABSORBING = "ISO8_ABSORBING_TAB"
        VITAL = "ISO8_VITAL_TAB"
        FIERCE = "ISO8_FIERCE_TAB"
        NIMBLE = "ISO8_NIMBLE_TAB"
        CHAOTIC = "ISO8_CHAOTIC_TAB"

    class ISO8_TYPE_TO_USE:
        POWERFUL = "ISO8_POWERFUL_ENHANCE"
        AMPLIFYING = "ISO8_AMPLIFYING_ENHANCE"
        IMPREGNABLE = "ISO8_IMPREGNABLE_ENHANCE"
        ABSORBING = "ISO8_ABSORBING_ENHANCE"
        VITAL = "ISO8_VITAL_ENHANCE"
        FIERCE = "ISO8_FIERCE_ENHANCE"
        NIMBLE = "ISO8_NIMBLE_ENHANCE"
        CHAOTIC = "ISO8_CHAOTIC_ENHANCE"
        BOOST = "ISO8_BOOST_ENHANCE"

    class ISO8_STARS_TO_USE:
        STAR_1 = "ISO8_ENHANCE_1_STAR"
        STAR_2 = "ISO8_ENHANCE_2_STAR"
        STAR_3 = "ISO8_ENHANCE_3_STAR"
        STAR_4 = "ISO8_ENHANCE_4_STAR"
        STAR_5 = "ISO8_ENHANCE_5_STAR"
        STAR_6 = "ISO8_ENHANCE_6_STAR"

    class ISO8_LOCK:
        ALL_ATTACK = "(ALL BASIC ATTACKS INCREASE){e<=3}.*"
        PHYSICAL_ATTACK = "(PHYSICAL ATTACK){e<=3}.*"
        ENERGY_ATTACK = "(ENERGY ATTACK){e<=3}.*"
        ALL_DEFENCE = "(ALL BASIC DEFENCES INCREASE){e<=3}.*"
        PHYSICAL_DEFENCE = "(PHYSICAL DEFENCE){e<=3}.*"
        ENERGY_DEFENCE = "(ENERGY DEFENCE){e<=3}.*"
        HP = "(HP).*"
        CRITICAL_RATE = "(CRITICAL RATE){e<=3}.*"
        DODGE = "(DODGE).*"
        ALL_ATTACK_AND_ALL_DEFENCE = f"{ALL_ATTACK}\\n{ALL_DEFENCE}"
        ALL_ATTACK_AND_HP = f"{ALL_ATTACK}\\n{HP}"
        PHYSICAL_ATTACK_AND_HP = f"{PHYSICAL_ATTACK}\\n{HP}"
        ENERGY_ATTACK_AND_HP = f"{ENERGY_ATTACK}\\n{HP}"

        @classmethod
        def multi_line(cls):
            return (cls.ALL_ATTACK_AND_ALL_DEFENCE, cls.ALL_ATTACK_AND_HP, cls.PHYSICAL_ATTACK_AND_HP,
                    cls.ENERGY_ATTACK_AND_HP)

    def open_iso8_tab(self):
        """Opens ISO-8 tab in Inventory."""

        def is_iso8_tab() -> bool:
            return self.emulator.is_ui_element_on_screen(ui.ISO8_QUICK_UPGRADE) or \
                   self.emulator.is_ui_element_on_screen(ui.ISO8_CHANGE_OPTION) or \
                   self.emulator.is_ui_element_on_screen(ui.ISO8_AWAKEN) or \
                   self.emulator.is_ui_element_on_screen(ui.ISO8_COMBINE) or \
                   self.emulator.is_ui_element_on_screen(ui.ISO8_UPGRADE)

        self.game.go_to_inventory()
        self.emulator.click_button(ui.INVENTORY_UPGRADE_TAB)
        self.emulator.click_button(ui.INVENTORY_ISO_8_TAB)
        return wait_until(is_iso8_tab, timeout=3, period=1)

    def toggle_quick_upgrade(self):
        """Toggles Quick Upgrade toggle if it's not active.

        :return: is toggle active or not.
        :rtype: bool
        """
        if not self.emulator.is_image_on_screen(ui.ISO8_QUICK_UPGRADE_TOGGLE):
            logger.debug("ISO-8: found Quick Upgrade toggle inactive. Clicking it.")
            self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_TOGGLE)
            wait_until(self.emulator.is_image_on_screen, ui_element=ui.ISO8_QUICK_UPGRADE_TOGGLE)
        return self.emulator.is_ui_element_on_screen(ui.ISO8_QUICK_UPGRADE)

    def lock_iso8(self, iso_to_lock, options_to_lock):
        """Locks ISO-8 from Inventory.
        Starting from bottom right clicks on every ISO-8 and detects whether it's options is good for locking.

        :param str | list[str] iso_to_lock: list of ISO-8 types to upgrade. See `ISO8_TYPE` class.
        :param str | list[str] options_to_lock: list of options to look for locking. See `ISO8_LOCK` class.
        """
        if not iso_to_lock or not options_to_lock:
            logger.warning("Nothing to lock.")
            return self.game.go_to_main_menu()
        if isinstance(iso_to_lock, str):
            iso_to_lock = [iso_to_lock]
        if isinstance(options_to_lock, str):
            options_to_lock = [options_to_lock]

        logger.info(f"ISO-8: locking options {options_to_lock} for each of given types: {iso_to_lock}.")
        if not self.open_iso8_tab():
            logger.error("Can't get to ISO-8 tab in the inventory.")
            return self.game.go_to_main_menu()

        for iso_type in iso_to_lock:
            logger.info(f"Starting to looking at {iso_type} type.")
            self.emulator.click_button(ui.get_by_name(iso_type))
            self._select_and_lock_iso8(options_to_lock=options_to_lock)
        self.game.go_to_main_menu()

    def upgrade_iso8(self, times_for_each_upgrade=0, iso_to_upgrade=None, iso_to_use=None, stars_to_use=None):
        """Upgrades ISO-8 from Inventory.
        Starting from bottom right clicks on every ISO-8 and detects whether it's available for upgrade.
        Uses Quick Upgrade toggle.

        :param int times_for_each_upgrade: how many times upgrade each of ISO-9 type.
        :param str | list[str] iso_to_upgrade: list of ISO-8 types to upgrade. See `ISO8_TYPE` class.
        :param str | list[str] iso_to_use: list of ISO-8 types to use for upgrade. See `ISO8_TYPE_TO_USE` class.
        :param str | list[str] stars_to_use: list of ISO-8 ranks to use for upgrade. See `ISO8_STARS_TO_USE` class.
        :return:
        """
        if not times_for_each_upgrade or not iso_to_upgrade or not iso_to_use or not stars_to_use:
            logger.warning("Nothing to upgrade.")
            return self.game.go_to_main_menu()
        if isinstance(iso_to_upgrade, str):
            iso_to_upgrade = [iso_to_upgrade]

        logger.info(f"ISO-8: upgrading {times_for_each_upgrade} times each of given types: {iso_to_upgrade}.")
        if not self.open_iso8_tab():
            logger.error("Can't get to ISO-8 tab in the inventory.")
            return self.game.go_to_main_menu()

        for iso_type in iso_to_upgrade:
            logger.info(f"Starting to upgrade {iso_type} type.")
            self.emulator.click_button(ui.get_by_name(iso_type))
            self._select_and_upgrade_iso8(times=times_for_each_upgrade, iso_to_use=iso_to_use,
                                          stars_to_use=stars_to_use)
        self.game.go_to_main_menu()

    def combine_iso8(self, times_for_each_combine=0, iso_to_combine=None):
        """Combines ISO-8 from Inventory.
        Starting from bottom right clicks on every ISO-8 and detects whether it's available for combine.

        :param int times_for_each_combine: how many times combine each of ISO-9 type.
        :param str | list[str] iso_to_combine: list of ISO-8 types to combine. See `ISO8_TYPE` class.
        :return:
        """
        if not times_for_each_combine or not iso_to_combine:
            logger.warning("Nothing to combine.")
            return self.game.go_to_main_menu()
        if isinstance(iso_to_combine, str):
            iso_to_combine = [iso_to_combine]

        logger.info(f"ISO-8: combining {times_for_each_combine} times each of given types: {iso_to_combine}.")
        if not self.open_iso8_tab():
            logger.error("Can't get to ISO-8 tab in the inventory.")
            return self.game.go_to_main_menu()

        for iso_type in iso_to_combine:
            logger.info(f"Starting to combining {iso_type} type.")
            self.emulator.click_button(ui.get_by_name(iso_type))
            self._select_and_combine_iso8(times=times_for_each_combine)
        self.game.go_to_main_menu()

    def _try_to_select_iso8_for_upgrade(self) -> bool:
        """Trying to select available ISO-8 for upgrade.
        Starting from bottom right clicks on every ISO-8 and looks for 'QUICK UPGRADE` button.
        Position doesn't matter because that ISO-8 would be already selected and on focus.

        :return: was available ISO-8 for upgrade found or not.
        :rtype: bool
        """
        for row in range(self.INVENTORY_ROW, 0, -1):
            for col in range(self.INVENTORY_COL, 0, -1):
                iso8_ui = ui.get_by_name(f"ISO8_ITEM_{row}_{col}")
                if self.emulator.is_image_on_screen(iso8_ui):  # Empty slot
                    continue
                self.emulator.click_button(iso8_ui)
                if self.emulator.is_ui_element_on_screen(ui.ISO8_QUICK_UPGRADE) or \
                        self.emulator.is_ui_element_on_screen(ui.ISO8_UPGRADE):
                    logger.debug(f"Found ISO-8 available for upgrade in inventory grid at ({row}, {col})")
                    return True
        return False

    def _try_to_select_iso8_for_combine(self, skip_positions=None):
        """Trying to select available ISO-8 for combine.
        Starting from bottom right clicks on every ISO-8 and looks for 'COMBINE` button.
        Can skip positions because each rank of ISO-8 could be combined with only the same rank
        so other available ISO-8 with lower ranks can be found later in the grid.

        :param skip_positions: list of position (row, col) which would be skipped for checking.

        :return: False when no available ISO-8 was found or position (row, col) in inventory's grid of found ISO-8.
        :rtype: bool | tuple[int, int]
        """
        for row in range(self.INVENTORY_ROW, 0, -1):
            for col in range(self.INVENTORY_COL, 0, -1):
                iso8_ui = ui.get_by_name(f"ISO8_ITEM_{row}_{col}")
                if self.emulator.is_image_on_screen(iso8_ui) or (skip_positions and (row, col) in skip_positions):
                    continue
                self.emulator.click_button(iso8_ui)
                if self.emulator.is_ui_element_on_screen(ui.ISO8_COMBINE):
                    logger.debug(f"Found ISO-8 available for combine in inventory grid at ({row}, {col})")
                    return row, col
        return False

    def _select_types_for_upgrade(self, iso_to_use, stars_to_use):
        """Deselects all previous selected types by clicking at 'Select All` toggle and
        then selects types and ranks of ISO-8 for upgrading in Upgrade Menu.

        :param str | list[str] iso_to_use: list of ISO-8 types to use for upgrade. See `ISO8_TYPE_TO_USE` class.
        :param str | list[str] stars_to_use: list of ISO-8 ranks to use for upgrade. See `ISO8_STARS_TO_USE` class.
        """
        if isinstance(iso_to_use, str):
            iso_to_use = [iso_to_use]
        if isinstance(stars_to_use, str):
            stars_to_use = [stars_to_use]
        if wait_until(self.emulator.is_image_on_screen, ui_element=ui.ISO8_QUICK_UPGRADE_SELECT_ALL):
            logger.debug("Clearing selecting types by deselecting them all.")
            self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_SELECT_ALL)
        else:
            logger.debug("Clearing selecting types by selecting and deselecting them all.")
            self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_SELECT_ALL)
            self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_SELECT_ALL)
        for iso_type in iso_to_use:
            self.emulator.click_button(ui.get_by_name(iso_type))
        for star_type in stars_to_use:
            self.emulator.click_button(ui.get_by_name(star_type))

    def _select_and_upgrade_iso8(self, times, iso_to_use, stars_to_use):
        """Selects available for upgrade ISO-8 from inventory's grid and then upgrades it.

        :param int times: how many times to select new ISO-8 for upgrading.
        :param str | list[str] iso_to_use: list of ISO-8 types to use for upgrade. See `ISO8_TYPE_TO_USE` class.
        :param str | list[str] stars_to_use: list of ISO-8 ranks to use for upgrade. See `ISO8_STARS_TO_USE` class.
        """
        for _ in range(times):
            if not self._try_to_select_iso8_for_upgrade():
                return logger.info("No available ISO-8 for upgrades on first page in the inventory grid.")
            if not self.toggle_quick_upgrade():
                return logger.error(f"ISO-8: can't find {ui.ISO8_QUICK_UPGRADE} button, cannot upgrade.")

            self.emulator.click_button(ui.ISO8_QUICK_UPGRADE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_QUICK_UPGRADE_MENU):
                self._select_types_for_upgrade(iso_to_use=iso_to_use, stars_to_use=stars_to_use)
                logger.debug("ISO-8: confirming upgrading.")
                self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_CONFIRM)
                self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_CONFIRM)  # To skip animation
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_QUICK_UPGRADE_RESULTS):
                    self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_RESULTS)
                else:
                    if self.emulator.is_ui_element_on_screen(ui.ISO8_QUICK_UPGRADE_MENU):
                        logger.info("Not enough ISO-8 types/stars to perform upgrade.")
                        self.emulator.click_button(ui.ISO8_QUICK_UPGRADE_MENU)
                        return
                self.close_after_mission_notifications()

    def _select_and_combine_iso8(self, times):
        """Selects available for combine ISO-8 from inventory's grid and then combines it.

        :param int times: how many times to select new ISO-8 for combining.
        """
        counter = 0
        unable_to_combine = []
        while counter < times:
            iso_position = self._try_to_select_iso8_for_combine(skip_positions=unable_to_combine)
            if not iso_position:
                logger.info("No more ISO-8 to combine.")
                return
            self.emulator.click_button(ui.ISO8_COMBINE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_COMBINE_LABEL):
                if not wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_COMBINE_MATERIAL_SELECT_1):
                    logger.info("No more materials to combine.")
                    self.emulator.click_button(ui.ISO8_COMBINE_LABEL)
                    unable_to_combine.append(iso_position)
                    continue
                for material_num in range(1, 6):
                    material_ui = ui.get_by_name(f"ISO8_COMBINE_MATERIAL_SELECT_{material_num}")
                    self.emulator.click_button(material_ui)
                    if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_COMBINE_LOCKED):
                        logger.info(f"Item #{material_num} is locked, cannot combine, trying next one.")
                        self.emulator.click_button(ui.ISO8_COMBINE_LOCKED)
                        continue
                    self.emulator.click_button(ui.ISO8_COMBINE_CONFIRM)
                    if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_COMBINE_CONFIRM_NOTICE):
                        logger.debug("Combining ISO-8.")
                        self.emulator.click_button(ui.ISO8_COMBINE_CONFIRM_NOTICE)
                        if wait_until(self.emulator.is_ui_element_on_screen,
                                      ui_element=ui.ISO8_COMBINE_CONFIRM_NOTICE_CLOSE):
                            self.emulator.click_button(ui.ISO8_COMBINE_CONFIRM_NOTICE_CLOSE)
                            self.close_after_mission_notifications()
                            break
                else:
                    logger.info("All items are locked, cannot combine.")
                    self.emulator.click_button(ui.ISO8_COMBINE_LABEL)
                    unable_to_combine.append(iso_position)
                    continue
            counter += 1

    def _select_and_lock_iso8(self, options_to_lock):
        """Selects each ISO-8 from inventory's grid, checks it's options and then locks it
        if option meets requirements.

        :param str | list[str] options_to_lock: list of options to look for locking. See `ISO8_LOCK` class.
        """
        for row in range(self.INVENTORY_ROW, 0, -1):
            for col in range(self.INVENTORY_COL, 0, -1):
                iso8_ui = ui.get_by_name(f"ISO8_ITEM_{row}_{col}")
                if self.emulator.is_image_on_screen(iso8_ui):
                    continue
                self.emulator.click_button(iso8_ui)
                text = self.emulator.get_screen_text(ui.ISO8_OPTION_TEXT)
                for option in options_to_lock:
                    if option in self.ISO8_LOCK.multi_line():
                        matched = regex.match(option, text) is not None
                    else:
                        # `match is not None` is required because `any()` can't cast `match` to bool
                        matched = any([regex.match(option, line) is not None for line in text.split("\n")])
                    if not matched:
                        continue
                    logger.debug(f"Found ISO-8 at {(row, col)} that meets requirements.")
                    if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_LOCK):
                        self.emulator.click_button(ui.ISO8_LOCK)
                        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ISO8_LOCK_CONFIRM):
                            logger.info(f"ISO-8 at {(row, col)} has locked.")
                            self.emulator.click_button(ui.ISO8_LOCK_CONFIRM)


class Artifact(Notifications):
    """Class for working with Artifacts."""

    class ARTIFACT_STARS:
        STAR_1 = "ARTIFACT_DISMANTLE_STAR_1"
        STAR_2 = "ARTIFACT_DISMANTLE_STAR_2"
        STAR_3 = "ARTIFACT_DISMANTLE_STAR_3"
        STAR_4 = "ARTIFACT_DISMANTLE_STAR_4"
        STAR_5 = "ARTIFACT_DISMANTLE_STAR_5"
        STAR_6 = "ARTIFACT_DISMANTLE_STAR_6"

    def open_artifact_tab(self):
        """Opens Artifact tab in Inventory."""

        def is_artifact_tab() -> bool:
            return self.emulator.is_ui_element_on_screen(ui.ARTIFACT_DISMANTLE)

        self.game.go_to_inventory()
        self.emulator.click_button(ui.INVENTORY_UPGRADE_TAB)
        self.emulator.click_button(ui.INVENTORY_ARTIFACT_TAB)
        return wait_until(is_artifact_tab, timeout=3, period=1)

    def _open_dismantle_menu(self):
        """Opens Dismantle Artifact menu.

        :rtype: bool
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE):
            logger.debug("Opening Dismantle menu.")
            self.emulator.click_button(ui.ARTIFACT_DISMANTLE)
            return wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE_LABEL)

    def _auto_select_for_dismantle(self, artifact_stars):
        """Selects artifacts for dismantling using Auto Select menu.

        :param str | list[str] artifact_stars: artifact's stars to dismantle. See `ARTIFACT_STARS` for reference.

        :rtype: bool
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE_AUTO_SELECT):
            logger.debug("Opening Auto Select menu.")
            self.emulator.click_button(ui.ARTIFACT_DISMANTLE_AUTO_SELECT)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE_AUTO_SELECT_LABEL):
                for artifact_star in artifact_stars:
                    artifact_star_ui = ui.get_by_name(artifact_star)
                    logger.debug(f"Selecting {artifact_star_ui}.")
                    self.emulator.click_button(artifact_star_ui)
                self.emulator.click_button(ui.ARTIFACT_DISMANTLE_AUTO_SELECT_CONFIRM)
                if wait_until(self.emulator.is_ui_element_on_screen,
                              ui_element=ui.ARTIFACT_DISMANTLE_AUTO_SELECT_CANCEL):
                    logger.info("No artifacts to dismantle.")
                    self.emulator.click_button(ui.ARTIFACT_DISMANTLE_AUTO_SELECT_CANCEL)
                    return False
                return True

    def dismantle_artifacts(self, artifact_stars):
        """Dismantles artifacts.

        :param str | list[str] artifact_stars: artifact's stars to dismantle. See `ARTIFACT_STARS` for reference.
        """
        if not artifact_stars:
            logger.warning("Nothing to dismantle.")
            return self.game.go_to_main_menu()
        if not self.open_artifact_tab():
            logger.error("Can't get to Artifact tab in the inventory.")
            return self.game.go_to_main_menu()
        if not self._open_dismantle_menu():
            logger.error("Can't open Dismantle menu.")
            return self.game.go_to_main_menu()
        if not self._auto_select_for_dismantle(artifact_stars=artifact_stars):
            return self.game.go_to_main_menu()

        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE_CONFIRM):
            logger.debug("Dismantling artifacts.")
            self.emulator.click_button(ui.ARTIFACT_DISMANTLE_CONFIRM)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE_CONFIRM_OK):
                self.emulator.click_button(ui.ARTIFACT_DISMANTLE_CONFIRM_OK)
                if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ARTIFACT_DISMANTLE_CONFIRM_CLOSE,
                              timeout=10):
                    logger.info("Artifacts were dismantled.")
                    self.emulator.click_button(ui.ARTIFACT_DISMANTLE_CONFIRM_CLOSE)
        self.game.go_to_main_menu()
