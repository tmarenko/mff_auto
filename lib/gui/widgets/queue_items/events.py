from lib.gui.widgets.queue_items.general import Event
import lib.game.missions as missions


class _EventWorldBoss(Event):

    def __init__(self, game):
        self.event_world_boss = missions.EventWorldBoss(game)
        super().__init__(game, "EVENT WORLD BOSS", self.event_world_boss.complete_event_world_boss)


class _WorldEvent(Event):

    def __init__(self, game):
        self.event_world_boss = missions.WorldEvent(game)
        super().__init__(game, "WORLD EVENT", self.event_world_boss.complete_world_event)


class _FuturePass(Event):

    def __init__(self, game):
        self.future_pass = missions.FuturePass(game)
        super().__init__(game, "FUTURE PASS: COLLECT POINTS AND CLAIM REWARDS",
                         self.future_pass.acquire_points_and_claim_rewards)
