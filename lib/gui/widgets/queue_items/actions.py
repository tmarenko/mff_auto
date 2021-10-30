import lib.game.missions as missions
import lib.game.routines as routines
from lib.game.dispatch_mission import DispatchMission
from lib.gui.widgets.queue_items.general import Action


class _RunQueue(Action):

    def __init__(self, game):
        super().__init__(game, "RUN QUEUE", lambda queue_index: None)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="queue_index",
                                                     text="Index of queue to run",
                                                     initial_value=1, min=1, max=4))


class _RestartGame(Action):

    def __init__(self, game):
        super().__init__(game, "RESTART GAME", game.restart_game)


class _DailyTrivia(Action):

    def __init__(self, game):
        self.daily_trivia = routines.DailyTrivia(game)
        super().__init__(game, "DAILY TRIVIA", self.daily_trivia.do_trivia)


class _DailyRewards(Action):

    def __init__(self, game):
        self.daily_rewards = routines.DailyRewards(game)
        super().__init__(game, "DAILY REWARDS: ACQUIRE ALL", self.daily_rewards.acquire_all_daily_rewards)


class _WeeklyRewards(Action):

    def __init__(self, game):
        self.daily_rewards = routines.DailyRewards(game)
        super().__init__(game, "WEEKLY REWARDS: ACQUIRE ALL", self.daily_rewards.acquire_all_weekly_rewards)


class _ComicCards(Action):

    def __init__(self, game):
        self.comic_cards = routines.ComicCards(game)
        super().__init__(game, "COMIC CARDS: UPGRADE ALL", self.comic_cards.upgrade_all_cards)


class _CustomGear(Action):

    def __init__(self, game):
        self.custom_gear = routines.CustomGear(game)
        super().__init__(game, "CUSTOM GEAR: UPGRADE", self.custom_gear.quick_upgrade_gear)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="times",
                                                     text="Select how many time to upgrade"))


class _WaitBoostPoints(Action):

    def __init__(self, game):
        self.wait_until = routines.WaitUntil(game)
        super().__init__(game, "WAIT FOR BOOST POINTS", self.wait_until.wait_until_boost_points)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="value",
                                                     text="Wait until boost points value is equal or greater than",
                                                     initial_value=100,
                                                     max=9999))


class _FriendsSendAll(Action):

    def __init__(self, game):
        self.friends = routines.Friends(game)
        super().__init__(game, "FRIENDS: SEND ALL TOKENS", self.friends.send_all)


class _FriendsAcquireAll(Action):

    def __init__(self, game):
        self.friends = routines.Friends(game)
        super().__init__(game, "FRIENDS: ACQUIRE ALL TOKENS", self.friends.acquire_all)


class _AllianceCheckIn(Action):

    def __init__(self, game):
        self.alliance = routines.Alliance(game)
        super().__init__(game, "ALLIANCE: CHECK-IN", self.alliance.check_in)


class _AllianceDonate(Action):

    def __init__(self, game):
        self.alliance = routines.Alliance(game)
        super().__init__(game, "ALLIANCE: DONATE", self.alliance.donate_resources)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="donate_gold",
                                                     text="Donate Gold"))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="donate_memento",
                                                     text="Donate Alliance Memento"))


class _AllianceBuyEnergy(Action):
    items = {
        "Energy": routines.Alliance.STORE_ITEM.ENERGY,
        "Boost Point": routines.Alliance.STORE_ITEM.BOOST_POINT,
        "Hidden Ticket": routines.Alliance.STORE_ITEM.HIDDEN_TICKET,
        "Uniform EXP Chip": routines.Alliance.STORE_ITEM.UNIFORM_EXP_CHIP,
    }

    def __init__(self, game):
        self.alliance = routines.Alliance(game)
        super().__init__(game, "ALLIANCE: BUY ITEMS FROM STORE", self.alliance.buy_items_from_store)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="items",
                                                     values_dict=self.items))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="buy_all_available",
                                                     text="Buy all available copies of item for today"))


