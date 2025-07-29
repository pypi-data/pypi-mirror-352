import sys
from PyQt6.QtWidgets import QApplication
from gui import LoginWindow


def main():
    from gui import LoginWindow
    from PyQt6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()