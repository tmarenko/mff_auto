﻿from lib.game.ui.general import UIElement, Rect, load_ui_image

COOP_PLAY_LABEL = UIElement(name='COOP_PLAY_LABEL')
COOP_PLAY_LABEL.description = "CO-OP label in mission selection."
COOP_PLAY_LABEL.text_rect = Rect(0.07857142857142857, 0.29733163913595934, 0.18428571428571427, 0.3392630241423126)
COOP_PLAY_LABEL.text = "CO-OP PLAY"
COOP_PLAY_LABEL.text_threshold = 150

COOP_PLAY_MENU_LABEL = UIElement(name='COOP_PLAY_MENU_LABEL')
COOP_PLAY_MENU_LABEL.description = "CO-OP LOBBY label at the top left corner of CO-OP menu."
COOP_PLAY_MENU_LABEL.text_rect = Rect(0.05142857142857143, 0.021601016518424398, 0.125, 0.07115628970775095)
COOP_PLAY_MENU_LABEL.text = "LOBBY"
COOP_PLAY_MENU_LABEL.text_threshold = 150

COOP_STAGE_PERCENTAGE = UIElement(name='COOP_STAGE_PERCENTAGE')
COOP_STAGE_PERCENTAGE.description = "CO-OP stage percentage."
COOP_STAGE_PERCENTAGE.text_rect = Rect(0.702614427911823, 0.7783171556004411, 0.7342956657932411, 0.8003159445711723)
COOP_STAGE_PERCENTAGE.text_threshold = 160
COOP_STAGE_PERCENTAGE.available_characters = "0123456789%"

COOP_DEPLOY_CHARACTER = UIElement(name='COOP_DEPLOY_CHARACTER')
COOP_DEPLOY_CHARACTER.description = "Deploy character message that shown if you haven't deployed a character."
COOP_DEPLOY_CHARACTER.text_rect = Rect(0.3942857142857143, 0.3875476493011436, 0.6078571428571429, 0.4485387547649301)
COOP_DEPLOY_CHARACTER.text = "Deploy a Character."
COOP_DEPLOY_CHARACTER.text_threshold = 120

COOP_FIRST_CHAR = UIElement(name='COOP_FIRST_CHAR')
COOP_FIRST_CHAR.description = "First available character to deploy."
COOP_FIRST_CHAR.button_rect = Rect(0.023443872902515484, 0.7888071323460268, 0.10569273969590628, 0.9403444384380925)

COOP_START_BUTTON = UIElement(name='COOP_START_BUTTON')
COOP_START_BUTTON.description = "COOP start button when character is deployed."
COOP_START_BUTTON.text_rect = Rect(0.8578960123700078, 0.8805270807701718, 0.9446311809884927, 0.9469908115123059)
COOP_START_BUTTON.button_rect = Rect(0.8578960123700078, 0.8805270807701718, 0.9446311809884927, 0.9469908115123059)
COOP_START_BUTTON.text = "START"
COOP_START_BUTTON.text_threshold = 150

COOP_START_BUTTON_INACTIVE = UIElement(name='COOP_START_BUTTON_INACTIVE')
COOP_START_BUTTON_INACTIVE.description = "COOP start button when no character was deployed."
COOP_START_BUTTON_INACTIVE.text_rect = Rect(0.8578960123700078, 0.8805270807701718, 0.9446311809884927, 0.9469908115123059)
COOP_START_BUTTON_INACTIVE.button_rect = Rect(0.8578960123700078, 0.8805270807701718, 0.9446311809884927, 0.9469908115123059)
COOP_START_BUTTON_INACTIVE.text = "START"
COOP_START_BUTTON_INACTIVE.text_threshold = 20

COOP_REWARD = UIElement(name='COOP_REWARD')
COOP_REWARD.description = "COOP get reward button."
COOP_REWARD.text_rect = Rect(0.8242487486818023, 0.8818563553850144, 0.9820170295309432, 0.9469908115123059)
COOP_REWARD.button_rect = Rect(0.8242487486818023, 0.8818563553850144, 0.9820170295309432, 0.9469908115123059)
COOP_REWARD.text = "Reward Acquired"
COOP_REWARD.text_threshold = 150

