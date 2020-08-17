# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'setup_game.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(651, 472)
        self.screen_image_label = QtWidgets.QLabel(Dialog)
        self.screen_image_label.setGeometry(QtCore.QRect(10, 80, 631, 354))
        self.screen_image_label.setStyleSheet("background-color: rgb(254, 255, 176);\n"
"color: rgb(0, 0, 127);")
        self.screen_image_label.setText("")
        self.screen_image_label.setObjectName("screen_image_label")
        self.top_text_label = QtWidgets.QLabel(Dialog)
        self.top_text_label.setGeometry(QtCore.QRect(10, 10, 631, 61))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.top_text_label.setFont(font)
        self.top_text_label.setObjectName("top_text_label")
        self.no_button = QtWidgets.QPushButton(Dialog)
        self.no_button.setEnabled(False)
        self.no_button.setGeometry(QtCore.QRect(550, 440, 91, 31))
        self.no_button.setCheckable(False)
        self.no_button.setObjectName("no_button")
        self.yes_button = QtWidgets.QPushButton(Dialog)
        self.yes_button.setEnabled(False)
        self.yes_button.setGeometry(QtCore.QRect(440, 440, 91, 31))
        self.yes_button.setCheckable(False)
        self.yes_button.setObjectName("yes_button")
        self.question_label = QtWidgets.QLabel(Dialog)
        self.question_label.setGeometry(QtCore.QRect(10, 440, 421, 31))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.question_label.setFont(font)
        self.question_label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.question_label.setObjectName("question_label")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Setup"))
        self.top_text_label.setText(_translate("Dialog", "TODO"))
        self.no_button.setText(_translate("Dialog", "No"))
        self.yes_button.setText(_translate("Dialog", "Yes"))
        self.question_label.setText(_translate("Dialog", "Question?"))
