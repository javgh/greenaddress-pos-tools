from PyQt4 import QtGui
from PyQt4 import QtCore

class MerchantGUI(QtGui.QWidget):
    def __init__(self, controller, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.controller = controller
        self.init_ui()

    def init_ui(self):
        self.status = QtGui.QLabel()
        self.status.setText("Welcome")

        amount = QtGui.QLabel()
        amount.setText("Amount")
        self.edit = QtGui.QLineEdit()
        validator = QtGui.QDoubleValidator(self.edit)
        self.edit.setValidator(validator)

        combo = QtGui.QComboBox()
        combo.addItem("BTC")
        combo.addItem("USD")

        show = QtGui.QPushButton("Show")
        self.connect(show, QtCore.SIGNAL('clicked()'), self.on_clicked)

        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(amount)
        hbox.addWidget(self.edit)
        hbox.addWidget(combo)
        hbox.addWidget(show)

        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.status)

        self.setLayout(vbox)
        self.setWindowTitle('Point of Sale System - Backend')

    def on_clicked(self):
        if self.edit.text() == "":
            amount = 0
        else:
            amount = float(self.edit.text())
        self.controller.init_new_transaction(amount)

    def update_status(self, message):
        self.status.setText(message)

    def closeEvent(self, event):
        event.accept()
        QtGui.QApplication.exit()