COOP_REWARD_ACQUIRE = UIElement(name='COOP_REWARD_ACQUIRE')
COOP_REWARD_ACQUIRE.description = "COOP reward acquire windows with OK button to close it."
COOP_REWARD_ACQUIRE.text_rect = Rect(0.47207405541191994, 0.7595630908194879, 0.5266573942838976, 0.8207097231022513)
COOP_REWARD_ACQUIRE.button_rect = Rect(0.47207405541191994, 0.7595630908194879, 0.5266573942838976, 0.8207097231022513)
COOP_REWARD_ACQUIRE.text = "OK"
COOP_REWARD_ACQUIRE.text_threshold = 120
COOP_REWARD_ACQUIRE.available_characters = "OK"

COOP_REWARD_ACQUIRE_CONFIRM = UIElement(name='COOP_REWARD_ACQUIRE_CONFIRM')
COOP_REWARD_ACQUIRE_CONFIRM.description = "COOP reward acquire confirm window (for first reward)."
COOP_REWARD_ACQUIRE_CONFIRM.text_rect = Rect(0.5354531186506587, 0.7239043166136473, 0.6210184720082992, 0.7685172025445903)
COOP_REWARD_ACQUIRE_CONFIRM.button_rect = Rect(0.5354531186506587, 0.7239043166136473, 0.6210184720082992, 0.7685172025445903)
COOP_REWARD_ACQUIRE_CONFIRM.text = "ACQUIRE"
COOP_REWARD_ACQUIRE_CONFIRM.text_threshold = 160

COOP_REWARD_ACQUIRE_CONFIRM_TICKETS = UIElement(name='COOP_REWARD_ACQUIRE_CONFIRM_TICKETS')
COOP_REWARD_ACQUIRE_CONFIRM_TICKETS.description = "COOP reward acquire confirm window with tickets (for others reward)."
COOP_REWARD_ACQUIRE_CONFIRM_TICKETS.text_rect = Rect(0.6, 0.7331639135959339, 0.6785714285714286, 0.7776365946632783)
COOP_REWARD_ACQUIRE_CONFIRM_TICKETS.button_rect = Rect(0.4835714285714286, 0.7242693773824651, 0.6835714285714286, 0.7801778907242694)
COOP_REWARD_ACQUIRE_CONFIRM_TICKETS.text = "ACQUIRE"
COOP_REWARD_ACQUIRE_CONFIRM_TICKETS.text_threshold = 160

COOP_REPEAT_TOGGLE = UIElement(name='COOP_REPEAT_TOGGLE')
COOP_REPEAT_TOGGLE.description = "Toggle for repeat."
COOP_REPEAT_TOGGLE.image_rect = Rect(0.8307291666666666, 0.7731481481481481, 0.8505208333333333, 0.8083333333333333)
COOP_REPEAT_TOGGLE.button_rect = Rect(0.8307291666666666, 0.7731481481481481, 0.8505208333333333, 0.8083333333333333)
COOP_REPEAT_TOGGLE.image_threshold = 0.7
COOP_REPEAT_TOGGLE.image = load_ui_image("repeat_toggle.png")

COOP_QUICK_MATCH_TOGGLE = UIElement(name='COOP_QUICK_MATCH_TOGGLE')
COOP_QUICK_MATCH_TOGGLE.description = "Toggle for quick match."
COOP_QUICK_MATCH_TOGGLE.image_rect = Rect(0.8307291666666666, 0.8194444444444444, 0.8505208333333333, 0.8546296296296296)
COOP_QUICK_MATCH_TOGGLE.button_rect = Rect(0.8307291666666666, 0.8194444444444444, 0.8505208333333333, 0.8546296296296296)
COOP_QUICK_MATCH_TOGGLE.image_threshold = 0.7
COOP_QUICK_MATCH_TOGGLE.image = load_ui_image("repeat_toggle.png")
