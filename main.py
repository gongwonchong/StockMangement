import sys
import bg
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    QApplication.setStyle(QStyleFactory.create("windowsvista"))
    ex = bg.MainWindow()
    sys.exit(app.exec_())