class _AllianceRequestSupport(Action):
    support_items = {
        "Norn Stone of Strength": routines.Alliance.SUPPORT_ITEM.NORN_STONE_OF_STRENGTH,
        "Norn Stone of Energy": routines.Alliance.SUPPORT_ITEM.NORN_STONE_OF_ENERGY,
        "Norn Stone of Brilliance": routines.Alliance.SUPPORT_ITEM.NORN_STONE_OF_BRILLIANCE,
        "Norn Stone of Omnipotence": routines.Alliance.SUPPORT_ITEM.NORN_STONE_OF_OMNIPOTENCE,
        "Black Anti-Matter": routines.Alliance.SUPPORT_ITEM.BLACK_ANTI_MATTER,
        "Norn Stone of Chaos": routines.Alliance.SUPPORT_ITEM.NORN_STONE_OF_CHAOS,
        "M'kraan Shard": routines.Alliance.SUPPORT_ITEM.MKRAAN_SHARD,
        "Phoenix Feather": routines.Alliance.SUPPORT_ITEM.PHOENIX_FEATHER,
        "M'kraan Crystal": routines.Alliance.SUPPORT_ITEM.MKRAAN_CRYSTAL,
        "Gear Up Kit": routines.Alliance.SUPPORT_ITEM.GEAR_UP_KIT,
        "Dimension Debris": routines.Alliance.SUPPORT_ITEM.DIMENSION_DEBRIS,
    }

    def __init__(self, game):
        self.alliance = routines.Alliance(game)
        super().__init__(game, "ALLIANCE: REQUEST SUPPORT", self.alliance.request_support_item)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Combobox,
                                                     setting_key="support_item",
                                                     text="Select item to request",
                                                     values_dict=self.support_items))


class _AllianceChallengesEnergy(Action):

    def __init__(self, game):
        self.alliance = routines.Alliance(game)
        super().__init__(game, "ALLIANCE: COLLECT ENERGY FROM CHALLENGES", self.alliance.collect_energy_from_challenges)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="collect_daily",
                                                     text="Collect daily Challenges energy"))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="collect_weekly",
                                                     text="Collect weekly Challenges energy"))


class _CollectFreeEnergy(Action):

    def __init__(self, game):
        self.store = routines.EnergyStore(game)
        super().__init__(game, "ENERGY: COLLECT FREE 24H", self.store.collect_free_energy)


class _CollectEnergyViaAssemblePoints(Action):

    def __init__(self, game):
        self.store = routines.EnergyStore(game)
        super().__init__(game, "ENERGY: COLLECT VIA ASSEMBLE POINTS", self.store.collect_energy_via_assemble_points)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="use_all_points",
                                                     text="Use all available Assemble Points"))


class _WaitEnergy(Action):

    def __init__(self, game):
        self.wait_until = routines.WaitUntil(game)
        super().__init__(game, "WAIT FOR ENERGY", self.wait_until.wait_until_energy)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="value",
                                                     text="Wait until energy value is equal or greater than",
                                                     initial_value=120,
                                                     max=9999))


class _WaitDailyReset(Action):

    def __init__(self, game):
        self.wait_until = routines.WaitUntil(game)
        super().__init__(game, "WAIT DAILY RESET", self.wait_until.wait_until_daily_reset)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="hour_offset",
                                                     text="Offset in hours before daily reset",
                                                     initial_value=0, min=0, max=24))


class _AcquireDispatchMissionRewards(Action):

    def __init__(self, game):
        self.dispatch_mission = DispatchMission(game)
        super().__init__(game, "DISPATCH MISSION: ACQUIRE ALL REWARDS", self.dispatch_mission.acquire_all_rewards)


class _AcquireAllGifts(Action):

    def __init__(self, game):
        self.inbox = routines.Inbox(game)
        super().__init__(game, "INBOX - GIFTS: ACQUIRE ALL", self.inbox.acquire_all_gifts)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Checkbox,
                                                     setting_key="acquire_energy",
                                                     text="Acquire energy",
                                                     initial_state=False))


class _AcquireFreeHeroChest(Action):

    def __init__(self, game):
        self.store = routines.CharacterStore(game)
        super().__init__(game, "STORE: ACQUIRE FREE HERO CHEST", self.store.acquire_free_hero_chest)


class _AcquireFreeArtifactChest(Action):

    def __init__(self, game):
        self.store = routines.ArtifactStore(game)
        super().__init__(game, "STORE: ACQUIRE FREE ARTIFACT CHEST", self.store.acquire_free_artifact_chest)


