﻿from lib.game.ui.general import UIElement, Rect, load_ui_image

TEAM = UIElement(name='TEAM')
TEAM.description = "Team button in main menu. Main identifier that main menu is opened."
TEAM.text_rect = Rect(0.006246382572988315, 0.4405371832572446, 0.10943132455015132, 0.521622934762648)
TEAM.text = "TEAM"
TEAM.text_threshold = 155

STORE = UIElement(name='STORE')
STORE.description = "Team button in main menu. Main identifier that main menu is opened."
STORE.text_rect = Rect(0.008489533485535331, 0.32356101715108876, 0.11391762637524536, 0.39800039558227884)
STORE.text = "STORE"
STORE.text_threshold = 155

MAIN_MENU_AD = UIElement(name='MAIN_MENU_AD')
MAIN_MENU_AD.description = "The X-button of closing ads in main menu."
MAIN_MENU_AD.text_rect = Rect(0.8496583143507973, 0.11133603238866396, 0.8826879271070615, 0.16700404858299595)
MAIN_MENU_AD.button_rect = Rect(0.8496583143507973, 0.11133603238866396, 0.8826879271070615, 0.16700404858299595)
MAIN_MENU_AD.text = "X"
MAIN_MENU_AD.text_threshold = 55
MAIN_MENU_AD.available_characters = "X"

MAIN_MENU_AD_2 = UIElement(name='MAIN_MENU_AD_2')
MAIN_MENU_AD_2.description = "The X-button of closing ads in main menu."
MAIN_MENU_AD_2.text_rect = Rect(0.8484375, 0.11203703703703703, 0.8802083333333334, 0.1685185185185185)
MAIN_MENU_AD_2.button_rect = Rect(0.8484375, 0.11203703703703703, 0.8802083333333334, 0.1685185185185185)
MAIN_MENU_AD_2.text = "X"
MAIN_MENU_AD_2.text_threshold = 55
MAIN_MENU_AD_2.available_characters = "X"

MAIN_MENU_AD_3 = UIElement(name='MAIN_MENU_AD_3')
MAIN_MENU_AD_3.description = "The X-button of closing ads in main menu."
MAIN_MENU_AD_3.text_rect = Rect(0.915625, 0.037037037037037035, 0.9494791666666667, 0.09537037037037037)
MAIN_MENU_AD_3.button_rect = Rect(0.915625, 0.037037037037037035, 0.9494791666666667, 0.09537037037037037)
MAIN_MENU_AD_3.text = "X"
MAIN_MENU_AD_3.text_threshold = 55
MAIN_MENU_AD_3.available_characters = "X"

MAIN_MENU_AD_4 = UIElement(name='MAIN_MENU_AD_4')
MAIN_MENU_AD_4.description = "The X-button of closing ads in main menu."
MAIN_MENU_AD_4.text_rect = Rect(0.9239583333333333, 0.028703703703703703, 0.9427083333333334, 0.06018518518518518)
MAIN_MENU_AD_4.button_rect = Rect(0.9239583333333333, 0.028703703703703703, 0.9427083333333334, 0.06018518518518518)
MAIN_MENU_AD_4.text = "X"
MAIN_MENU_AD_4.text_threshold = 55
MAIN_MENU_AD_4.available_characters = "X"

MAIN_MENU_REWARDS = UIElement(name='MAIN_MENU_REWARDS')
MAIN_MENU_REWARDS.description = "The X-button of closing daily rewards in main menu."
MAIN_MENU_REWARDS.text_rect = Rect(0.9546875, 0.021296296296296296, 0.9854166666666667, 0.07592592592592592)
MAIN_MENU_REWARDS.button_rect = Rect(0.9546875, 0.021296296296296296, 0.9854166666666667, 0.07592592592592592)
MAIN_MENU_REWARDS.text = "X"
MAIN_MENU_REWARDS.text_threshold = 55
MAIN_MENU_REWARDS.available_characters = "X"

