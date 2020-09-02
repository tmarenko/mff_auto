import lib.logger as logging
from lib.players.nox_player import NoxWindow
from lib.game.missions.legendary_battle import LegendaryBattle
from lib.game.missions.alliance_battles import AllianceBattles
from lib.game.missions.dimension_missions import DimensionMissions
from lib.game.missions.epic_quests import StupidXMen, MutualEnemy, BeginningOfTheChaos, DoomsDay, \
    TwistedWorld, TheBigTwin, VeiledSecret, TheFault, FateOfTheUniverse
from lib.game.missions.coop import CoopPlay
from lib.game.missions.danger_room import DangerRoom
from lib.game.missions.timeline import TimelineBattle
from lib.game.missions.invasion import WorldBossInvasion
from lib.game.missions.squad_battles import SquadBattles
from lib.game.missions.world_bosses import WorldBosses
from lib.game.routines import DailyTrivia
from lib.game.game import Game

logger = logging.get_logger(__name__)


if __name__ == '__main__':

    nox = NoxWindow("NoxPlayer")              # Use your window's name of emulator to get a handle

    game = Game(nox)
    game.set_mission_team(1)                  # Setup your team for common missions to get EXP
    game.set_timeline_team(2)                 # Setup your team for PVP missions
    game.ACQUIRE_HEROIC_QUEST_REWARDS = True  # Setup ability to collect Heroic Quest rewards

    wbi = WorldBossInvasion(game).do_missions()
    dt = DailyTrivia(game).do_trivia()
    dd = DoomsDay(game).do_missions()
    botc = BeginningOfTheChaos(game).do_missions()
    xm = MutualEnemy(game).do_missions()
    fotu = FateOfTheUniverse(game).do_missions()
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

    # Available: DangerRoom.MODE.NORMAL or DangerRoom.MODE.EXTREME
    DangerRoom(game).do_missions(times=1, mode=DangerRoom.MODE.NORMAL)
