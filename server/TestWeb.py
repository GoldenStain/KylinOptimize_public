from PyQt5.QtCore import QSize
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIcon


class WebWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setUI()

    def setUI(self):
        self.setWindowTitle('麒麟调优')
        self.setGeometry(100, 100, 1050, 600)
        # 添加Icon
        icon = QIcon()
        icon.addFile(u"static/images/Ubuntu_Kylin_logo.ico", QSize(), QIcon.Normal, QIcon.Off)
        self.setWindowIcon(icon)
        # 创建Web视图
        self.webView = QWebEngineView()
        self.setCentralWidget(self.webView)

        # 加载网页
        self.webView.setUrl('http://127.0.0.1:5000')