MAIN_MENU_REWARDS_OK = UIElement(name='MAIN_MENU_REWARDS_OK')
MAIN_MENU_REWARDS_OK.description = "OK-button of closing window with daily rewards in main menu.,."
MAIN_MENU_REWARDS_OK.text_rect = Rect(0.47880350814956096, 0.718355577759365, 0.5199279415462564, 0.7688680131233866)
MAIN_MENU_REWARDS_OK.button_rect = Rect(0.47880350814956096, 0.718355577759365, 0.5199279415462564, 0.7688680131233866)
MAIN_MENU_REWARDS_OK.text = "OK"
MAIN_MENU_REWARDS_OK.text_threshold = 150
MAIN_MENU_REWARDS_OK.available_characters = "OK"

ENTER_MISSIONS = UIElement(name='ENTER_MISSIONS')
ENTER_MISSIONS.description = "The ENTER button in main menu, that opens missions selection."
ENTER_MISSIONS.text_rect = Rect(0.8369599371862357, 0.8858441792295425, 0.9244428227755696, 0.9576250084310471)
ENTER_MISSIONS.button_rect = Rect(0.8369599371862357, 0.8858441792295425, 0.9244428227755696, 0.9576250084310471)
ENTER_MISSIONS.text = "ENTER"
ENTER_MISSIONS.text_threshold = 120

COOP_MISSIONS = UIElement(name='COOP_MISSIONS')
COOP_MISSIONS.description = "COOP button in mission selection."
COOP_MISSIONS.text_rect = Rect(0.8086592518379722, 0.15959673986983558, 0.8797998986329839, 0.2103637742024261)
COOP_MISSIONS.button_rect = Rect(0.8086592518379722, 0.15959673986983558, 0.8797998986329839, 0.2103637742024261)
COOP_MISSIONS.text = "CO-OP"
COOP_MISSIONS.text_threshold = 130
COOP_MISSIONS.available_characters = "CO-OP"

NEWS_ON_START_GAME = UIElement(name='NEWS_ON_START_GAME')
NEWS_ON_START_GAME.description = "News that can be shown at game loading. You can close it."
NEWS_ON_START_GAME.text_rect = Rect(0.09635416666666667, 0.8796296296296297, 0.2453125, 0.9222222222222223)
NEWS_ON_START_GAME.button_rect = Rect(0.09635416666666667, 0.8796296296296297, 0.2453125, 0.9222222222222223)
NEWS_ON_START_GAME.text = "Don't Show for Today"
NEWS_ON_START_GAME.text_threshold = 130

MAINTENANCE_NOTICE = UIElement(name='MAINTENANCE_NOTICE')
MAINTENANCE_NOTICE.description = "Maintenance notification on game start. Leads to CLOSE button."
MAINTENANCE_NOTICE.text_rect = Rect(0.4660923196451279, 0.8738807076959585, 0.5363777149049346, 0.9270516922896657)
MAINTENANCE_NOTICE.button_rect = Rect(0.4660923196451279, 0.8738807076959585, 0.5363777149049346, 0.9270516922896657)
MAINTENANCE_NOTICE.text = "CLOSE"
MAINTENANCE_NOTICE.text_threshold = 130

MAINTENANCE_NOTICE_ACQUIRE = UIElement(name='MAINTENANCE_NOTICE_ACQUIRE')
MAINTENANCE_NOTICE_ACQUIRE.description = "Maintenance notification on game start. Leads to ACQUIRE button."
MAINTENANCE_NOTICE_ACQUIRE.text_rect = Rect(0.5326391300506894, 0.8659050600069023, 0.6261037514068154, 0.9270516922896657)
MAINTENANCE_NOTICE_ACQUIRE.button_rect = Rect(0.5326391300506894, 0.8659050600069023, 0.6261037514068154, 0.9270516922896657)
MAINTENANCE_NOTICE_ACQUIRE.text = "ACQUIRE"
MAINTENANCE_NOTICE_ACQUIRE.text_threshold = 130

