from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4.QtWebKit import QWebView

class CustomerDisplay(QWebView):
    def __init__(self, page, single_screen_mode, parent=None):
        QWebView.__init__(self, parent)
        self.setWindowTitle('Point of Sale System - Frontend')
        self.load(QtCore.QUrl(page))
        self.single_screen_mode = single_screen_mode

    def evaluate_java_script(self, js):
        self.page().mainFrame().evaluateJavaScript(js)

    def closeEvent(self, event):
        event.accept()
        QtGui.QApplication.exit()

    def keyPressEvent(self, event):
        if self.single_screen_mode:
            self.hide()
