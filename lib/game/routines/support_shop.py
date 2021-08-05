import lib.logger as logging
from lib.game.notifications import Notifications
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class SupportShop(Notifications):
    """Class for working with energy in store."""

    class MATERIALS:

        NORN_STONE_OF_STRENGTH = "SUPPORT_SHOP_MATERIAL_NORN_STONE_OF_STRENGTH"
        NORN_STONE_OF_ENERGY = "SUPPORT_SHOP_MATERIAL_NORN_STONE_OF_ENERGY"
        NORN_STONE_OF_BRILLIANCE = "SUPPORT_SHOP_MATERIAL_NORN_STONE_OF_BRILLIANCE"
        NORN_STONE_OF_OMNIPOTENCE = "SUPPORT_SHOP_MATERIAL_NORN_STONE_OF_OMNIPOTENCE"
        MKRAAN_SHARD = "SUPPORT_SHOP_MATERIAL_MKRAAN_SHARD"
        GEAR_UP_KIT = "SUPPORT_SHOP_MATERIAL_GEAR_UP_KIT"
        DIMENSION_DEBRIS = "SUPPORT_SHOP_MATERIAL_DIMENSION_DEBRIS"
        UNIFORM_UPGRADE_KIT = "SUPPORT_SHOP_MATERIAL_UNIFORM_UPGRADE_KIT"

    def open_support_shop(self):
        """Open Support Shop from Main Menu tab."""
        self.game.go_to_main_menu()
        self.emulator.click_button(self.ui['MAIN_MENU'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['MAIN_MENU']):
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['MAIN_MENU_SUPPORT_SHOP']):
                self.emulator.click_button(self.ui['MAIN_MENU_SUPPORT_SHOP'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['SUPPORT_SHOP_LABEL']):
                    r_sleep(1)  # Wait for animation
                    return True

    def _open_material_tab(self):
        """Open Material tab in Support Shop."""
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['SUPPORT_SHOP_MATERIAL_TAB']):
            self.emulator.click_button(self.ui['SUPPORT_SHOP_MATERIAL_TAB'].button)
            return True
        return False

    def _buy_material(self, material_ui, max_items=True):
        """Buy material from Support Shop.

        :param material_ui: name of UI Element of material to buy.
        :param max_items: buy all items or not.
        """
        logger.debug(f"Buying material with UI: {material_ui}")
        self.emulator.click_button(self.ui[material_ui].button)
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['SUPPORT_SHOP_BUY_MATERIAL_EXCHANGE_BUTTON']):
            logger.warning("Cannot get into Exchange menu, probably material has been already bought.")
            return

        if max_items and self.emulator.is_ui_element_on_screen(self.ui['SUPPORT_SHOP_BUY_MATERIAL_MAX_BUTTON']):
            logger.debug("Clicking MAX button.")
            self.emulator.click_button(self.ui['SUPPORT_SHOP_BUY_MATERIAL_MAX_BUTTON'].button)

        self.emulator.click_button(self.ui['SUPPORT_SHOP_BUY_MATERIAL_EXCHANGE_BUTTON'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['SUPPORT_SHOP_BUY_MATERIAL_CLOSE_PURCHASE']):
            logger.info("Material acquired.")
            r_sleep(1)  # Wait for animation
            self.emulator.click_button(self.ui['SUPPORT_SHOP_BUY_MATERIAL_CLOSE_PURCHASE'].button)

    def buy_materials(self, materials_list):
        """Buy materials from Support Shop.

        :param materials_list: list of UI Element of materials to buy.
        """
        if isinstance(materials_list, str):
            materials_list = [materials_list]

        self.open_support_shop()
        self._open_material_tab()
        for material in materials_list:
            self._buy_material(material_ui=material)
        self.game.go_to_main_menu()
