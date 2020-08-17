# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setup_player.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(651, 472)
        self.players_list_widget = QtWidgets.QListWidget(Dialog)
        self.players_list_widget.setGeometry(QtCore.QRect(10, 80, 631, 354))
        self.players_list_widget.setIconSize(QtCore.QSize(256, 256))
        self.players_list_widget.setMovement(QtWidgets.QListView.Static)
        self.players_list_widget.setFlow(QtWidgets.QListView.LeftToRight)
        self.players_list_widget.setResizeMode(QtWidgets.QListView.Adjust)
        self.players_list_widget.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.players_list_widget.setGridSize(QtCore.QSize(300, 169))
        self.players_list_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.players_list_widget.setModelColumn(0)
        self.players_list_widget.setUniformItemSizes(False)
        self.players_list_widget.setSelectionRectVisible(True)
        self.players_list_widget.setObjectName("players_list_widget")
        self.verticalLayoutWidget = QtWidgets.QWidget(Dialog)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 693, 61))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.select_player_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.select_player_label.setFont(font)
        self.select_player_label.setObjectName("select_player_label")
        self.verticalLayout.addWidget(self.select_player_label)
        self.selected_player_info_label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.selected_player_info_label.setFont(font)
        self.selected_player_info_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.selected_player_info_label.setObjectName("selected_player_info_label")
        self.verticalLayout.addWidget(self.selected_player_info_label)
        self.next_button = QtWidgets.QPushButton(Dialog)
        self.next_button.setEnabled(False)
        self.next_button.setGeometry(QtCore.QRect(550, 440, 91, 31))
        self.next_button.setCheckable(False)
        self.next_button.setObjectName("next_button")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Setup"))
        self.select_player_label.setText(_translate("Dialog", "Run NoxPlayer with MFF installed and select player\'s window from the list below"))
        self.selected_player_info_label.setText(_translate("Dialog", "Selected:"))
        self.next_button.setText(_translate("Dialog", "Next"))
