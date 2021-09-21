import lib.logger as logging
from math import ceil
from lib.game.notifications import Notifications
from lib.game import ui
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class EnhancePotential(Notifications):
    """Class for working with character's potential enhancement."""

    COSMIC_CUBE_FRAGMENT = "COSMIC_CUBE_FRAGMENT"
    BLACK_ANTI_MATTER = "BLACK_ANTI_MATTER"
    NORN_STONE_OF_CHAOS = "NORN_STONE_OF_CHAOS"

    @property
    def success_rate(self):
        """Returns Success Rate number of enhancement.

        :rtype: float
        """
        success_rate_text = self.emulator.get_screen_text(ui_element=ui.ENHANCE_POTENTIAL_RATE)
        success_rate = success_rate_text.replace("%", "").replace(" ", "")
        return float(success_rate)

    def apply_material(self, material, click_speed=0.02):
        """Applies material for enhancement.

        :param str material: name of the material.
        :param float click_speed: clicking speed of applying.
        """
        if material == self.COSMIC_CUBE_FRAGMENT:
            self.emulator.click_button(ui.ENHANCE_POTENTIAL_COSMIC_CUBES, min_duration=click_speed,
                                       max_duration=click_speed)
        if material == self.BLACK_ANTI_MATTER:
            self.emulator.click_button(ui.ENHANCE_POTENTIAL_ANTI_MATTER, min_duration=click_speed,
                                       max_duration=click_speed)
        if material == self.NORN_STONE_OF_CHAOS:
            self.emulator.click_button(ui.ENHANCE_POTENTIAL_NORN_STONES, min_duration=click_speed,
                                       max_duration=click_speed)

    def press_upgrade(self):
        """Presses Upgrade button to enhance potential.

        :return: was button pressed successful or not.
        :rtype: bool
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ENHANCE_POTENTIAL_UPGRADE):
            logger.debug(f"Upgrading potential with rate: {self.success_rate}.")
            self.emulator.click_button(ui.ENHANCE_POTENTIAL_UPGRADE)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ENHANCE_POTENTIAL_UPGRADE_OK):
                self.emulator.click_button(ui.ENHANCE_POTENTIAL_UPGRADE_OK)
                return True
        logger.error(f"Can't find {ui.ENHANCE_POTENTIAL_UPGRADE} button to click.")
        return False

    def check_enhance_was_successful(self):
        """Checks enhancement result.

        :return: was enhancement successful or not.
        :rtype: bool
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ENHANCE_POTENTIAL_FAILED):
            logger.debug("Enhance Potential failed.")
            self.emulator.click_button(ui.ENHANCE_POTENTIAL_FAILED, min_duration=1, max_duration=1.5)
            return False
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=ui.ENHANCE_POTENTIAL_SUCCESS):
            logger.debug("Enhance Potential succeeded.")
            self.emulator.click_button(ui.ENHANCE_POTENTIAL_SUCCESS, min_duration=1, max_duration=1.5)
            return True

    def enhance_potential(self, target_success_rate=10.00, material_to_use=(NORN_STONE_OF_CHAOS, BLACK_ANTI_MATTER)):
        """Tries to enhance potential with materials.

        :param float target_success_rate: minimal success rate of enhancement to proceed upgrading.
        :param str | tuple[str] | list[str] material_to_use: name of materials to use in enhancement.
        """
        if not self.emulator.is_ui_element_on_screen(ui_element=ui.ENHANCE_POTENTIAL_LABEL):
            return logger.error("Open character's Enhance Potential menu to enhance the potential.")
        if not isinstance(material_to_use, (list, tuple)):
            material_to_use = [material_to_use]
        wrong_materials = [material for material in material_to_use if material not in (self.COSMIC_CUBE_FRAGMENT,
                                                                                        self.BLACK_ANTI_MATTER,
                                                                                        self.NORN_STONE_OF_CHAOS)]
        if wrong_materials:
            return logger.error(f"Material to use contains wrong materials: {wrong_materials}")
        for material in material_to_use:
            current_rate = self.success_rate
            self.apply_material(material)
            r_sleep(1)  # Wait for success rate animation
            material_cost = self.success_rate - current_rate - 0.005
            if material_cost == 0:
                continue
            steps_count = ceil((target_success_rate - self.success_rate) / material_cost)
            logger.debug(f"{material} material cost = {material_cost}, "
                         f"steps to achieve target {target_success_rate} from {current_rate} is {steps_count} steps.")
            for _ in range(steps_count):
                self.apply_material(material)
            r_sleep(1)  # Wait for success rate animation
            if self.success_rate >= target_success_rate:
                break
        if self.success_rate < target_success_rate:
            return logger.error(f"Current Success Rate: {self.success_rate}, can't get to {target_success_rate}.")
        if self.press_upgrade():
            if not self.check_enhance_was_successful():
                r_sleep(1)
                self.enhance_potential(target_success_rate=target_success_rate, material_to_use=material_to_use)