class _BuyArtifactChest(Action):
    artifact_chest = {
        "100k gold": routines.ArtifactStore.ARTIFACT_CHEST.GOLD_100,
        "250k gold": routines.ArtifactStore.ARTIFACT_CHEST.GOLD_250,
        "750k gold": routines.ArtifactStore.ARTIFACT_CHEST.GOLD_750,
        "1250k gold": routines.ArtifactStore.ARTIFACT_CHEST.GOLD_1250
    }

    def __init__(self, game):
        self.store = routines.ArtifactStore(game)
        super().__init__(game, "STORE: BUY ARTIFACT CHEST", self.store.buy_artifact_chest)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="chests_to_buy",
                                                     values_dict=self.artifact_chest))


class _AcquireAllChests(Action):

    def __init__(self, game):
        self.inbox = routines.Inbox(game)
        super().__init__(game, "INBOX - CHESTS: ACQUIRE ALL", self.inbox.acquire_all_chests)


class _ResetWorldBoss(Action):
    world_bosses = {
        "Proxima Midnight": missions.WorldBoss.BOSS_OF_THE_DAY.PROXIMA_MIDNIGHT,
        "Black Dwarf": missions.WorldBoss.BOSS_OF_THE_DAY.BLACK_DWARF,
        "Corvus Glave": missions.WorldBoss.BOSS_OF_THE_DAY.CORVUS_GLAIVE,
        "Supergiant": missions.WorldBoss.BOSS_OF_THE_DAY.SUPERGIANT,
        "Ebony Maw": missions.WorldBoss.BOSS_OF_THE_DAY.EBONY_MAW,
        "Thanos": missions.WorldBoss.BOSS_OF_THE_DAY.THANOS,
        "Quicksilver": missions.WorldBoss.BOSS_OF_THE_DAY.QUICKSILVER,
        "Cable": missions.WorldBoss.BOSS_OF_THE_DAY.CABLE,
        "Scarlet Witch": missions.WorldBoss.BOSS_OF_THE_DAY.SCARLET_WITCH,
        "Apocalypse": missions.WorldBoss.BOSS_OF_THE_DAY.APOCALYPSE,
        "Knull": missions.WorldBoss.BOSS_OF_THE_DAY.KNULL,
        "Mephisto": missions.WorldBoss.BOSS_OF_THE_DAY.MEPHISTO

    }

    def __init__(self, game):
        self.world_boss = missions.WorldBoss(game)
        super().__init__(game, "RESET TODAY'S WORLD BOSS", self.world_boss.change_world_boss_of_the_day)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="max_resets",
                                                     text="Max times of resets",
                                                     min=0, max=99, initial_value=99))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="world_boss",
                                                     values_dict=self.world_bosses))


class _SupportShopBuyMaterials(Action):
    material_list = {
        "Norn Stone of Strength (Red)": routines.SupportShop.MATERIALS.NORN_STONE_OF_STRENGTH,
        "Norn Stone of Energy (Blue)": routines.SupportShop.MATERIALS.NORN_STONE_OF_ENERGY,
        "Norn Stone of Brilliance (Green)": routines.SupportShop.MATERIALS.NORN_STONE_OF_BRILLIANCE,
        "Norn Stone of Omnipotence (Purple)": routines.SupportShop.MATERIALS.NORN_STONE_OF_OMNIPOTENCE,
        "M'Kraan Shard": routines.SupportShop.MATERIALS.MKRAAN_SHARD,
        "Gear Up Kit": routines.SupportShop.MATERIALS.GEAR_UP_KIT,
        "Dimension Debris": routines.SupportShop.MATERIALS.DIMENSION_DEBRIS,
        "Uniform Upgrade Kit": routines.SupportShop.MATERIALS.UNIFORM_UPGRADE_KIT,
    }

    def __init__(self, game):
        self.support_shop = routines.SupportShop(game)
        super().__init__(game, "SUPPORT SHOP: BUY MATERIALS", self.support_shop.buy_materials)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="materials_list",
                                                     values_dict=self.material_list))


