# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'queue_editor_window.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(600, 400)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.select_mode_tool_button = QtWidgets.QToolButton(Dialog)
        self.select_mode_tool_button.setMinimumSize(QtCore.QSize(100, 40))
        self.select_mode_tool_button.setObjectName("select_mode_tool_button")
        self.horizontalLayout_2.addWidget(self.select_mode_tool_button)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout.addLayout(self.gridLayout)
        self.editor_button_box = QtWidgets.QDialogButtonBox(Dialog)
        self.editor_button_box.setOrientation(QtCore.Qt.Horizontal)
        self.editor_button_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.editor_button_box.setObjectName("editor_button_box")
        self.verticalLayout.addWidget(self.editor_button_box)

        self.retranslateUi(Dialog)
        self.editor_button_box.accepted.connect(Dialog.accept)
        self.editor_button_box.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Add mission to queue"))
        self.select_mode_tool_button.setText(_translate("Dialog", "Select Mode"))
