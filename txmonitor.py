import zmq

from PyQt4.Qt import QThread

PORT = 15556

# note: apparently we need to use a QThread if we want to
#       safely communicate with other QT threads.
class TxMonitor(QThread):
    def __init__(self, callback):
        QThread.__init__(self)
        self.callback = callback

    def run(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://127.0.0.1:%s" % PORT)

        while True:
            txid = socket.recv()
            socket.send("")
            self.callback(txid)
