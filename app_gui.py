﻿import lib.logger as logging
import os
import sys
import traceback
from PyQt5 import QtWidgets, QtCore


def main():
    from lib.gui.widgets.main import MainWindow
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = MainWindow(file_logger=file_logger)
    window.setWindowTitle(f"{window.windowTitle()} {current_version}")
    window.show()
    app.exec_()


def check_updates():
    from lib.updater import Updater
    updater = Updater()
    if updater.check_updates():
        updater.update_from_new_version()
        os.execl(sys.executable, sys.executable, *sys.argv)
    updater.clean()
    return updater.current_version


if __name__ == '__main__':
    try:
        file_logger = logging.create_file_handler()
        current_version = check_updates()
        main()
    except BaseException as err:
        logging.root.error(f"{err}\n{traceback.format_exc()}")
