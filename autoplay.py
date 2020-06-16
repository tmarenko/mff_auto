from lib.players.nox_player import NoxWindow
from lib.game.battle_bot import ManualBattleBot
from lib.game.game import Game
import lib.logger as logging
logger = logging.get_logger(__name__)


if __name__ == '__main__':

    nox = NoxWindow("NoxPlayer")
    game = Game(nox, fake_modes=True)
    m = ManualBattleBot(game, battle_over_conditions=None).fight()
