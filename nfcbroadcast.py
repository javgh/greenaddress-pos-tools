#!/usr/bin/env python

import time

from PyQt4.Qt import QThread
from Queue import Queue

import nfc
import nfc.snep

class NFCBroadcast(QThread):
    def __init__(self):
        self.btc_uri = None
        self.restart_required = False
        self.start_signal = Queue()
        try:
            self.clf = nfc.ContactlessFrontend('usb')
            print "Contactless reader ready"
        except IOError:
            self.clf = None
            print "No contactless reader found"
        super(NFCBroadcast, self).__init__()

    def run(self):
        # wait for first URI
        _ = self.start_signal.get()

        if self.clf:
            self.serve_nfc()
        else:
            self.idle_forever()

    def serve_nfc(self):
        print "Contactless reader active"
        while True:
            self.clf.connect( llcp={'on-connect': self.connected}
                            , terminate=self.check_restart
                            )

    def idle_forever(self):
        while True:
            time.sleep(60)

    def set_btc_uri(self, btc_uri):
        if self.btc_uri == None:
            self.btc_uri = btc_uri
            self.start_signal.put('start')
        else:
            self.btc_uri = btc_uri
            self.restart_required = True

    def connected(self, llc):
        self.helper = NFCBroadcastHelper(llc, self.btc_uri)
            # store reference to thread beyond the local function
            # to prevent if from being garbage collected
        self.helper.start()
        return True

    def check_restart(self):
        if self.restart_required:
            self.restart_required = False
            return True
        else:
            return False

class NFCBroadcastHelper(QThread):
    def __init__(self, llc, btc_uri):
        self.llc = llc
        self.btc_uri = btc_uri
        super(NFCBroadcastHelper, self).__init__()

    def run(self):
        sp = nfc.ndef.SmartPosterRecord(self.btc_uri)
        snep = nfc.snep.SnepClient(self.llc)
        snep.put(nfc.ndef.Message(sp))

if __name__ == '__main__':
    nfc_broadcast = NFCBroadcast()
    nfc_broadcast.start()

    nfc_broadcast.set_btc_uri('bitcoin:16mj2Veiw6rWHBDn4dN8rAAsRJog7EooYF?amount=0.0001')
    while True:
        time.sleep(60)