MAINTENANCE_NOTICE_ACQUIRE_OK = UIElement(name='MAINTENANCE_NOTICE_ACQUIRE_OK')
MAINTENANCE_NOTICE_ACQUIRE_OK.description = "Maintenance notification on game start. Notification after acquiring. Leads to OK button."
MAINTENANCE_NOTICE_ACQUIRE_OK.text_rect = Rect(0.44665167840305375, 0.16670661259965244, 0.5535752052344617, 0.22918251949725849)
MAINTENANCE_NOTICE_ACQUIRE_OK.button_rect = Rect(0.477308074207863, 0.7130384792999941, 0.5236665264005015, 0.7728558369679147)
MAINTENANCE_NOTICE_ACQUIRE_OK.text = "ACQUIRE"
MAINTENANCE_NOTICE_ACQUIRE_OK.text_threshold = 130

MAIN_MENU_AD_CLOSE = UIElement(name='MAIN_MENU_AD_CLOSE')
MAIN_MENU_AD_CLOSE.description = "Position of OK-button when you are trying to close ad in main menu."
MAIN_MENU_AD_CLOSE.text_rect = Rect(0.5535666627690687, 0.7148536225464859, 0.6052515933830781, 0.7736168511515608)
MAIN_MENU_AD_CLOSE.button_rect = Rect(0.5535666627690687, 0.7148536225464859, 0.6052515933830781, 0.7736168511515608)
MAIN_MENU_AD_CLOSE.text = "OK"
MAIN_MENU_AD_CLOSE.text_threshold = 150
MAIN_MENU_AD_CLOSE.available_characters = "OK"

HOME = UIElement(name='HOME')
HOME.description = "Home button in top navigation bar that leads you to main menu."
HOME.image_rect = Rect(0.9135416666666667, 0.026851851851851852, 0.9395833333333333, 0.07314814814814814)
HOME.button_rect = Rect(0.9135416666666667, 0.026851851851851852, 0.9395833333333333, 0.07314814814814814)
HOME.image_threshold = 0.6
HOME.image = load_ui_image("main_menu_button.png")

GAME_APP = UIElement(name='GAME_APP')
GAME_APP.description = "Position of the app name on emulator's desktop."
GAME_APP.text_rect = Rect(0.5, 0.5, 0.5, 0.5)
GAME_APP.button_rect = Rect(0.5, 0.5, 0.5, 0.5)
GAME_APP.text = "Future Fight"
GAME_APP.text_threshold = 125

USER_NAME = UIElement(name='USER_NAME')
USER_NAME.description = "Position of user name in top navigation bar."
USER_NAME.text_rect = Rect(0.0040032316604412975, 0.02314495419664295, 0.1453217391509037, 0.07099884033097952)
USER_NAME.text_threshold = 155

ENERGY = UIElement(name='ENERGY')
ENERGY.description = "Position of energy counter in top navigation bar."
ENERGY.text_rect = Rect(0.40360971277466484, 0.028676049789068573, 0.4693535314333067, 0.06167028945613814)
ENERGY.text_threshold = 175
ENERGY.available_characters = "0123456789/,"

GOLD = UIElement(name='GOLD')
GOLD.description = "Position of gold counter in top navigation bar."
GOLD.text_rect = Rect(0.5184254726330584, 0.032590620597026, 0.5901460020788496, 0.06446641146182204)
GOLD.text_threshold = 150
GOLD.available_characters = "0123456789,"

BOOST = UIElement(name='BOOST')
BOOST.description = "Position of boost counter in top navigation bar."
BOOST.text_rect = Rect(0.7345307521473501, 0.032590620597026, 0.7848609482496597, 0.06390718706068522)
BOOST.text_threshold = 155
BOOST.available_characters = "0123456789"

CONTENT_STATUS_BOARD_BUTTON = UIElement(name='CONTENT_STATUS_BOARD_BUTTON')
CONTENT_STATUS_BOARD_BUTTON.description = "Button to content status board in main menu."
CONTENT_STATUS_BOARD_BUTTON.button_rect = Rect(0.7255610317235944, 0.8822245744720514, 0.7699147647575799, 0.961261187376534)

CONTENT_STATUS_BOARD_LABEL = UIElement(name='CONTENT_STATUS_BOARD_LABEL')
CONTENT_STATUS_BOARD_LABEL.description = "Label of content status board."
CONTENT_STATUS_BOARD_LABEL.text_rect = Rect(0.052083333333333336, 0.003703703703703704, 0.23125, 0.09259259259259259)
CONTENT_STATUS_BOARD_LABEL.text = "CONTENT STATUS BOARD"
CONTENT_STATUS_BOARD_LABEL.text_threshold = 120

