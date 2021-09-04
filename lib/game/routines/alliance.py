import lib.logger as logging
from lib.game.notifications import Notifications
from lib.functions import wait_until, r_sleep

logger = logging.get_logger(__name__)


class Alliance(Notifications):
    """Class for working with Alliance."""

    class STORE_ITEM:
        ENERGY = "ALLIANCE_STORE_ENERGY_ITEM_1"
        UNIFORM_EXP_CHIP = "ALLIANCE_STORE_UNIFORM_EXP_CHIP_ITEM_2"
        HIDDEN_TICKET = "ALLIANCE_STORE_HIDDEN_TICKET_ITEM_3"
        BOOST_POINT = "ALLIANCE_STORE_BOOST_POINT_ITEM_4"

    class SUPPORT_ITEM:
        NORN_STONE_OF_STRENGTH = "ALLIANCE_SUPPORT_REQUEST_NORN_STONE_OF_STRENGTH"
        NORN_STONE_OF_ENERGY = "ALLIANCE_SUPPORT_REQUEST_NORN_STONE_OF_ENERGY"
        NORN_STONE_OF_BRILLIANCE = "ALLIANCE_SUPPORT_REQUEST_NORN_STONE_OF_BRILLIANCE"
        NORN_STONE_OF_OMNIPOTENCE = "ALLIANCE_SUPPORT_REQUEST_NORN_STONE_OF_OMNIPOTENCE"
        BLACK_ANTI_MATTER = "ALLIANCE_SUPPORT_REQUEST_BLACK_ANTI_MATTER"
        NORN_STONE_OF_CHAOS = "ALLIANCE_SUPPORT_REQUEST_NORN_STONE_OF_CHAOS"
        MKRAAN_SHARD = "ALLIANCE_SUPPORT_REQUEST_MKRAAN_SHARD"
        PHOENIX_FEATHER = "ALLIANCE_SUPPORT_REQUEST_PHOENIX_FEATHER"
        MKRAAN_CRYSTAL = "ALLIANCE_SUPPORT_REQUEST_MKRAAN_CRYSTAL"
        GEAR_UP_KIT = "ALLIANCE_SUPPORT_REQUEST_GEAR_UP_KIT"
        DIMENSION_DEBRIS = "ALLIANCE_SUPPORT_REQUEST_DIMENSION_DEBRIS"

        ON_SECOND_LIST = [MKRAAN_SHARD, PHOENIX_FEATHER, MKRAAN_CRYSTAL, GEAR_UP_KIT, DIMENSION_DEBRIS]

    def check_in(self):
        """Click Check-In button in Alliance."""
        self.game.go_to_alliance()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_CHECK_IN']):
            self.emulator.click_button(self.ui['ALLIANCE_CHECK_IN'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_CHECK_IN_CLOSE']):
                self.emulator.click_button(self.ui['ALLIANCE_CHECK_IN_CLOSE'].button)
        self.game.go_to_main_menu()

    def donate_resources(self, donate_gold=True, donate_memento=True):
        """Donate resources to Alliance

        :param donate_gold: True or False.
        :param donate_memento: True or False.
        """
        if not donate_gold and not donate_memento:
            logger.info("Nothing to donate.")
            return self.game.go_to_main_menu()
        self.game.go_to_alliance()
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_DONATE']):
            self.emulator.click_button(self.ui['ALLIANCE_DONATE'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_DONATION_MENU']):
                if donate_gold:
                    logger.debug("Maxing GOLD for donation.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_MAX_GOLD'].button)
                if donate_memento:
                    logger.debug("Maxing ALLIANCE MEMENTO for donation.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_MAX_MEMENTO'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['ALLIANCE_DONATION_CONFIRM']):
                    logger.info("Donating resources for Alliance.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_CONFIRM'].button)
                    if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                                  ui_element=self.ui['ALLIANCE_DONATION_REWARD_CLOSE']):
                        logger.info("Resources were donated, exiting.")
                        self.emulator.click_button(self.ui['ALLIANCE_DONATION_REWARD_CLOSE'].button)
                else:
                    logger.info("Can't donate resource for Alliance. Probably already donated, exiting.")
                    self.emulator.click_button(self.ui['ALLIANCE_DONATION_CANCEL'].button)
        self.game.go_to_main_menu()

    def buy_items_from_store(self, items=None, buy_all_available=True):
        """Buy items from Alliance Store.

        :param items: list of UI Elements of items to buy.
        :param buy_all_available: (bool) buy all available copies of item for today or not.
        """
        self.game.go_to_alliance()
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_STORE_TAB']):
            logger.error("Can't find STORE tab, exiting.")
            return self.game.go_to_main_menu()
        self.emulator.click_button(self.ui['ALLIANCE_STORE_TAB'].button)
        self.game.close_ads()
        if isinstance(items, str):
            items = [items]
        for item in items:
            logger.debug(f"Trying to buy {item}.")
            bought = self._buy_item_once(item)
            if buy_all_available and bought:
                while bought:
                    logger.debug(f"Trying to buy {item} again.")
                    bought = self._buy_item_once(item)
        self.game.go_to_main_menu()

    def _buy_item_once(self, item):
        """Buy item from Alliance Store once.

        :return: (bool) was item bought or not.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui[item]):
            self.emulator.click_button(self.ui[item].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_STORE_PURCHASE']):
                logger.debug("Purchasing via Alliance Tokens.")
                self.emulator.click_button(self.ui['ALLIANCE_STORE_PURCHASE'].button)
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['ALLIANCE_STORE_PURCHASE_CLOSE']):
                    logger.info("Item was bought.")
                    self.emulator.click_button(self.ui['ALLIANCE_STORE_PURCHASE_CLOSE'].button)
                    return True
                # TODO: no tokens scenario
                # if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                #               ui_element=self.ui['STORE_RECHARGE_ENERGY_VIA_NO_POINTS']):
                #     logger.info("Not enough Assemble Points for energy recharge.")
                #     self.emulator.click_button(self.ui['STORE_RECHARGE_ENERGY_VIA_NO_POINTS'].button)
                #     return False
                if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                              ui_element=self.ui['ALLIANCE_STORE_PURCHASE_LIMIT']):
                    logger.info("Reached daily limit for purchasing.")
                    self.emulator.click_button(self.ui['ALLIANCE_STORE_PURCHASE_LIMIT'].button)
                    return False
        logger.warning(f"Item {item} was not found in the Alliance Store.")
        return False

    def request_support_item(self, support_item):
        """Request Support item and collect previous request.

        :param support_item: item to request.
        """
        self.game.go_to_alliance()
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_SUPPORT_TAB']):
            logger.error("Can't find SUPPORT tab, exiting.")
            return self.game.go_to_main_menu()
        self.emulator.click_button(self.ui['ALLIANCE_SUPPORT_TAB'].button)
        self.claim_support_item()
        if not wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_SUPPORT_REQUEST']):
            logger.info("Can not request support item for now, exiting.")
            return self.game.go_to_main_menu()
        self.emulator.click_button(self.ui['ALLIANCE_SUPPORT_REQUEST'].button)
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                      ui_element=self.ui['ALLIANCE_SUPPORT_REQUEST_MENU']):
            if support_item in self.SUPPORT_ITEM.ON_SECOND_LIST:
                self._drag_support_item_list()
            logger.debug(f"Sending support request for item {support_item}.")
            self.emulator.click_button(self.ui[support_item].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_SUPPORT_REQUEST_CONFIRM']):
                self.emulator.click_button(self.ui['ALLIANCE_SUPPORT_REQUEST_CONFIRM'].button)
                r_sleep(1)  # Wait for animations
        self.game.go_to_main_menu()

    def claim_support_item(self):
        """Try to claim available item from support request.

        :return: (bool) was item claimed or not.
        """
        if wait_until(self.emulator.is_ui_element_on_screen, timeout=3, ui_element=self.ui['ALLIANCE_SUPPORT_CLAIM']):
            logger.info("Claiming previous support request.")
            self.emulator.click_button(self.ui['ALLIANCE_SUPPORT_CLAIM'].button)
            if wait_until(self.emulator.is_ui_element_on_screen, timeout=3,
                          ui_element=self.ui['ALLIANCE_SUPPORT_CLAIM_CLOSE']):
                self.emulator.click_button(self.ui['ALLIANCE_SUPPORT_CLAIM_CLOSE'].button)
                return True
        return False

    def _drag_support_item_list(self):
        """Drags Support Items list from top to bottom."""
        logger.debug("Dragging list to the bottom.")
        self.emulator.drag(self.ui['ALLIANCE_SUPPORT_REQUEST_MENU_DRAG_BOTTOM'].button,
                           self.ui['ALLIANCE_SUPPORT_REQUEST_MENU_DRAG_TOP'].button)
        r_sleep(1)
