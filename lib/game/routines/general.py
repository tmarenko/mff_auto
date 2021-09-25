import json
import urllib.request as request
from datetime import datetime, timedelta
from time import sleep

import lib.logger as logging
from lib.game.notifications import Notifications

logger = logging.get_logger(__name__)


class WaitUntil(Notifications):
    """Class for working with waiting different events."""
    GAME_RESET_HOUR_UTC = 15

    def wait_until_boost_points(self, value=100):
        """Waits until boost points value is equal or greater then given amount.

        :param int value: value for boost pints.
        """
        logger.debug(f"Current Boost points: {self.game.boost}, waiting until: {value}")
        while int(self.game.boost) < value:
            sleep(90)
        logger.debug(f"Current Boost points: {self.game.boost}, done.")

    def wait_until_max_energy(self):
        """Waits until energy is max out."""
        logger.debug(f"Current energy: {self.game.energy}, waiting until: {self.game.energy_max}")
        while int(self.game.energy) < int(self.game.energy_max):
            sleep(120)
        logger.debug(f"Current energy: {self.game.energy}, done.")

    def wait_until_daily_reset(self, hour_offset=0):
        """Waits until game's daily reset.

        :param hour_offset: offset in hours that will be subtract from the Daily Reset time.
        """
        if not isinstance(hour_offset, int):
            hour_offset = 0
        try:
            with request.urlopen("http://worldtimeapi.org/api/timezone/Etc/UTC") as url_data:
                content = url_data.read()
                time_data = json.loads(content)
        except BaseException as err:
            logger.error(f"Caught error: {err}\n"
                         f"Trying to get time again in next 10 seconds.")
            sleep(10)
            return self.wait_until_daily_reset()
        current_time = datetime.strptime(time_data['datetime'][:-6], '%Y-%m-%dT%H:%M:%S.%f')
        logger.debug(f"Current time is {current_time} (UTC timezone), "
                     f"waiting until {self.GAME_RESET_HOUR_UTC - hour_offset}:00.")
        while current_time.hour < self.GAME_RESET_HOUR_UTC - hour_offset:
            sleep(60)
            current_time += timedelta(seconds=60)
        logger.debug(f"Current time is {current_time}, done.")
