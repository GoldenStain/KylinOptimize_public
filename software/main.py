from PySide6.QtWidgets import QApplication
from software.TestWeb import WebWindow

if __name__ == "__main__":

    app = QApplication()
    Gui = WebWindow()
    Gui.show()
    app.exec()