CONTENT_STATUS_BOARD_1 = UIElement(name='CONTENT_STATUS_BOARD_1')
CONTENT_STATUS_BOARD_1.description = "Position of first half of content status board. Contains info about stages."
CONTENT_STATUS_BOARD_1.button_rect = Rect(0.05625, 0.2462962962962963, 0.94375, 0.8148148148148148)

CONTENT_STATUS_BOARD_2 = UIElement(name='CONTENT_STATUS_BOARD_2')
CONTENT_STATUS_BOARD_2.description = "Position of second half of content status board. Contains info about stages."
CONTENT_STATUS_BOARD_2.button_rect = Rect(0.05520833333333333, 0.34274074074074073, 0.94375, 0.9092592592592592)

CONTENT_STATUS_ELEMENT_1 = UIElement(name='CONTENT_STATUS_ELEMENT_1')
CONTENT_STATUS_ELEMENT_1.description = "Local position of any element in content status board 1. Can be translated to any col/row. Button rect contains offset info for col/row."
CONTENT_STATUS_ELEMENT_1.button_rect = Rect(0.0, 0.0, 0.32629107981220656, 0.2280130293159609)
CONTENT_STATUS_ELEMENT_1.offset = Rect(0.0, 0.0, 0.01039518496770405, 0.028417910447761194)

CONTENT_STATUS_ELEMENT_LABEL = UIElement(name='CONTENT_STATUS_ELEMENT_LABEL')
CONTENT_STATUS_ELEMENT_LABEL.description = "Local position of stage label and button inside content status element."
CONTENT_STATUS_ELEMENT_LABEL.text_rect = Rect(0.02154398563734291, 0.14285714285714285, 0.6678635547576302, 0.5142857142857142)
CONTENT_STATUS_ELEMENT_LABEL.text_threshold = 170

CONTENT_STATUS_ELEMENT_STAGE = UIElement(name='CONTENT_STATUS_ELEMENT_STAGE')
CONTENT_STATUS_ELEMENT_STAGE.description = "Local position of stage counter inside content status element."
CONTENT_STATUS_ELEMENT_STAGE.text_rect = Rect(0.7630161579892281, 0.3357142857142857, 0.9353680430879713, 0.6214285714285714)
CONTENT_STATUS_ELEMENT_STAGE.text_threshold = 160
CONTENT_STATUS_ELEMENT_STAGE.available_characters = "1234567890/"

CONTENT_STATUS_DRAG_FROM = UIElement(name='CONTENT_STATUS_DRAG_FROM')
CONTENT_STATUS_DRAG_FROM.description = "Start position of dragging board to see others elements."
CONTENT_STATUS_DRAG_FROM.button_rect = Rect(0.7640625, 0.6462962962962963, 0.8104166666666667, 0.725925925925926)

CONTENT_STATUS_DRAG_TO = UIElement(name='CONTENT_STATUS_DRAG_TO')
CONTENT_STATUS_DRAG_TO.description = "End position of dragging board to see others elements."
CONTENT_STATUS_DRAG_TO.button_rect = Rect(0.7640625, 0.2659259259259259, 0.8104166666666667, 0.34555555555555556)

MENU_BACK = UIElement(name='MENU_BACK')
MENU_BACK.description = "Back button in menus."
MENU_BACK.button_rect = Rect(0.016564922115597916, 0.030490300712176312, 0.03558447870697902, 0.06186011437197852)

LOADING_CIRCLE_1 = UIElement(name='LOADING_CIRCLE_1')
LOADING_CIRCLE_1.description = "Position in the loading circle for checking the color. Button contains RGBA color value of circle."
LOADING_CIRCLE_1.image_rect = Rect(0.5, 0.4537037037037037, 0.5, 0.4537037037037037)
LOADING_CIRCLE_1.image_color = (255, 140, 0)

