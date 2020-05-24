from lib.player import NoxWindow
from lib.battle_bot import ManualBattleBot
from lib.game import Game
import time
from lib.functions import sleep as random_sleep
time.sleep = random_sleep


if __name__ == '__main__':

    nox = NoxWindow("NoxPlayer")
    game = Game(nox, fake_modes=True)
    m = ManualBattleBot(game, battle_over_conditions=None).fight()
