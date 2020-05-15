from lib.player import NoxWindow
from lib.legendary_battle import LegendaryBattle
from lib.dimension_missions import DimensionMissions
from lib.epic_quests import StupidXMen, DarkDimension, MutualEnemy, BeginningOfTheChaos, DoomsDay, NewFaces, \
    TwistedWorld, TheBigTwin, VeiledSecret, MemoryMission
from lib.coop import CoopPlay
from lib.timeline import TimelineBattle
from lib.invasion import WorldBossInvasion
from lib.routines import DailyMissions, DailyTrivia, ShieldLab
from lib.squad_battles import SquadBattles
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
    nf = NewFaces(game).do_missions()
    tw = TwistedWorld(game).do_missions()
    # Available: DarkDimension.SATANA, DarkDimension.HELLSTORM
    ss = DarkDimension(game).do_missions(DarkDimension.SATANA)

    sx = StupidXMen(game).do_missions()
    bt = TheBigTwin(game).do_missions()
    vs = VeiledSecret(game).do_missions()
    cp = CoopPlay(game).do_missions()
    tb = TimelineBattle(game).do_missions()
    lb = LegendaryBattle(game).do_missions()
    # Available: SquadBattles.MODE.DAILY_RANDOM and SquadBattles.MODE.ALL_BATTLES
    sb = SquadBattles(game).do_missions(mode=SquadBattles.MODE.DAILY_RANDOM)

    # Available: MemoryMission.MORDO, MemoryMission.WONG, MemoryMission.ANCIENT_ONE, MemoryMission.KAECILIUS,
    # MemoryMission.DIFFICULTY
    # Use MemoryMission.DIFFICULTY.STAGE_1 up to MemoryMission.DIFFICULTY.STAGE_6 for difficulty
    mm = MemoryMission(game).do_missions(MemoryMission.ANCIENT_ONE, MemoryMission.DIFFICULTY.STAGE_6)

    dm = DimensionMissions(game).do_missions(times=20, difficulty=10)