LOADING_CIRCLE_2 = UIElement(name='LOADING_CIRCLE_2')
LOADING_CIRCLE_2.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_2.image_rect = Rect(0.5, 0.5462962962962963, 0.5, 0.5462962962962963)

LOADING_CIRCLE_3 = UIElement(name='LOADING_CIRCLE_3')
LOADING_CIRCLE_3.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_3.image_rect = Rect(0.4739583333333333, 0.5, 0.4739583333333333, 0.5)

LOADING_CIRCLE_4 = UIElement(name='LOADING_CIRCLE_4')
LOADING_CIRCLE_4.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_4.image_rect = Rect(0.5260416666666666, 0.5, 0.5260416666666666, 0.5)

LOADING_CIRCLE_5 = UIElement(name='LOADING_CIRCLE_5')
LOADING_CIRCLE_5.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_5.image_rect = Rect(0.4817708333333333, 0.46296296296296297, 0.4817708333333333, 0.46296296296296297)

LOADING_CIRCLE_6 = UIElement(name='LOADING_CIRCLE_6')
LOADING_CIRCLE_6.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_6.image_rect = Rect(0.5182291666666666, 0.46296296296296297, 0.5182291666666666, 0.46296296296296297)

LOADING_CIRCLE_7 = UIElement(name='LOADING_CIRCLE_7')
LOADING_CIRCLE_7.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_7.image_rect = Rect(0.5208333333333334, 0.5277777777777778, 0.5208333333333334, 0.5277777777777778)

LOADING_CIRCLE_8 = UIElement(name='LOADING_CIRCLE_8')
LOADING_CIRCLE_8.description = "Position in the loading circle for checking the color."
LOADING_CIRCLE_8.image_rect = Rect(0.4791666666666667, 0.5277777777777778, 0.4791666666666667, 0.5277777777777778)

MAIN_MENU = UIElement(name='MAIN_MENU')
MAIN_MENU.description = "Main Menu button."
MAIN_MENU.text_rect = Rect(0.9584238425925697, 0.02848973614409105, 0.9839579164645923, 0.07222693323874806)
MAIN_MENU.button_rect = Rect(0.9584238425925697, 0.02848973614409105, 0.9839579164645923, 0.07222693323874806)
MAIN_MENU.text = "X"
MAIN_MENU.text_threshold = 120
MAIN_MENU.available_characters = "X"

MAIN_MENU_CHALLENGES = UIElement(name='MAIN_MENU_CHALLENGES')
MAIN_MENU_CHALLENGES.description = "Main Menu Challenges button."
MAIN_MENU_CHALLENGES.text_rect = Rect(0.8429416729530277, 0.5628304478227711, 0.9199565209504754, 0.5960623131938382)
MAIN_MENU_CHALLENGES.button_rect = Rect(0.8564005784283097, 0.48041542170252505, 0.9042544645626461, 0.5482084270595016)
MAIN_MENU_CHALLENGES.text = "CHALLENGES"
MAIN_MENU_CHALLENGES.text_threshold = 150

MAIN_MENU_LAB = UIElement(name='MAIN_MENU_LAB')
MAIN_MENU_LAB.description = "Main Menu Lab button."
MAIN_MENU_LAB.text_rect = Rect(0.7936685021488451, 0.5901337014102112, 0.8293949992672005, 0.6214020202556777)
MAIN_MENU_LAB.button_rect = Rect(0.7832253722219412, 0.469946100847949, 0.8381892139424879, 0.5657053273121904)
MAIN_MENU_LAB.text = "LAB"
MAIN_MENU_LAB.text_threshold = 150

MAIN_MENU_CARDS = UIElement(name='MAIN_MENU_CARDS')
MAIN_MENU_CARDS.description = "Main Menu Card button."
MAIN_MENU_CARDS.text_rect = Rect(0.5984382234854022, 0.38470764943385205, 0.6380672229403996, 0.41793951480491903)
MAIN_MENU_CARDS.button_rect = Rect(0.5932042046894591, 0.30096334869876323, 0.6403103738529466, 0.3714149032854252)
MAIN_MENU_CARDS.text = "CARD"
MAIN_MENU_CARDS.text_threshold = 150

