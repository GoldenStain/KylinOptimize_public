from PySide6.QtWidgets import QApplication
from server.window import WebWindow

def start():
    app = QApplication()
    pomodoroWindowGenerator = WebWindow()
    pomodoroWindowGenerator.show()
    app.exec()