class _Iso8Upgrade(Action):
    iso_to_upgrade = {
        "Upgrade Powerful (White)": routines.Iso8.ISO8_TYPE.POWERFUL,
        "Upgrade Amplifying (Red)": routines.Iso8.ISO8_TYPE.AMPLIFYING,
        "Upgrade Impregnable (Blue)": routines.Iso8.ISO8_TYPE.IMPREGNABLE,
        "Upgrade Absorbing (Green)": routines.Iso8.ISO8_TYPE.ABSORBING,
        "Upgrade Vital (Orange)": routines.Iso8.ISO8_TYPE.VITAL,
        "Upgrade Fierce (Yellow)": routines.Iso8.ISO8_TYPE.FIERCE,
        "Upgrade Nimble (Purple)": routines.Iso8.ISO8_TYPE.NIMBLE,
        "Upgrade Chaotic (Rainbow)": routines.Iso8.ISO8_TYPE.CHAOTIC
    }

    iso_to_use = {
        "Waste Powerful (White)": routines.Iso8.ISO8_TYPE_TO_USE.POWERFUL,
        "Waste Amplifying (Red)": routines.Iso8.ISO8_TYPE_TO_USE.AMPLIFYING,
        "Waste Impregnable (Blue)": routines.Iso8.ISO8_TYPE_TO_USE.IMPREGNABLE,
        "Waste Absorbing (Green)": routines.Iso8.ISO8_TYPE_TO_USE.ABSORBING,
        "Waste Vital (Orange)": routines.Iso8.ISO8_TYPE_TO_USE.VITAL,
        "Waste Fierce (Yellow)": routines.Iso8.ISO8_TYPE_TO_USE.FIERCE,
        "Waste Nimble (Purple)": routines.Iso8.ISO8_TYPE_TO_USE.NIMBLE,
        "Waste Chaotic (Rainbow)": routines.Iso8.ISO8_TYPE_TO_USE.CHAOTIC,
        "Waste Boost": routines.Iso8.ISO8_TYPE_TO_USE.BOOST
    }

    stars_to_use = {
        "Waste 1 star": routines.Iso8.ISO8_STARS_TO_USE.STAR_1,
        "Waste 2 star": routines.Iso8.ISO8_STARS_TO_USE.STAR_2,
        "Waste 3 star": routines.Iso8.ISO8_STARS_TO_USE.STAR_3,
        "Waste 4 star": routines.Iso8.ISO8_STARS_TO_USE.STAR_4,
        "Waste 5 star": routines.Iso8.ISO8_STARS_TO_USE.STAR_5,
        "Waste 6 star": routines.Iso8.ISO8_STARS_TO_USE.STAR_6,
    }

    def __init__(self, game):
        self.iso8 = routines.Iso8(game)
        super().__init__(game, "ISO-8: UPGRADE", self.iso8.upgrade_iso8)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="times_for_each_upgrade",
                                                     text="Select how many time to upgrade each of ISO-8 type",
                                                     min=0, max=99, initial_value=0))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="iso_to_upgrade",
                                                     values_dict=self.iso_to_upgrade))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="iso_to_use",
                                                     values_dict=self.iso_to_use,
                                                     add_to_next_column=True))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="stars_to_use",
                                                     values_dict=self.stars_to_use,
                                                     add_to_next_column=True))


class _Iso8Combine(Action):
    iso_to_combine = {
        "Combine Powerful (White)": routines.Iso8.ISO8_TYPE.POWERFUL,
        "Combine Amplifying (Red)": routines.Iso8.ISO8_TYPE.AMPLIFYING,
        "Combine Impregnable (Blue)": routines.Iso8.ISO8_TYPE.IMPREGNABLE,
        "Combine Absorbing (Green)": routines.Iso8.ISO8_TYPE.ABSORBING,
        "Combine Vital (Orange)": routines.Iso8.ISO8_TYPE.VITAL,
        "Combine Fierce (Yellow)": routines.Iso8.ISO8_TYPE.FIERCE,
        "Combine Nimble (Purple)": routines.Iso8.ISO8_TYPE.NIMBLE,
        "Combine Chaotic (Rainbow)": routines.Iso8.ISO8_TYPE.CHAOTIC
    }

    def __init__(self, game):
        self.iso8 = routines.Iso8(game)
        super().__init__(game, "ISO-8: COMBINE", self.iso8.combine_iso8)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.Spinbox,
                                                     setting_key="times_for_each_combine",
                                                     text="Select how many time to combine each of ISO-8 type",
                                                     min=0, max=99, initial_value=0))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="iso_to_combine",
                                                     values_dict=self.iso_to_combine))


