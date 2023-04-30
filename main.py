from PyQt5.QtWidgets import QApplication
from sys import argv, exit
from window import MainWindow

if __name__ == '__main__':
    app = QApplication(argv)
    main_window = MainWindow()
    main_window.show()
    exit(app.exec())