MAIN_MENU_INVENTORY = UIElement(name='MAIN_MENU_INVENTORY')
MAIN_MENU_INVENTORY.description = "Main Menu Inventory button."
MAIN_MENU_INVENTORY.text_rect = Rect(0.8990204457667031, 0.3833783748190094, 0.9685581240556609, 0.41793951480491903)
MAIN_MENU_INVENTORY.button_rect = Rect(0.9124793512419854, 0.29963407408392045, 0.9550992185803788, 0.3714149032854252)
MAIN_MENU_INVENTORY.text = "INVENTORY"
MAIN_MENU_INVENTORY.text_threshold = 150

MAIN_MENU_FRIENDS = UIElement(name='MAIN_MENU_FRIENDS')
MAIN_MENU_FRIENDS.description = "Main Menu Friends button."
MAIN_MENU_FRIENDS.text_rect = Rect(0.8010695225854831, 0.738294696982005, 0.8578960123700078, 0.7781729354272855)
MAIN_MENU_FRIENDS.button_rect = Rect(0.8085466922939732, 0.6611967693211295, 0.8489234087198196, 0.7223434016038928)
MAIN_MENU_FRIENDS.text = "FRIENDS"
MAIN_MENU_FRIENDS.text_threshold = 150

MAIN_MENU_ALLIANCE = UIElement(name='MAIN_MENU_ALLIANCE')
MAIN_MENU_ALLIANCE.description = "Main Menu Alliance button."
MAIN_MENU_ALLIANCE.text_rect = Rect(0.6941459957540752, 0.7396239715968477, 0.7539633534219958, 0.7741851115827575)
MAIN_MENU_ALLIANCE.button_rect = Rect(0.7038663163751122, 0.6585382200914442, 0.7419998818884117, 0.7250019508335782)
MAIN_MENU_ALLIANCE.text = "ALLIANCE"
MAIN_MENU_ALLIANCE.text_threshold = 150

MAIN_MENU_INBOX = UIElement(name='MAIN_MENU_INBOX')
MAIN_MENU_INBOX.description = "Main Menu Inbox button."
MAIN_MENU_INBOX.text_rect = Rect(0.9124793512419854, 0.738294696982005, 0.9543515016095299, 0.771526562353072)
MAIN_MENU_INBOX.button_rect = Rect(0.9132270682128343, 0.6572089454766016, 0.9550992185803788, 0.7236726762187355)
MAIN_MENU_INBOX.text = "INBOX"
MAIN_MENU_INBOX.text_threshold = 150

CHALLENGE_COMPLETE_NOTIFICATION = UIElement(name='CHALLENGE_COMPLETE_NOTIFICATION')
CHALLENGE_COMPLETE_NOTIFICATION.description = "Notification of completion of some challenge."
CHALLENGE_COMPLETE_NOTIFICATION.text_rect = Rect(0.79757343550447, 0.775, 0.9208173690932312, 0.8227272727272728)
CHALLENGE_COMPLETE_NOTIFICATION.button_rect = Rect(0.7969348659003831, 0.8670454545454546, 0.9227330779054917, 0.9204545454545454)
CHALLENGE_COMPLETE_NOTIFICATION.text = "CHALLENGES"
CHALLENGE_COMPLETE_NOTIFICATION.text_threshold = 120

ALLIANCE_CONQUEST_NOTIFICATION = UIElement(name='ALLIANCE_CONQUEST_NOTIFICATION')
ALLIANCE_CONQUEST_NOTIFICATION.description = "Notification of Alliance Conquest at the start of the game."
ALLIANCE_CONQUEST_NOTIFICATION.text_rect = Rect(0.36822916666666666, 0.837037037037037, 0.440625, 0.8953703703703704)
ALLIANCE_CONQUEST_NOTIFICATION.button_rect = Rect(0.36822916666666666, 0.837037037037037, 0.440625, 0.8953703703703704)
ALLIANCE_CONQUEST_NOTIFICATION.text = "CLOSE"
ALLIANCE_CONQUEST_NOTIFICATION.text_threshold = 150

