import sys
import inspect
from lib.gui.widgets.queue_items import actions
from lib.gui.widgets.queue_items import events
from lib.gui.widgets.queue_items import missions
from .general import GameMode, Action, Event
import lib.logger as logging

logger = logging.get_logger(__name__)


def _classes_from_module(module_name):
    """Generator for all non-imported classes inside module.

    :param module_name: module's name.
    """
    if module_name not in sys.modules:
        logger.error(f"Cannot load {module_name} module.")
    for name, obj in inspect.getmembers(sys.modules[module_name]):
        if obj and inspect.isclass(obj) and obj.__module__ == module_name:
            yield obj


def _init_classes(module_name, game):
    """Initialize all non-imported classes inside module into the game.

    :param module_name: module's name.
    :param game: instance of the game.
    """
    return [class_init(game) for class_init in _classes_from_module(module_name)]


def get_actions(game):
    """Get all initialized actions."""
    return _init_classes(module_name=actions.__name__, game=game)


def get_events(game):
    """Get all initialized events."""
    return _init_classes(module_name=events.__name__, game=game)


def get_missions(game):
    """Get all initialized missions."""
    return _init_classes(module_name=missions.__name__, game=game)


def get_missions_dict(mission_instances):
    """Construct menu dictionary for missions by it's instances.

    :param mission_instances: list of mission's instances.
    """
    def find_instance(class_):
        return next((inst for inst in mission_instances if inst.__class__.__name__ == class_.__name__), None)

    menu_dict = {
        "EPIC QUESTS": {
            "DARK REIGN": [find_instance(missions._PlayingHero), find_instance(missions._GoldenGods),
                           find_instance(missions._StingOfTheScorpion), find_instance(missions._SelfDefenseProtocol),
                           find_instance(missions._LegacyOfBlood)],
            "GALACTIC IMPERATIVE": [find_instance(missions._FateOfTheUniverse), find_instance(missions._TheFault),
                                    find_instance(missions._DangerousSisters), find_instance(missions._CosmicRider),
                                    find_instance(missions._QuantumPower), find_instance(missions._WingsOfDarkness)],
            "FIRST FAMILY": [find_instance(missions._DoomsDay), find_instance(missions._TwistedWorld),
                             find_instance(missions._InhumanPrincess), find_instance(missions._MeanAndGreen),
                             find_instance(missions._ClobberinTime), find_instance(missions._Hothead)],
            "X-FORCE": [find_instance(missions._BeginningOfTheChaos), find_instance(missions._StupidXMen),
                        find_instance(missions._TheBigTwin), find_instance(missions._AwManThisGuy),
                        find_instance(missions._DominoFalls)],
            "RISE OF THE X-MEN": [find_instance(missions._MutualEnemy), find_instance(missions._VeiledSecret),
                                  find_instance(missions._GoingRogue), find_instance(missions._FriendsAndEnemies),
                                  find_instance(missions._WeatheringTheStorm), find_instance(missions._Blindsided)],
            "SORCERER SUPREME": [find_instance(missions._DarkAdvent), find_instance(missions._IncreasingDarkness),
                                 find_instance(missions._RoadToMonastery), find_instance(missions._MysteriousAmbush),
                                 find_instance(missions._MonasteryInTrouble), find_instance(missions._PowerOfTheDark)]
        },
        "DIMENSION MISSION": find_instance(missions._DimensionMissions),
        "LEGENDARY BATTLE": find_instance(missions._LegendaryBattle),
        "SQUAD BATTLE": find_instance(missions._SquadBattles),
        "WORLD BOSS": find_instance(missions._WorldBosses),
        "TIMELINE BATTLE": find_instance(missions._TimelineBattle),
        "DANGER ROOM": find_instance(missions._DangerRoom),
        "ALLIANCE BATTLE": find_instance(missions._AllianceBattle),
        "CO-OP PLAY": find_instance(missions._CoopPlay),
        "WORLD BOSS INVASION": find_instance(missions._WorldBossInvasion),
        "GIANT BOSS RAID": find_instance(missions._GiantBossRaid),
    }
    return menu_dict


def get_actions_dict(action_instances):
    """Construct menu dictionary for actions by it's instances.

    :param action_instances: list of action's instances.
    """
    def find_instance(class_):
        return next((inst for inst in action_instances if inst.__class__.__name__ == class_.__name__), None)

    alliance = [find_instance(actions._AllianceCheckIn), find_instance(actions._AllianceDonate),
                find_instance(actions._AllianceBuyEnergy), find_instance(actions._AllianceRequestSupport),
                find_instance(actions._AllianceChallengesEnergy)]
    inventory = [find_instance(actions._ComicCards), find_instance(actions._CustomGear),
                 find_instance(actions._Iso8Upgrade), find_instance(actions._Iso8Combine),
                 find_instance(actions._Iso8Lock)]
    store = [find_instance(actions._CollectFreeEnergy), find_instance(actions._CollectEnergyViaAssemblePoints),
             find_instance(actions._AcquireFreeHeroChest)]
    menu_dict = {
        "[ACTIONS]": {
            "ALLIANCE": alliance,
            "INVENTORY": inventory,
            "STORE": store,
            **{action.mode_name: action for action in action_instances if action not in [*alliance, *inventory, *store]}
        }
    }
    return menu_dict
