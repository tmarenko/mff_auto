# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setup_emulator.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(651, 472)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.select_emulator_label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.select_emulator_label.setFont(font)
        self.select_emulator_label.setObjectName("select_emulator_label")
        self.verticalLayout.addWidget(self.select_emulator_label)
        self.selected_emulator_info_label = QtWidgets.QLabel(Dialog)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(False)
        font.setWeight(50)
        self.selected_emulator_info_label.setFont(font)
        self.selected_emulator_info_label.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.selected_emulator_info_label.setObjectName("selected_emulator_info_label")
        self.verticalLayout.addWidget(self.selected_emulator_info_label)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.emulators_list_widget = QtWidgets.QListWidget(Dialog)
        self.emulators_list_widget.setIconSize(QtCore.QSize(256, 256))
        self.emulators_list_widget.setMovement(QtWidgets.QListView.Static)
        self.emulators_list_widget.setFlow(QtWidgets.QListView.LeftToRight)
        self.emulators_list_widget.setResizeMode(QtWidgets.QListView.Adjust)
        self.emulators_list_widget.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.emulators_list_widget.setGridSize(QtCore.QSize(300, 169))
        self.emulators_list_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.emulators_list_widget.setModelColumn(0)
        self.emulators_list_widget.setUniformItemSizes(False)
        self.emulators_list_widget.setSelectionRectVisible(True)
        self.emulators_list_widget.setObjectName("emulators_list_widget")
        self.verticalLayout_2.addWidget(self.emulators_list_widget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.next_button = QtWidgets.QPushButton(Dialog)
        self.next_button.setEnabled(False)
        self.next_button.setMinimumSize(QtCore.QSize(0, 40))
        self.next_button.setCheckable(False)
        self.next_button.setObjectName("next_button")
        self.horizontalLayout.addWidget(self.next_button)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Setup"))
        self.select_emulator_label.setText(_translate("Dialog", "Run Android Emulator with MFF installed and select emulator\'s window from the list below"))
        self.selected_emulator_info_label.setText(_translate("Dialog", "Selected:"))
        self.next_button.setText(_translate("Dialog", "Next"))
