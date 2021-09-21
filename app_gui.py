import lib.logger as logging
import os
import sys
import traceback
from PyQt5 import QtWidgets, QtCore


def main():
    app_settings = QtCore.QSettings("tmarenko", "mff_auto")
    os.environ['MFF_LOW_MEMORY_MODE'] = str(app_settings.value("mff_low_memory_mode", defaultValue='false'))
    from lib.gui.widgets.main import MainWindow
    app = QtWidgets.QApplication(sys.argv)
    app.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    window = MainWindow(file_logger=file_logger, settings=app_settings)
    window.setWindowTitle(f"{window.windowTitle()} {current_version}")
    window.show()
    if is_new_updater:
        notification = create_updater_notification()
        notification.show()
    app.exec_()


def check_updates():
    from lib.updater import Updater
    updater = Updater()
    if updater.check_updates():
        updater.update_from_new_version()
        os.execl(sys.executable, sys.executable, *sys.argv)
    updater.clean()
    return updater.current_version.mff_auto, updater.is_new_updater


def create_updater_notification():
    from PyQt5.QtWidgets import QDialog
    from lib.gui.designes.updater_notification import Ui_Dialog
    from lib.gui.helper import set_default_icon
    notification = QDialog()
    Ui_Dialog().setupUi(Dialog=notification)
    set_default_icon(window=notification)
    return notification


def suppress_qt_warnings():
    from os import environ
    environ["QT_DEVICE_PIXEL_RATIO"] = "0"
    environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    environ["QT_SCREEN_SCALE_FACTORS"] = "1"
    environ["QT_SCALE_FACTOR"] = "1"


if __name__ == '__main__':
    suppress_qt_warnings()
    try:
        file_logger = logging.create_file_handler()
        current_version, is_new_updater = check_updates()
        main()
    except BaseException as err:
        logging.root.error(f"{err}\n{traceback.format_exc()}")
    finally:
        exit()
