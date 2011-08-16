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

RPC_URL = "http://rpcuser:localaccessonly@127.0.0.1:8332"

class Controller:
    def __init__(self):
        self.bitcoind = AuthServiceProxy(RPC_URL)
        self.current_address = ""

    def run(self):
        self.app = QtGui.QApplication([])
        self.app.connect(self.app, QtCore.SIGNAL('_new_transaction_received(PyQt_PyObject)'),
                self._new_transaction_received)

        self.merchant_gui = MerchantGUI(self)
        self.merchant_gui.show()
        self.customer_display = CustomerDisplay('data/customer_display.html')
        self.customer_display.show()
        self.app.exec_()

    def init_new_transaction(self, amount):
        self.current_address = self.bitcoind.getnewaddress("Point of Sale")
        self.merchant_gui.update_status("Looking for a transaction to %s..." %
                self.current_address)

        amount_str = self.format_btc_amount(amount)
        imgdata = self.create_img_data(self.current_address, amount_str)
        js = 'show_payment_info("%s", "%s", "%s", "%s")' % \
                ('%s BTC' % amount_str, '...',
                        self.current_address, imgdata)

        self.customer_display.evaluate_java_script(js)

    def create_img_data(self, address, amount_str):
        (_, size, img) = qrencode.encode("bitcoin:%s?amount=%s&label=" %
                (address, amount_str))
        if size < 300: img = img.resize((300, 300), Image.NEAREST)

        buf = StringIO()
        img.save(buf, format='PNG')
        imgdata = "data:image/png,%s" % urllib.quote(buf.getvalue())
        return imgdata

    def format_btc_amount(self, amount):
        s = "%.8f" % amount
        return re.sub("\.?0+$", "", s)

    # this is thread-safe, as long as it is called from a QThread
    def new_transaction_received(self, txid, output_addresses, from_instawallet):
        # emit signal, so we can process this on the Qt GUI thread
        self.app.emit(QtCore.SIGNAL('_new_transaction_received(PyQt_PyObject)'),
                (txid, output_addresses, from_instawallet))

    def _new_transaction_received(self, data):
        (_, output_addresses, from_instawallet) = data
        if self.current_address != "" and self.current_address in output_addresses:
            msg = "Transaction to %s received." % self.current_address
            if from_instawallet: msg += " Verified by Instawallet."

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
