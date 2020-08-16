import sys
from PyQt5 import QtWidgets
from lib.gui.widgets.main import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
