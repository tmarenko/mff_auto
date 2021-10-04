﻿from lib.game.ui.general import UIElement, Rect, load_ui_image

DISPATCH_MISSION = UIElement(name='DISPATCH_MISSION')
DISPATCH_MISSION.description = "Dispatch Mission label in mission selection."
DISPATCH_MISSION.text_rect = Rect(0.5161893566920114, 0.26906075794253886, 0.6762007884536989, 0.3288781156104595)
DISPATCH_MISSION.button_rect = Rect(0.5460980355259717, 0.36742707944089725, 0.7262978255005824, 0.6837944377734552)
DISPATCH_MISSION.text = "DISPATCH MISSION"
DISPATCH_MISSION.text_threshold = 150

DISPATCH_MISSION_LABEL = UIElement(name='DISPATCH_MISSION_LABEL')
DISPATCH_MISSION_LABEL.description = "Dispatch Mission label inside mission."
DISPATCH_MISSION_LABEL.text_rect = Rect(0.04886624991138173, 0.012510757277901676, 0.2141117004690124, 0.07764521340519293)
DISPATCH_MISSION_LABEL.text = "DISPATCH MISSION"
DISPATCH_MISSION_LABEL.text_threshold = 150

DISPATCH_SECTOR_BUTTON = UIElement(name='DISPATCH_SECTOR_BUTTON')
DISPATCH_SECTOR_BUTTON.description = "Dispatch Mission: Dispatch button inside sector menu."
DISPATCH_SECTOR_BUTTON.text_rect = Rect(0.8638777481367997, 0.22918251949725849, 0.9506129167552847, 0.2757071310167523)
DISPATCH_SECTOR_BUTTON.button_rect = Rect(0.8638777481367997, 0.22918251949725849, 0.9506129167552847, 0.2757071310167523)
DISPATCH_SECTOR_BUTTON.text = "DISPATCH"
DISPATCH_SECTOR_BUTTON.text_threshold = 150

DISPATCH_SECTOR_CLOSE = UIElement(name='DISPATCH_SECTOR_CLOSE')
DISPATCH_SECTOR_CLOSE.description = "Dispatch Mission: Close (X) button inside sector menu."
DISPATCH_SECTOR_CLOSE.button_rect = Rect(0.9668258784516061, 0.13789178599912807, 0.97855315455397, 0.15916965080117987)

DISPATCH_DRAG_RIGHT_POSITION = UIElement(name='DISPATCH_DRAG_RIGHT_POSITION')
DISPATCH_DRAG_RIGHT_POSITION.description = "Dispatch Mission: position for dragging from the right."
DISPATCH_DRAG_RIGHT_POSITION.button_rect = Rect(0.9588378034346238, 0.10821852954657461, 0.9790261616475469, 0.13613329645827077)

DISPATCH_DRAG_LEFT_POSITION = UIElement(name='DISPATCH_DRAG_LEFT_POSITION')
DISPATCH_DRAG_LEFT_POSITION.description = "Dispatch Mission: position for dragging from the left."
DISPATCH_DRAG_LEFT_POSITION.button_rect = Rect(0.009237250456384327, 0.10954780416141716, 0.02867789169845854, 0.1454382187621697)

DISPATCH_ACQUIRE_SECTOR_1 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_1')
DISPATCH_ACQUIRE_SECTOR_1.description = "Dispatch Mission: Acquire button in Sector 1."
DISPATCH_ACQUIRE_SECTOR_1.text_rect = Rect(0.07727949480364403, 0.5202936601478054, 0.1453217391509037, 0.5548548001337152)
DISPATCH_ACQUIRE_SECTOR_1.button_rect = Rect(0.07727949480364403, 0.5202936601478054, 0.1453217391509037, 0.5548548001337152)
DISPATCH_ACQUIRE_SECTOR_1.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_1.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_2 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_2')
DISPATCH_ACQUIRE_SECTOR_2.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 2."
DISPATCH_ACQUIRE_SECTOR_2.text_rect = Rect(0.2559838508365568, 0.8153926246428804, 0.32253066124211843, 0.8526123138584755)
DISPATCH_ACQUIRE_SECTOR_2.button_rect = Rect(0.2559838508365568, 0.8153926246428804, 0.32253066124211843, 0.8526123138584755)
DISPATCH_ACQUIRE_SECTOR_2.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_2.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_3 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_3')
DISPATCH_ACQUIRE_SECTOR_3.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 3."
DISPATCH_ACQUIRE_SECTOR_3.text_rect = Rect(0.4331927729277716, 0.4578177532501994, 0.49824414939163525, 0.4950374424657945)
DISPATCH_ACQUIRE_SECTOR_3.button_rect = Rect(0.4331927729277716, 0.4578177532501994, 0.49824414939163525, 0.4950374424657945)
DISPATCH_ACQUIRE_SECTOR_3.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_3.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_4 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_4')
DISPATCH_ACQUIRE_SECTOR_4.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 4."
DISPATCH_ACQUIRE_SECTOR_4.text_rect = Rect(0.6118971289606845, 0.8140633500280379, 0.678443939366246, 0.8526123138584755)
DISPATCH_ACQUIRE_SECTOR_4.button_rect = Rect(0.6118971289606845, 0.8140633500280379, 0.678443939366246, 0.8526123138584755)
DISPATCH_ACQUIRE_SECTOR_4.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_4.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_5 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_5')
DISPATCH_ACQUIRE_SECTOR_5.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 5."
DISPATCH_ACQUIRE_SECTOR_5.text_rect = Rect(0.7868629001393522, 0.509659463229064, 0.8519142766032158, 0.5468791524446591)
DISPATCH_ACQUIRE_SECTOR_5.button_rect = Rect(0.7868629001393522, 0.509659463229064, 0.8519142766032158, 0.5468791524446591)
DISPATCH_ACQUIRE_SECTOR_5.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_5.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_6 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_6')
DISPATCH_ACQUIRE_SECTOR_6.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 6."
DISPATCH_ACQUIRE_SECTOR_6.text_rect = Rect(0.9663149731431138, 0.7768436608124428, 0.9962236519770741, 0.8114048007983525)
DISPATCH_ACQUIRE_SECTOR_6.button_rect = Rect(0.9663149731431138, 0.7768436608124428, 0.9962236519770741, 0.8114048007983525)
DISPATCH_ACQUIRE_SECTOR_6.text = "ACQ"
DISPATCH_ACQUIRE_SECTOR_6.text_threshold = 130
DISPATCH_ACQUIRE_SECTOR_6.available_characters = "ACQ"

