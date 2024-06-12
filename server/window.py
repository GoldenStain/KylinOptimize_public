from PySide6.QtCore import QSize
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QMainWindow
from PySide6.QtGui import QIcon


class WebWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setUI()

    def setUI(self):
        self.setWindowTitle('麒麟调优')
        self.setGeometry(100, 100, 1050, 600)
       		# 添加Icon
        icon = QIcon()
        icon.addFile("./icon.jpeg", QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        	# 创建Web视图
        self.webView = QWebEngineView()
        self.setCentralWidget(self.webView)

        	# 加载网页
        self.webView.setUrl('http://127.0.0.1:5000')

