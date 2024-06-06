from PySide6.QtWidgets import QApplication
from TestWeb import WebWindow

if __name__ == "__main__":
    app = QApplication()
    pomodoroWindowGenerator = WebWindow()
    pomodoroWindowGenerator.show()
    app.exec()
