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
    def __init__(self, settings, nfc_broadcast):
        self.nfc_broadcast = nfc_broadcast
        self.bitcoind = AuthServiceProxy(settings['rpc_url'])
        self.current_address = ""
        self.exchange_rate = 0.0
        self.exchange_rate_source = ""
        self.currency = settings['exchange_rate_ticker']['currency']
        self.single_screen_mode = settings['single_screen_mode']
        self.green_addresses = settings['green_addresses']
        self.bt_addr = None

    def run(self):
        self.app = QtGui.QApplication([])

        font = self.app.font()
        font.setPointSize(12)
        self.app.setFont(font)

        self.app.connect(self.app, QtCore.SIGNAL('_new_transaction_received(PyQt_PyObject)'),
                self._new_transaction_received)
        self.app.connect(self.app, QtCore.SIGNAL('_exchange_rate_updated(PyQt_PyObject)'),
                self._exchange_rate_updated)

        self.merchant_gui = MerchantGUI(self, self.currency)
        self.merchant_gui.show()
        self.customer_display = CustomerDisplay('data/customer_display.html', self.single_screen_mode)
        if not self.single_screen_mode:
            self.customer_display.show()
        self.app.exec_()

    def init_new_transaction(self, amount, currency):
        if self.single_screen_mode:
            self.customer_display.show()
            if not self.customer_display.isFullScreen():
                self.customer_display.showFullScreen()
        if currency != "BTC":
            cur_amount = amount
            if self.exchange_rate != 0:
                amount = round(cur_amount / self.exchange_rate, 8)
            else:
                amount = 0

            conversion = '["%.2f %s", "%.4f %s", "%s"]' % (cur_amount, 
                            currency, self.exchange_rate, currency,
                            self.exchange_rate_source)
        else:
            conversion = '-1'

        self.current_address = self.bitcoind.getnewaddress("Point of Sale")
        self.merchant_gui.update_status("Looking for a transaction to %s..." %
                self.current_address)

        amount_str = self.format_btc_amount(amount)
        btc_uri = self.create_btc_uri(self.current_address, amount_str,
                                        self.bt_addr)
        imgdata = self.create_img_data(btc_uri)
        js = 'show_payment_info("%s", %s, "%s", "%s")' % \
                ('%s BTC' % amount_str, conversion,
                        self.current_address, imgdata)

        self.customer_display.evaluate_java_script(js)
        self.nfc_broadcast.set_btc_uri(btc_uri)

    def create_btc_uri(self, address, amount_str, bt_addr):
        btc_uri = "bitcoin:%s?amount=%s" % (address, amount_str)
        if bt_addr != None:
            bt_addr_stripped = bt_addr.translate(None, ':')
            btc_uri += "&bt=%s" % bt_addr_stripped
        return btc_uri

    def create_img_data(self, btc_uri):
        (_, size, img) = qrencode.encode(btc_uri)
        if size < 400: img = img.resize((400, 400), Image.NEAREST)

        buf = StringIO()
        img.save(buf, format='PNG')
        imgdata = "data:image/png,%s" % urllib.quote(buf.getvalue())
        return imgdata

    def format_btc_amount(self, amount):
        s = "%.8f" % amount
        return re.sub("\.?0+$", "", s)

    # this is thread-safe, as long as it is called from a QThread
    def new_transaction_received(self, txid):
        if not hasattr(self, 'app'): return  # not yet read
        # emit signal, so we can process this on the Qt GUI thread
        self.app.emit(QtCore.SIGNAL('_new_transaction_received(PyQt_PyObject)'),
                txid)

    def _new_transaction_received(self, txid):
        # check if we are waiting for a payment
        if self.current_address == "": return

        # check if the txid looks sane before passing it
        # to bitcoind (for security reasons; might be overly
        # paranoid, but can't hurt)
        if re.search("^[a-f0-9]*$", txid) == None: return

        tx_info = self.bitcoind.gettransaction(txid)
        output_addresses = []
        for detail in tx_info['details']:
            output_addresses.append(detail['address'])
        if self.current_address not in output_addresses: return

        msg = "Transaction to %s received." % self.current_address
        (from_green_address, green_address_msg) = self.green_address_check(txid)
        if from_green_address: msg += " " + green_address_msg

        self.merchant_gui.update_status(msg)
        self.customer_display.evaluate_java_script('show_payment_received()')
        self.current_address = ""

    def bluetooth_available(self, bt_addr):
        self.bt_addr = bt_addr

    def new_transaction_via_bluetooth(self, tx):
        try:
            self.bitcoind.sendrawtransaction(tx)
        except JSONRPCException:
            # ignore, if this did not work - we might
            # have already received the transaction in
            # a different way
            pass

    def green_address_check(self, txid):
        found = False
        msg = ""

        origins = self.get_origins(txid)
        for origin in origins:
            if origin in self.green_addresses:
                found = True
                msg = self.green_addresses[origin]
                break

        return (found, msg)

    def get_origins(self, txid):
        try:
            origins = []
            raw_tx = self.bitcoind.getrawtransaction(txid, 1)
            vins = raw_tx['vin']
            for vin in vins:
                raw_tx = self.bitcoind.getrawtransaction(vin['txid'], 1)
                for vout in raw_tx['vout']:
                    if vin['vout'] == vout['n']:
                        origins.extend(vout['scriptPubKey']['addresses'])
            return origins
        except JSONRPCException:
            return []

    def toggle_fullscreen_mode(self):
        if not self.customer_display.isFullScreen():
            self.customer_display.showFullScreen()
        else:
            self.customer_display.showNormal()

    def clear_customer_display(self):
        self.customer_display.evaluate_java_script('show_idle()')
        self.merchant_gui.update_status("System ready.");

    # this is thread-safe, as long as it is called from a QThread
    def exchange_rate_updated(self, rate, source):
        if not hasattr(self, 'app'): return  # not yet read
        self.app.emit(QtCore.SIGNAL('_exchange_rate_updated(PyQt_PyObject)'),
                (rate, source))

    def _exchange_rate_updated(self, data):
        (self.exchange_rate, self.exchange_rate_source) = data
        self.merchant_gui.update_exchange_rate(self.exchange_rate)