GOLD_ICON = UIElement(name='GOLD_ICON')
GOLD_ICON.description = "Gold icon image."
GOLD_ICON.image_rect = Rect(0.5, 0.037037037037037035, 0.5130208333333334, 0.062037037037037036)
GOLD_ICON.button_rect = Rect(0.5, 0.037037037037037035, 0.5130208333333334, 0.062037037037037036)
GOLD_ICON.image_threshold = 0.7
GOLD_ICON.image = load_ui_image("gold_image.png")

SELECT_MISSION = UIElement(name='SELECT_MISSION')
SELECT_MISSION.description = "The SELECT MISSION label in mission selector."
SELECT_MISSION.text_rect = Rect(0.0515625, 0.010185185185185186, 0.19947916666666668, 0.08333333333333333)
SELECT_MISSION.text = "SELECT MISSION"
SELECT_MISSION.text_threshold = 120

EPIC_QUEST_MISSIONS = UIElement(name='EPIC_QUEST_MISSIONS')
EPIC_QUEST_MISSIONS.description = "The EPIC QUEST selector in mission selector."
EPIC_QUEST_MISSIONS.text_rect = Rect(0.77340399466407, 0.27437785640190965, 0.872102634816139, 0.32356101715108876)
EPIC_QUEST_MISSIONS.button_rect = Rect(0.8010695225854831, 0.36742707944089725, 0.9767830107349998, 0.6837944377734552)
EPIC_QUEST_MISSIONS.text = "EPIC QUEST"
EPIC_QUEST_MISSIONS.text_threshold = 120

BIOMETRICS_NOTIFICATION = UIElement(name='BIOMETRICS_NOTIFICATION')
BIOMETRICS_NOTIFICATION.description = "Notification of Biometrics subscription."
BIOMETRICS_NOTIFICATION.text_rect = Rect(0.3050899618978798, 0.7138398630534284, 0.38801468845322745, 0.7728085574927868)
BIOMETRICS_NOTIFICATION.button_rect = Rect(0.33972815157164565, 0.8512830392436328, 0.6560124302407757, 0.9350273399787217)
BIOMETRICS_NOTIFICATION.text = "SELECT"
BIOMETRICS_NOTIFICATION.text_threshold = 120

X_GENE_NOTIFICATION = UIElement(name='X_GENE_NOTIFICATION')
X_GENE_NOTIFICATION.description = "Notification of X-Gene subscription."
X_GENE_NOTIFICATION.text_rect = Rect(0.6109001729995523, 0.7102442109534672, 0.6942294104161457, 0.7749659487527633)
X_GENE_NOTIFICATION.button_rect = Rect(0.33972815157164565, 0.8512830392436328, 0.6560124302407757, 0.9350273399787217)
X_GENE_NOTIFICATION.text = "SELECT"
X_GENE_NOTIFICATION.text_threshold = 120

ALLIANCE_CONQUEST_REWARDS_ACQUIRE = UIElement(name='ALLIANCE_CONQUEST_REWARDS_ACQUIRE')
ALLIANCE_CONQUEST_REWARDS_ACQUIRE.description = "Alliance Conquest Results notification: acquire rewards."
ALLIANCE_CONQUEST_REWARDS_ACQUIRE.text_rect = Rect(0.45416666666666666, 0.899074074074074, 0.5494791666666666, 0.9555555555555556)
ALLIANCE_CONQUEST_REWARDS_ACQUIRE.button_rect = Rect(0.45416666666666666, 0.899074074074074, 0.5494791666666666, 0.9555555555555556)
ALLIANCE_CONQUEST_REWARDS_ACQUIRE.text = "ACQUIRE"
ALLIANCE_CONQUEST_REWARDS_ACQUIRE.text_threshold = 150

