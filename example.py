from lib.player import NoxWindow
from lib.alliance_battles import AllianceBattles
from lib.legendary_battle import LegendaryBattle
from lib.dimension_missions import DimensionMissions
from lib.epic_quests import StupidXMen, MutualEnemy, BeginningOfTheChaos, DoomsDay, \
    TwistedWorld, TheBigTwin, VeiledSecret, TheFault
from lib.coop import CoopPlay
from lib.timeline import TimelineBattle
from lib.invasion import WorldBossInvasion
from lib.routines import DailyTrivia, ShieldLab
from lib.squad_battles import SquadBattles
from lib.world_bosses import WorldBosses
from lib.game import Game
import time
from lib.functions import sleep

time.sleep = sleep

if __name__ == '__main__':

    nox = NoxWindow("NoxPlayer")    # Use your window's name of emulator to get a handle

    game = Game(nox)
    game.set_mission_team(5)        # Setup your team for common missions to get EXP
    game.set_timeline_team(2)       # Setup your team for PVP missions
    wbi = WorldBossInvasion(game).do_missions()
    dt = DailyTrivia(game).do_trivia()
    dd = DoomsDay(game).do_missions()
    botc = BeginningOfTheChaos(game).do_missions()
    xm = MutualEnemy(game).do_missions()
    tw = TwistedWorld(game).do_missions()
    sx = StupidXMen(game).do_missions()
    bt = TheBigTwin(game).do_missions()
    vs = VeiledSecret(game).do_missions()
    tf = TheFault(game).do_missions()
    cp = CoopPlay(game).do_missions()
    tb = TimelineBattle(game).do_missions()
    lb = LegendaryBattle(game).do_missions()
    # Available: SquadBattles.MODE.DAILY_RANDOM and SquadBattles.MODE.ALL_BATTLES
    sb = SquadBattles(game).do_missions(mode=SquadBattles.MODE.DAILY_RANDOM)

    # Available: AllianceBattles.MODE.NORMAL or AllianceBattles.MODE.ALL_BATTLES
    ab = AllianceBattles(game).do_missions(AllianceBattles.MODE.ALL_BATTLES)

    # Available: WorldBosses.MODE.BEGINNER or WorldBosses.MODE.NORMAL or WorldBosses.MODE.ULTIMATE
    wb = WorldBosses(game).do_missions(mode=WorldBosses.MODE.ULTIMATE, difficulty=1)

    dm = DimensionMissions(game).do_missions(times=20, difficulty=10)
