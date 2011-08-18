import qrencode
import urllib
import re
from StringIO import StringIO
from PIL import Image
from PyQt4 import QtGui
from PyQt4 import QtCore
from authproxy import AuthServiceProxy, JSONRPCException
from merchantgui import MerchantGUI
from customerdisplay import CustomerDisplay

class Controller:
    def __init__(self, settings):
        self.bitcoind = AuthServiceProxy(settings['rpc_url'])
        self.current_address = ""
        self.exchange_rate = 0.0
        self.exchange_rate_source = ""

    def run(self):
        self.app = QtGui.QApplication([])

        font = self.app.font()
        font.setPointSize(12)
        self.app.setFont(font)

        self.app.connect(self.app, QtCore.SIGNAL('_new_transaction_received(PyQt_PyObject)'),
                self._new_transaction_received)
        self.app.connect(self.app, QtCore.SIGNAL('_exchange_rate_updated(PyQt_PyObject)'),
                self._exchange_rate_updated)

        self.merchant_gui = MerchantGUI(self)
        self.merchant_gui.show()
        self.customer_display = CustomerDisplay('data/customer_display.html')
        self.customer_display.show()
        self.app.exec_()

    def init_new_transaction(self, amount, currency):
        if currency == "USD":
            usd_amount = amount
            if self.exchange_rate != 0:
                amount = round(usd_amount / self.exchange_rate, 8)
            else:
                amount = 0

            conversion = '["%.2f USD", "%.4f USD", "%s"]' % (usd_amount,
                            self.exchange_rate, self.exchange_rate_source)
        else:
            conversion = '-1'

        self.current_address = self.bitcoind.getnewaddress("Point of Sale")
        self.merchant_gui.update_status("Looking for a transaction to %s..." %
                self.current_address)

        amount_str = self.format_btc_amount(amount)
        imgdata = self.create_img_data(self.current_address, amount_str)
        js = 'show_payment_info("%s", %s, "%s", "%s")' % \
                ('%s BTC' % amount_str, conversion,
                        self.current_address, imgdata)

        self.customer_display.evaluate_java_script(js)

    def create_img_data(self, address, amount_str):
        (_, size, img) = qrencode.encode("bitcoin:%s?amount=%s&label=" %
                (address, amount_str))
        if size < 400: img = img.resize((400, 400), Image.NEAREST)

        buf = StringIO()
        img.save(buf, format='PNG')
        imgdata = "data:image/png,%s" % urllib.quote(buf.getvalue())
        return imgdata

    def format_btc_amount(self, amount):
        s = "%.8f" % amount
        return re.sub("\.?0+$", "", s)

    # this is thread-safe, as long as it is called from a QThread
    def new_transaction_received(self, txid, output_addresses,
            from_green_address, green_address_msg):
        # emit signal, so we can process this on the Qt GUI thread
        self.app.emit(QtCore.SIGNAL('_new_transaction_received(PyQt_PyObject)'),
                (txid, output_addresses, from_green_address, green_address_msg))

    def _new_transaction_received(self, data):
        (_, output_addresses, from_green_address, green_address_msg) = data
        if self.current_address != "" and self.current_address in output_addresses:
            msg = "Transaction to %s received." % self.current_address
            if from_green_address: msg += " " + green_address_msg

            self.merchant_gui.update_status(msg)
            self.customer_display.evaluate_java_script('show_payment_received()')
            self.current_address = ""

    def toggle_fullscreen_mode(self):
        if not self.customer_display.isFullScreen():
            self.customer_display.showFullScreen()
        else:
            self.customer_display.showNormal()

    def clear_customer_display(self):
        self.customer_display.evaluate_java_script('show_idle()')

    # this is thread-safe, as long as it is called from a QThread
    def exchange_rate_updated(self, rate, source):
        self.app.emit(QtCore.SIGNAL('_exchange_rate_updated(PyQt_PyObject)'),
                (rate, source))

    def _exchange_rate_updated(self, data):
        (self.exchange_rate, self.exchange_rate_source) = data
        self.merchant_gui.update_exchange_rate(self.exchange_rate)
