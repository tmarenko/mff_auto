# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1150, 630)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.info_group = QtWidgets.QGroupBox(self.centralwidget)
        self.info_group.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.info_group.setObjectName("info_group")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.info_group)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_username = QtWidgets.QLabel(self.info_group)
        self.label_username.setAlignment(QtCore.Qt.AlignCenter)
        self.label_username.setWordWrap(True)
        self.label_username.setObjectName("label_username")
        self.horizontalLayout.addWidget(self.label_username)
        self.label_energy = QtWidgets.QLabel(self.info_group)
        self.label_energy.setAlignment(QtCore.Qt.AlignCenter)
        self.label_energy.setWordWrap(True)
        self.label_energy.setObjectName("label_energy")
        self.horizontalLayout.addWidget(self.label_energy)
        self.label_gold = QtWidgets.QLabel(self.info_group)
        self.label_gold.setAlignment(QtCore.Qt.AlignCenter)
        self.label_gold.setWordWrap(True)
        self.label_gold.setObjectName("label_gold")
        self.horizontalLayout.addWidget(self.label_gold)
        self.label_boosts = QtWidgets.QLabel(self.info_group)
        self.label_boosts.setAlignment(QtCore.Qt.AlignCenter)
        self.label_boosts.setWordWrap(True)
        self.label_boosts.setObjectName("label_boosts")
        self.horizontalLayout.addWidget(self.label_boosts)
        self.horizontalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_3.addWidget(self.info_group)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 5, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.autoplay_button = QtWidgets.QPushButton(self.centralwidget)
        self.autoplay_button.setMinimumSize(QtCore.QSize(120, 50))
        self.autoplay_button.setObjectName("autoplay_button")
        self.horizontalLayout_2.addWidget(self.autoplay_button)
        self.restart_game_button = QtWidgets.QPushButton(self.centralwidget)
        self.restart_game_button.setMinimumSize(QtCore.QSize(120, 50))
        self.restart_game_button.setObjectName("restart_game_button")
        self.horizontalLayout_2.addWidget(self.restart_game_button)
        self.horizontalLayout_3.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3.setStretch(0, 1)
        self.verticalLayout_6.addLayout(self.horizontalLayout_3)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.mission_queue_group = QtWidgets.QGroupBox(self.centralwidget)
        self.mission_queue_group.setObjectName("mission_queue_group")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.mission_queue_group)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_6 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.queue_button_1 = QtWidgets.QPushButton(self.mission_queue_group)
        self.queue_button_1.setCheckable(True)
        self.queue_button_1.setChecked(False)
        self.queue_button_1.setDefault(False)
        self.queue_button_1.setObjectName("queue_button_1")
        self.horizontalLayout_6.addWidget(self.queue_button_1)
        self.queue_button_2 = QtWidgets.QPushButton(self.mission_queue_group)
        self.queue_button_2.setCheckable(True)
        self.queue_button_2.setDefault(False)
        self.queue_button_2.setObjectName("queue_button_2")
        self.horizontalLayout_6.addWidget(self.queue_button_2)
        self.queue_button_3 = QtWidgets.QPushButton(self.mission_queue_group)
        self.queue_button_3.setCheckable(True)
        self.queue_button_3.setDefault(False)
        self.queue_button_3.setObjectName("queue_button_3")
        self.horizontalLayout_6.addWidget(self.queue_button_3)
        self.queue_button_4 = QtWidgets.QPushButton(self.mission_queue_group)
        self.queue_button_4.setCheckable(True)
        self.queue_button_4.setAutoDefault(False)
        self.queue_button_4.setDefault(False)
        self.queue_button_4.setFlat(False)
        self.queue_button_4.setObjectName("queue_button_4")
        self.horizontalLayout_6.addWidget(self.queue_button_4)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_6.addItem(spacerItem)
        self.verticalLayout_5.addLayout(self.horizontalLayout_6)
        self.queue_list_widget = QtWidgets.QListWidget(self.mission_queue_group)
        self.queue_list_widget.setLineWidth(-1)
        self.queue_list_widget.setMidLineWidth(0)
        self.queue_list_widget.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.queue_list_widget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.queue_list_widget.setProperty("isWrapping", True)
        self.queue_list_widget.setResizeMode(QtWidgets.QListView.Adjust)
        self.queue_list_widget.setWordWrap(False)
        self.queue_list_widget.setObjectName("queue_list_widget")
        self.verticalLayout_5.addWidget(self.queue_list_widget)
        self.horizontalLayout_5.addWidget(self.mission_queue_group)
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.mission_controls_group = QtWidgets.QGroupBox(self.centralwidget)
        self.mission_controls_group.setObjectName("mission_controls_group")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.mission_controls_group)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.add_queue_button = QtWidgets.QPushButton(self.mission_controls_group)
        self.add_queue_button.setMinimumSize(QtCore.QSize(120, 50))
        self.add_queue_button.setObjectName("add_queue_button")
        self.verticalLayout_2.addWidget(self.add_queue_button)
        self.edit_queue_button = QtWidgets.QPushButton(self.mission_controls_group)
        self.edit_queue_button.setMinimumSize(QtCore.QSize(120, 50))
        self.edit_queue_button.setObjectName("edit_queue_button")
        self.verticalLayout_2.addWidget(self.edit_queue_button)
        self.remove_queue_button = QtWidgets.QPushButton(self.mission_controls_group)
        self.remove_queue_button.setMinimumSize(QtCore.QSize(120, 50))
        self.remove_queue_button.setObjectName("remove_queue_button")
        self.verticalLayout_2.addWidget(self.remove_queue_button)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.run_queue_button = QtWidgets.QPushButton(self.mission_controls_group)
        self.run_queue_button.setMinimumSize(QtCore.QSize(120, 50))
        self.run_queue_button.setObjectName("run_queue_button")
        self.verticalLayout_2.addWidget(self.run_queue_button)
        self.verticalLayout_4.addWidget(self.mission_controls_group)
        self.settings_group = QtWidgets.QGroupBox(self.centralwidget)
        self.settings_group.setObjectName("settings_group")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.settings_group)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.formLayout.setFormAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.formLayout.setObjectName("formLayout")
        self.acquire_heroic_quest_rewards_label = QtWidgets.QLabel(self.settings_group)
        self.acquire_heroic_quest_rewards_label.setObjectName("acquire_heroic_quest_rewards_label")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.acquire_heroic_quest_rewards_label)
        self.acquire_heroic_quest_rewards_checkbox = QtWidgets.QCheckBox(self.settings_group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.acquire_heroic_quest_rewards_checkbox.sizePolicy().hasHeightForWidth())
        self.acquire_heroic_quest_rewards_checkbox.setSizePolicy(sizePolicy)
        self.acquire_heroic_quest_rewards_checkbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.acquire_heroic_quest_rewards_checkbox.setText("")
        self.acquire_heroic_quest_rewards_checkbox.setChecked(True)
        self.acquire_heroic_quest_rewards_checkbox.setObjectName("acquire_heroic_quest_rewards_checkbox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.acquire_heroic_quest_rewards_checkbox)
        self.mission_team_label = QtWidgets.QLabel(self.settings_group)
        self.mission_team_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.mission_team_label.setAutoFillBackground(False)
        self.mission_team_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.mission_team_label.setObjectName("mission_team_label")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.mission_team_label)
        self.mission_team_spin_box = QtWidgets.QSpinBox(self.settings_group)
        self.mission_team_spin_box.setMinimum(1)
        self.mission_team_spin_box.setMaximum(5)
        self.mission_team_spin_box.setObjectName("mission_team_spin_box")
        self.formLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.mission_team_spin_box)
        self.timeline_team_label = QtWidgets.QLabel(self.settings_group)
        self.timeline_team_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.timeline_team_label.setObjectName("timeline_team_label")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.LabelRole, self.timeline_team_label)
        self.timeline_team_spin_box = QtWidgets.QSpinBox(self.settings_group)
        self.timeline_team_spin_box.setMinimum(1)
        self.timeline_team_spin_box.setMaximum(5)
        self.timeline_team_spin_box.setObjectName("timeline_team_spin_box")
        self.formLayout.setWidget(7, QtWidgets.QFormLayout.FieldRole, self.timeline_team_spin_box)
        self.handle_network_errors_label = QtWidgets.QLabel(self.settings_group)
        self.handle_network_errors_label.setObjectName("handle_network_errors_label")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.LabelRole, self.handle_network_errors_label)
        self.handle_network_errors_checkbox = QtWidgets.QCheckBox(self.settings_group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.handle_network_errors_checkbox.sizePolicy().hasHeightForWidth())
        self.handle_network_errors_checkbox.setSizePolicy(sizePolicy)
        self.handle_network_errors_checkbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.handle_network_errors_checkbox.setText("")
        self.handle_network_errors_checkbox.setChecked(False)
        self.handle_network_errors_checkbox.setObjectName("handle_network_errors_checkbox")
        self.formLayout.setWidget(9, QtWidgets.QFormLayout.FieldRole, self.handle_network_errors_checkbox)
        self.verticalLayout_7.addLayout(self.formLayout)
        self.verticalLayout_4.addWidget(self.settings_group)
        self.verticalLayout_4.setStretch(1, 1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_4)
        self.quick_start_group = QtWidgets.QGroupBox(self.centralwidget)
        self.quick_start_group.setObjectName("quick_start_group")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.quick_start_group)
        self.verticalLayout.setObjectName("verticalLayout")
        self.daily_trivia_button = QtWidgets.QPushButton(self.quick_start_group)
        self.daily_trivia_button.setMinimumSize(QtCore.QSize(120, 50))
        self.daily_trivia_button.setObjectName("daily_trivia_button")
        self.verticalLayout.addWidget(self.daily_trivia_button)
        self.comic_cards_button = QtWidgets.QPushButton(self.quick_start_group)
        self.comic_cards_button.setMinimumSize(QtCore.QSize(120, 50))
        self.comic_cards_button.setObjectName("comic_cards_button")
        self.verticalLayout.addWidget(self.comic_cards_button)
        self.custom_gear_button = QtWidgets.QPushButton(self.quick_start_group)
        self.custom_gear_button.setMinimumSize(QtCore.QSize(120, 50))
        self.custom_gear_button.setObjectName("custom_gear_button")
        self.verticalLayout.addWidget(self.custom_gear_button)
        self.dispatch_mission_rewards = QtWidgets.QPushButton(self.quick_start_group)
        self.dispatch_mission_rewards.setMinimumSize(QtCore.QSize(120, 50))
        self.dispatch_mission_rewards.setObjectName("dispatch_mission_rewards")
        self.verticalLayout.addWidget(self.dispatch_mission_rewards)
        self.squad_battle_button = QtWidgets.QPushButton(self.quick_start_group)
        self.squad_battle_button.setMinimumSize(QtCore.QSize(120, 50))
        self.squad_battle_button.setObjectName("squad_battle_button")
        self.verticalLayout.addWidget(self.squad_battle_button)
        self.world_boss_invasion_button = QtWidgets.QPushButton(self.quick_start_group)
        self.world_boss_invasion_button.setMinimumSize(QtCore.QSize(120, 50))
        self.world_boss_invasion_button.setObjectName("world_boss_invasion_button")
        self.verticalLayout.addWidget(self.world_boss_invasion_button)
        self.danger_room_button = QtWidgets.QPushButton(self.quick_start_group)
        self.danger_room_button.setMinimumSize(QtCore.QSize(120, 50))
        self.danger_room_button.setObjectName("danger_room_button")
        self.verticalLayout.addWidget(self.danger_room_button)
        self.enhance_potential_button = QtWidgets.QPushButton(self.quick_start_group)
        self.enhance_potential_button.setMinimumSize(QtCore.QSize(120, 50))
        self.enhance_potential_button.setObjectName("enhance_potential_button")
        self.verticalLayout.addWidget(self.enhance_potential_button)
        self.shadowland_button = QtWidgets.QPushButton(self.quick_start_group)
        self.shadowland_button.setMinimumSize(QtCore.QSize(120, 50))
        self.shadowland_button.setObjectName("shadowland_button")
        self.verticalLayout.addWidget(self.shadowland_button)
        spacerItem2 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem2)
        self.horizontalLayout_5.addWidget(self.quick_start_group)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.game_screen_group = QtWidgets.QGroupBox(self.centralwidget)
        self.game_screen_group.setObjectName("game_screen_group")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.game_screen_group)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.screen_label = QtWidgets.QLabel(self.game_screen_group)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.screen_label.sizePolicy().hasHeightForWidth())
        self.screen_label.setSizePolicy(sizePolicy)
        self.screen_label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.screen_label.setAutoFillBackground(False)
        self.screen_label.setStyleSheet("background-color: rgb(15, 0, 50);\n"
"color: rgb(0, 0, 127);")
        self.screen_label.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.screen_label.setLineWidth(1)
        self.screen_label.setMidLineWidth(0)
        self.screen_label.setText("")
        self.screen_label.setAlignment(QtCore.Qt.AlignCenter)
        self.screen_label.setObjectName("screen_label")
        self.gridLayout_2.addWidget(self.screen_label, 0, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.game_screen_group)
        self.logs_group = QtWidgets.QGroupBox(self.centralwidget)
        self.logs_group.setObjectName("logs_group")
        self.gridLayout = QtWidgets.QGridLayout(self.logs_group)
        self.gridLayout.setObjectName("gridLayout")
        self.log_tab_widget = QtWidgets.QTabWidget(self.logs_group)
        self.log_tab_widget.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.log_tab_widget.setObjectName("log_tab_widget")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.tab_3)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.logger_text = QtWidgets.QPlainTextEdit(self.tab_3)
        self.logger_text.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.logger_text.setReadOnly(True)
        self.logger_text.setObjectName("logger_text")
        self.verticalLayout_8.addWidget(self.logger_text)
        self.log_tab_widget.addTab(self.tab_3, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.verticalLayout_9 = QtWidgets.QVBoxLayout(self.tab_5)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.logger_text_info = QtWidgets.QPlainTextEdit(self.tab_5)
        self.logger_text_info.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.logger_text_info.setReadOnly(True)
        self.logger_text_info.setObjectName("logger_text_info")
        self.verticalLayout_9.addWidget(self.logger_text_info)
        self.log_tab_widget.addTab(self.tab_5, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.verticalLayout_10 = QtWidgets.QVBoxLayout(self.tab_6)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.logger_text_error = QtWidgets.QPlainTextEdit(self.tab_6)
        self.logger_text_error.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.logger_text_error.setReadOnly(True)
        self.logger_text_error.setObjectName("logger_text_error")
        self.verticalLayout_10.addWidget(self.logger_text_error)
        self.log_tab_widget.addTab(self.tab_6, "")
        self.gridLayout.addWidget(self.log_tab_widget, 0, 0, 1, 1)
        self.verticalLayout_3.addWidget(self.logs_group)
        self.verticalLayout_3.setStretch(0, 1)
        self.horizontalLayout_5.addLayout(self.verticalLayout_3)
        self.horizontalLayout_5.setStretch(0, 7)
        self.horizontalLayout_5.setStretch(3, 10)
        self.verticalLayout_6.addLayout(self.horizontalLayout_5)
        self.verticalLayout_6.setStretch(1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1150, 21))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)

        self.retranslateUi(MainWindow)
        self.queue_list_widget.setCurrentRow(-1)
        self.log_tab_widget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MFF Auto"))
        self.info_group.setTitle(_translate("MainWindow", "Info"))
        self.label_username.setText(_translate("MainWindow", "Username"))
        self.label_energy.setText(_translate("MainWindow", "Energy:"))
        self.label_gold.setText(_translate("MainWindow", "Gold:"))
        self.label_boosts.setText(_translate("MainWindow", "Boost:"))
        self.autoplay_button.setToolTip(_translate("MainWindow", "Automatically determines in-game battles and start casting skills"))
        self.autoplay_button.setText(_translate("MainWindow", "Autoplay++"))
        self.restart_game_button.setText(_translate("MainWindow", "Restart Game"))
        self.mission_queue_group.setTitle(_translate("MainWindow", "Mission Queue"))
        self.queue_button_1.setText(_translate("MainWindow", "Queue #1"))
        self.queue_button_2.setText(_translate("MainWindow", "Queue #2"))
        self.queue_button_3.setText(_translate("MainWindow", "Queue #3"))
        self.queue_button_4.setText(_translate("MainWindow", "Queue #4"))
        self.queue_list_widget.setSortingEnabled(False)
        self.mission_controls_group.setTitle(_translate("MainWindow", "Mission Controls"))
        self.add_queue_button.setText(_translate("MainWindow", "Add"))
        self.edit_queue_button.setText(_translate("MainWindow", "Edit"))
        self.remove_queue_button.setText(_translate("MainWindow", "Remove"))
        self.run_queue_button.setText(_translate("MainWindow", "Run"))
        self.settings_group.setTitle(_translate("MainWindow", "Settings"))
        self.acquire_heroic_quest_rewards_label.setToolTip(_translate("MainWindow", "Should bot acquire Heroic Quest rewards when they\'re available"))
        self.acquire_heroic_quest_rewards_label.setText(_translate("MainWindow", "Acquire Heroic Quest rewards"))
        self.acquire_heroic_quest_rewards_checkbox.setToolTip(_translate("MainWindow", "Should bot acquire Heroic Quest rewards when they\'re available"))
        self.mission_team_label.setToolTip(_translate("MainWindow", "Your in-game team number for PvE modes"))
        self.mission_team_label.setText(_translate("MainWindow", "Mission Team:"))
        self.mission_team_spin_box.setToolTip(_translate("MainWindow", "Your in-game team number for PvE modes"))
        self.timeline_team_label.setToolTip(_translate("MainWindow", "Your in-game team number for PvP mode"))
        self.timeline_team_label.setText(_translate("MainWindow", "Timeline Team:"))
        self.timeline_team_spin_box.setToolTip(_translate("MainWindow", "Your in-game team number for PvP mode"))
        self.handle_network_errors_label.setToolTip(_translate("MainWindow", "Should bot restart current queue when network errors occurred"))
        self.handle_network_errors_label.setText(_translate("MainWindow", "Restart queue on network errors"))
        self.handle_network_errors_checkbox.setToolTip(_translate("MainWindow", "Should bot restart current queue when network errors occurred"))
        self.quick_start_group.setTitle(_translate("MainWindow", "Quick Start"))
        self.daily_trivia_button.setText(_translate("MainWindow", "Daily Trivia"))
        self.comic_cards_button.setText(_translate("MainWindow", "Comic Cards:\n"
"Upgrade All"))
        self.custom_gear_button.setText(_translate("MainWindow", "Custom Gear Upgrade"))
        self.dispatch_mission_rewards.setText(_translate("MainWindow", "Dispatch Mission:\n"
" Acquire All Rewards"))
        self.squad_battle_button.setText(_translate("MainWindow", "Squad Battle:\n"
" All Battles"))
        self.world_boss_invasion_button.setText(_translate("MainWindow", "World Boss Invasion:\n"
" All Battles"))
        self.danger_room_button.setText(_translate("MainWindow", "Danger Room:\n"
" 1 Battle"))
        self.enhance_potential_button.setText(_translate("MainWindow", "Enhance Potential\n"
"with 10% success rate"))
        self.shadowland_button.setText(_translate("MainWindow", "Shadowland:\n"
"Clear All Floors"))
        self.game_screen_group.setTitle(_translate("MainWindow", "Game Screen"))
        self.logs_group.setTitle(_translate("MainWindow", "Logs"))
        self.log_tab_widget.setTabText(self.log_tab_widget.indexOf(self.tab_3), _translate("MainWindow", "All"))
        self.log_tab_widget.setTabText(self.log_tab_widget.indexOf(self.tab_5), _translate("MainWindow", "Info"))
        self.log_tab_widget.setTabText(self.log_tab_widget.indexOf(self.tab_6), _translate("MainWindow", "Errors"))