ALLIANCE_CONQUEST_REWARDS_CLOSE = UIElement(name='ALLIANCE_CONQUEST_REWARDS_CLOSE')
ALLIANCE_CONQUEST_REWARDS_CLOSE.description = "Alliance Conquest Results notification: close acquired rewards."
ALLIANCE_CONQUEST_REWARDS_CLOSE.text_rect = Rect(0.46684003661597695, 0.7489288939007465, 0.5348822809632365, 0.7981120546499255)
ALLIANCE_CONQUEST_REWARDS_CLOSE.button_rect = Rect(0.46684003661597695, 0.7489288939007465, 0.5348822809632365, 0.7981120546499255)
ALLIANCE_CONQUEST_REWARDS_CLOSE.text = "CLOSE"
ALLIANCE_CONQUEST_REWARDS_CLOSE.text_threshold = 120

NETWORK_ERROR_NOTIFICATION = UIElement(name='NETWORK_ERROR_NOTIFICATION')
NETWORK_ERROR_NOTIFICATION.description = "Network error notification. Can be anywhere. Leads to OK button."
NETWORK_ERROR_NOTIFICATION.text_rect = Rect(0.3452265534037128, 0.428525349727345, 0.6554730888470826, 0.4783963392783423)
NETWORK_ERROR_NOTIFICATION.button_rect = Rect(0.5539500029754094, 0.7135024328759014, 0.6077171635850784, 0.7740600630449695)
NETWORK_ERROR_NOTIFICATION.text = "Unable to establish network connection."
NETWORK_ERROR_NOTIFICATION.text_threshold = 120

NETWORK_ERROR_NOTIFICATION_2 = UIElement(name='NETWORK_ERROR_NOTIFICATION_2')
NETWORK_ERROR_NOTIFICATION_2.description = "Network error notification. Can be anywhere. Leads to OK button."
NETWORK_ERROR_NOTIFICATION_2.text_rect = Rect(0.3277646800380615, 0.4485128309463008, 0.673957637541152, 0.5030130901548506)
NETWORK_ERROR_NOTIFICATION_2.button_rect = Rect(0.47880350814956096, 0.7130384792999941, 0.5259096773130485, 0.7755143861976)
NETWORK_ERROR_NOTIFICATION_2.text = "Network Error. Returning to the main screen."
NETWORK_ERROR_NOTIFICATION_2.text_threshold = 120

MAIN_MENU_DIMENSION_CHEST = UIElement(name='MAIN_MENU_DIMENSION_CHEST')
MAIN_MENU_DIMENSION_CHEST.description = "Main menu: Store: Dimension Chest button."
MAIN_MENU_DIMENSION_CHEST.text_rect = Rect(0.44228507450668303, 0.6064373308060554, 0.540805524468089, 0.6368380668897042)
MAIN_MENU_DIMENSION_CHEST.button_rect = Rect(0.47394842180670943, 0.519157798178805, 0.5111280317025593, 0.5917272972171931)
MAIN_MENU_DIMENSION_CHEST.text = "DIMENSION CHEST"
MAIN_MENU_DIMENSION_CHEST.text_threshold = 120

MAIN_MENU_SUPPORT_SHOP = UIElement(name='MAIN_MENU_SUPPORT_SHOP')
MAIN_MENU_SUPPORT_SHOP.description = "Main menu: Store: Support Shop button."
MAIN_MENU_SUPPORT_SHOP.text_rect = Rect(0.4497058193093056, 0.7425602179891547, 0.5336722813084339, 0.7724573673373294)
MAIN_MENU_SUPPORT_SHOP.button_rect = Rect(0.47332138674656044, 0.6596539385910256, 0.5144697239478379, 0.7264454424539685)
MAIN_MENU_SUPPORT_SHOP.text = "SUPPORT SHOP"
MAIN_MENU_SUPPORT_SHOP.text_threshold = 120

DOWNLOAD_UPDATE = UIElement(name="DOWNLOAD_UPDATE")
DOWNLOAD_UPDATE.description = "Download update notification while starting the game."
DOWNLOAD_UPDATE.text_rect = Rect(0.8369599371862357, 0.8911612776889132, 0.9521083506969829, 0.9483200861271485)
DOWNLOAD_UPDATE.button_rect = Rect(0.8369599371862357, 0.8911612776889132, 0.9521083506969829, 0.9483200861271485)
DOWNLOAD_UPDATE.text = "DOWNLOAD"
DOWNLOAD_UPDATE.text_threshold = 120
