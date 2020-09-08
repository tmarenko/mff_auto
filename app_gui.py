import os
import sys
from PyQt5 import QtWidgets
from lib.gui.widgets.main import MainWindow
from lib.updater import Updater


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


def check_updates():
    updater = Updater()
    if updater.check_updates():
        updater.update_from_new_version()
        os.execl(sys.executable, sys.executable, *sys.argv)


if __name__ == '__main__':
    check_updates()
    main()