DISPATCH_ACQUIRE_SECTOR_7 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_7')
DISPATCH_ACQUIRE_SECTOR_7.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 7."
DISPATCH_ACQUIRE_SECTOR_7.text_rect = Rect(0.03177083333333333, 0.45092592592592595, 0.0984375, 0.48703703703703705)
DISPATCH_ACQUIRE_SECTOR_7.button_rect = Rect(0.03177083333333333, 0.45092592592592595, 0.0984375, 0.48703703703703705)
DISPATCH_ACQUIRE_SECTOR_7.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_7.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_8 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_8')
DISPATCH_ACQUIRE_SECTOR_8.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 8."
DISPATCH_ACQUIRE_SECTOR_8.text_rect = Rect(0.20833333333333334, 0.7481481481481481, 0.2765625, 0.7842592592592592)
DISPATCH_ACQUIRE_SECTOR_8.button_rect = Rect(0.20833333333333334, 0.7481481481481481, 0.2765625, 0.7842592592592592)
DISPATCH_ACQUIRE_SECTOR_8.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_8.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_9 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_9')
DISPATCH_ACQUIRE_SECTOR_9.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 9."
DISPATCH_ACQUIRE_SECTOR_9.text_rect = Rect(0.38333333333333336, 0.48333333333333334, 0.45364583333333336, 0.5259259259259259)
DISPATCH_ACQUIRE_SECTOR_9.button_rect = Rect(0.38333333333333336, 0.48333333333333334, 0.45364583333333336, 0.5259259259259259)
DISPATCH_ACQUIRE_SECTOR_9.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_9.text_threshold = 130

DISPATCH_ACQUIRE_SECTOR_10 = UIElement(name='DISPATCH_ACQUIRE_SECTOR_10')
DISPATCH_ACQUIRE_SECTOR_10.description = "DEPRECATED: Dispatch Mission: Acquire button in Sector 10."
DISPATCH_ACQUIRE_SECTOR_10.text_rect = Rect(0.5625, 0.7314814814814815, 0.6296875, 0.7722222222222223)
DISPATCH_ACQUIRE_SECTOR_10.button_rect = Rect(0.5625, 0.7314814814814815, 0.6296875, 0.7722222222222223)
DISPATCH_ACQUIRE_SECTOR_10.text = "ACQUIRE"
DISPATCH_ACQUIRE_SECTOR_10.text_threshold = 130

DISPATCH_ACQUIRE_OK_BUTTON = UIElement(name='DISPATCH_ACQUIRE_OK_BUTTON')
DISPATCH_ACQUIRE_OK_BUTTON.description = "Dispatch Mission: OK button after acquiring rewards in sector."
DISPATCH_ACQUIRE_OK_BUTTON.text_rect = Rect(0.47805579117871205, 0.742282520826533, 0.5251619603421994, 0.8060877023389817)
DISPATCH_ACQUIRE_OK_BUTTON.button_rect = Rect(0.47805579117871205, 0.742282520826533, 0.5251619603421994, 0.8060877023389817)
DISPATCH_ACQUIRE_OK_BUTTON.text = "OK"
DISPATCH_ACQUIRE_OK_BUTTON.text_threshold = 150
DISPATCH_ACQUIRE_OK_BUTTON.available_characters = "OK"

DISPATCH_NEXT_REWARD = UIElement(name='DISPATCH_NEXT_REWARD')
DISPATCH_NEXT_REWARD.description = "Dispatch Mission: next reward button while acquiring rewards."
DISPATCH_NEXT_REWARD.text_rect = Rect(0.5139462057794643, 0.7436117954413758, 0.6477875435614368, 0.8047584277241392)
DISPATCH_NEXT_REWARD.button_rect = Rect(0.5139462057794643, 0.7436117954413758, 0.6477875435614368, 0.8047584277241392)
DISPATCH_NEXT_REWARD.text = "NEXT REWARD"
DISPATCH_NEXT_REWARD.text_threshold = 120