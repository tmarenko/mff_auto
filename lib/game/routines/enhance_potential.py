import lib.logger as logging
from math import ceil
from lib.game.notifications import Notifications
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class EnhancePotential(Notifications):
    """Class for working with character's potential enhancement."""

    COSMIC_CUBE_FRAGMENT = "COSMIC_CUBE_FRAGMENT"
    BLACK_ANTI_MATTER = "BLACK_ANTI_MATTER"
    NORN_STONE_OF_CHAOS = "NORN_STONE_OF_CHAOS"

    @property
    def success_rate(self):
        """Returns Success Rate number of enhancement."""
        success_rate_text = self.emulator.get_screen_text(ui_element=self.ui['ENHANCE_POTENTIAL_RATE'])
        success_rate = success_rate_text.replace("%", "").replace(" ", "")
        return float(success_rate)

    def apply_material(self, material, click_speed=0.02):
        """Apply material to enhancement.

        :param material: name of the material.
        :param click_speed: clicking speed of applying.
        """
        if material == self.COSMIC_CUBE_FRAGMENT:
            self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_COSMIC_CUBES'].button, min_duration=click_speed,
                                       max_duration=click_speed)
        if material == self.BLACK_ANTI_MATTER:
            self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_ANTI_MATTER'].button, min_duration=click_speed,
                                       max_duration=click_speed)
        if material == self.NORN_STONE_OF_CHAOS:
            self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_NORN_STONES'].button, min_duration=click_speed,
                                       max_duration=click_speed)

    def press_upgrade(self):
        """Press Upgrade button to enhance potential.

        :return: was button pressed successful or not.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_UPGRADE'],
                      timeout=3):
            logger.debug(f"Upgrading potential with rate: {self.success_rate}.")
            self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_UPGRADE'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_UPGRADE_OK'],
                          timeout=3):
                self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_UPGRADE_OK'].button)
                return True
        logger.error("Can't find Upgrade button to click.")
        return False

    def check_enhance_was_successful(self):
        """Check enhancement result.

        :return: was enhancement successful or not.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_FAILED'],
                      timeout=3):
            logger.debug("Enhance Potential failed.")
            self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_FAILED'].button, min_duration=1, max_duration=1.5)
            return False
        if wait_until(self.emulator.is_ui_element_on_screen, ui_element=self.ui['ENHANCE_POTENTIAL_SUCCESS'],
                      timeout=3):
            logger.debug("Enhance Potential succeeded.")
            self.emulator.click_button(self.ui['ENHANCE_POTENTIAL_SUCCESS'].button, min_duration=1, max_duration=1.5)
            return True

    def enhance_potential(self, target_success_rate=10.00, material_to_use=(NORN_STONE_OF_CHAOS, BLACK_ANTI_MATTER)):
        """Try to enhance potential with materials.

        :param target_success_rate: minimal success rate of enhancement to proceed upgrading.
        :param material_to_use: name of materials to use in enhancement.
        """
        if not self.emulator.is_ui_element_on_screen(ui_element=self.ui['ENHANCE_POTENTIAL_LABEL']):
            logger.error("Open character's Enhance Potential menu to enhance the potential.")
            return
        if not isinstance(material_to_use, (list, tuple)):
            material_to_use = [material_to_use]
        wrong_materials = [material for material in material_to_use if material not in (self.COSMIC_CUBE_FRAGMENT,
                                                                                        self.BLACK_ANTI_MATTER,
                                                                                        self.NORN_STONE_OF_CHAOS)]
        if wrong_materials:
            logger.error(f"Material to use contains wrong materials: {wrong_materials}")
            return
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
        if self.success_rate >= target_success_rate:
            if self.press_upgrade():
                if not self.check_enhance_was_successful():
                    r_sleep(1)
                    self.enhance_potential(target_success_rate=target_success_rate, material_to_use=material_to_use)
        else:
            logger.error(f"Current Success Rate: {self.success_rate}, cannot get to target {target_success_rate}.")
            return
