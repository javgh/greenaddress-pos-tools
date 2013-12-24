#!/usr/bin/env python

# NFC communication is implemented in its own process, as apparently
# nfcpy and the Qt main event loop do not play well together.
# A queue is used to communicate across process boundaries and submit
# the current Bitcoin URI to be broadcasted via NFC.

import threading
import time

from multiprocessing import Process, Queue

import nfc
import nfc.snep

class NFCBroadcast:
    def start(self):
        self.queue = Queue()
        self.nfc_process = NFCProcess(self.queue)
        self.nfc_process.start()

    def set_btc_uri(self, btc_uri):
        self.queue.put(('uri', btc_uri))

    def shutdown(self):
        self.queue.put(('shutdown', None))

class NFCProcess(Process):
    def __init__(self, queue):
        self.queue = queue
        super(NFCProcess, self).__init__()

    def run(self):
        nfc_conn = NFCConnection()
        nfc_conn.start()

        is_running = True
        while is_running:
            (cmd, param) = self.queue.get()
            if cmd == 'uri':
                nfc_conn.set_btc_uri(param)
            elif cmd == 'shutdown':
                is_running = False

class NFCConnection(threading.Thread):
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
        super(NFCConnection, self).__init__()

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
        self.helper = NFCConnectionHelper(llc, self.btc_uri)
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

class NFCConnectionHelper(threading.Thread):
    def __init__(self, llc, btc_uri):
        self.llc = llc
        self.btc_uri = btc_uri
        super(NFCConnectionHelper, self).__init__()

    def run(self):
        sp = nfc.ndef.SmartPosterRecord(self.btc_uri)
        snep = nfc.snep.SnepClient(self.llc)
        snep.put(nfc.ndef.Message(sp))

if __name__ == '__main__':
    nfc_broadcast = NFCBroadcast()
    nfc_broadcast.start()

    nfc_broadcast.set_btc_uri('bitcoin:16mj2Veiw6rWHBDn4dN8rAAsRJog7EooYF?amount=0.0001')
    time.sleep(20)

    nfc_broadcast.set_btc_uri('bitcoin:16mj2Veiw6rWHBDn4dN8rAAsRJog7EooYF?amount=0.0002')
    while True:
        time.sleep(60)