class _Iso8Lock(Action):
    iso_to_lock = {
        "Powerful (White)": routines.Iso8.ISO8_TYPE.POWERFUL,
        "Amplifying (Red)": routines.Iso8.ISO8_TYPE.AMPLIFYING,
        "Impregnable (Blue)": routines.Iso8.ISO8_TYPE.IMPREGNABLE,
        "Absorbing (Green)": routines.Iso8.ISO8_TYPE.ABSORBING,
        "Vital (Orange)": routines.Iso8.ISO8_TYPE.VITAL,
        "Fierce (Yellow)": routines.Iso8.ISO8_TYPE.FIERCE,
        "Nimble (Purple)": routines.Iso8.ISO8_TYPE.NIMBLE,
        "Chaotic (Rainbow)": routines.Iso8.ISO8_TYPE.CHAOTIC
    }

    options_to_lock = {
        "Lock ALL ATTACK && ALL DEFENCE": routines.Iso8.ISO8_LOCK.ALL_ATTACK_AND_ALL_DEFENCE,
        "Lock ALL ATTACK && HP": routines.Iso8.ISO8_LOCK.ALL_ATTACK_AND_HP,
        "Lock PHYSICAL ATTACK && HP": routines.Iso8.ISO8_LOCK.PHYSICAL_ATTACK_AND_HP,
        "Lock ENERGY ATTACK && HP": routines.Iso8.ISO8_LOCK.ENERGY_ATTACK_AND_HP,
        "Lock any with ALL ATTACK": routines.Iso8.ISO8_LOCK.ALL_ATTACK,
        "Lock any with PHYSICAL ATTACK": routines.Iso8.ISO8_LOCK.PHYSICAL_ATTACK,
        "Lock any with ENERGY ATTACK": routines.Iso8.ISO8_LOCK.ENERGY_ATTACK,
        "Lock any with ALL DEFENCE": routines.Iso8.ISO8_LOCK.ALL_DEFENCE,
        "Lock any with PHYSICAL DEFENCE": routines.Iso8.ISO8_LOCK.PHYSICAL_DEFENCE,
        "Lock any with ENERGY DEFENCE": routines.Iso8.ISO8_LOCK.ENERGY_DEFENCE,
        "Lock any with HP": routines.Iso8.ISO8_LOCK.HP,
        "Lock any with CRITICAL RATE": routines.Iso8.ISO8_LOCK.CRITICAL_RATE,
        "Lock any with DODGE": routines.Iso8.ISO8_LOCK.DODGE,
    }

    def __init__(self, game):
        self.iso8 = routines.Iso8(game)
        super().__init__(game, "ISO-8: LOCK", self.iso8.lock_iso8)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="iso_to_lock",
                                                     values_dict=self.iso_to_lock))
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="options_to_lock",
                                                     values_dict=self.options_to_lock,
                                                     add_to_next_column=True))


class _ArtifactDismantle(Action):
    stars_to_dismantle = {
        "Dismantle 1 star": routines.Artifact.ARTIFACT_STARS.STAR_1,
        "Dismantle 2 star": routines.Artifact.ARTIFACT_STARS.STAR_2,
        "Dismantle 3 star": routines.Artifact.ARTIFACT_STARS.STAR_3,
        "Dismantle 4 star": routines.Artifact.ARTIFACT_STARS.STAR_4,
        "Dismantle 5 star": routines.Artifact.ARTIFACT_STARS.STAR_5,
        "Dismantle 6 star": routines.Artifact.ARTIFACT_STARS.STAR_6
    }

    def __init__(self, game):
        self.store = routines.Artifact(game)
        super().__init__(game, "ARTIFACT: DISMANTLE", self.store.dismantle_artifacts)
        self.mode_settings.append(Action.ModeSetting(setting_type=Action.ModeSetting.MultiCheckbox,
                                                     setting_key="artifact_stars",
                                                     values_dict=self.stars_to_dismantle))
