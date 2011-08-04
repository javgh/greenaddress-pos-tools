import asyncore
from minimalnode import MinimalBitcoinNode
from bitcointools.deserialize import extract_public_key

from PyQt4.Qt import QThread

INSTAPAY_ADDRESS = "1CDysWzQ5Z4hMLhsj4AKAEFwrgXRC8DqRN"

# note: apparently we need to use a QThread if we want to
#       safely communicate with other QT threads.
class GreenAddressCheck(QThread):
    def __init__(self, callback):
        QThread.__init__(self)
        self.callback = callback
        self.keep_running = True

    def run(self):
        monitor_node = MonitorNode('127.0.0.1', 8333, [ INSTAPAY_ADDRESS ],
                self.callback)
        asyncore.loop()

class MonitorNode(MinimalBitcoinNode):
    def __init__(self, dstaddr, dstport, addresses, callback):
        MinimalBitcoinNode.__init__(self, dstaddr, dstport)
        self.addresses = addresses
        self.callback = callback

    def handle_tx(self, tx):
        found = False
        for txin in tx.vin:
            if extract_public_key(txin.scriptSig) in self.addresses:
                found = True
                break
        output_addresses = []
        for txout in tx.vout:
            output_addresses.append(extract_public_key(txout.scriptPubKey))

        txid = "%064x" % tx.sha256
        self.callback(txid, output_addresses, found)
