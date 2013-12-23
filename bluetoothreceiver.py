#!/usr/bin/env python

import binascii
import errno
import socket
import struct
import time

import bluetooth._bluetooth as _bt

from bluetooth import *
from PyQt4.Qt import QThread

BITCOIN_BLUETOOTH_UUID = "3357a7bb-762d-464a-8d9a-dca592d57d5b"

class BluetoothReceiver(QThread):
    def __init__(self, callback_address, callback_new_transaction):
        self.callback_address = callback_address
        self.callback_new_transaction = callback_new_transaction
        super(BluetoothReceiver, self).__init__()

    def find_local_bdaddr(self):
        dev_id = 0
        hci_sock = _bt.hci_open_dev(dev_id)

        old_filter = hci_sock.getsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, 14)
        flt = _bt.hci_filter_new()
        opcode = _bt.cmd_opcode_pack(_bt.OGF_INFO_PARAM, _bt.OCF_READ_BD_ADDR)
        _bt.hci_filter_set_ptype(flt, _bt.HCI_EVENT_PKT)
        _bt.hci_filter_set_event(flt, _bt.EVT_CMD_COMPLETE);
        _bt.hci_filter_set_opcode(flt, opcode)
        hci_sock.setsockopt(_bt.SOL_HCI, _bt.HCI_FILTER, flt)

        _bt.hci_send_cmd(hci_sock, _bt.OGF_INFO_PARAM, _bt.OCF_READ_BD_ADDR)

        pkt = hci_sock.recv(255)

        status,raw_bdaddr = struct.unpack("xxxxxxB6s", pkt)
        assert status == 0

        t = [ "%X" % ord(b) for b in raw_bdaddr ]
        t.reverse()
        bdaddr = ":".join(t)

        # restore old filter
        hci_sock.setsockopt( _bt.SOL_HCI, _bt.HCI_FILTER, old_filter )
        return bdaddr

    def run(self):
        # find our Bluetooth address
        bt_addr = self.find_local_bdaddr()

        # inform controller about our Bluetooth address
        self.callback_address(bt_addr)

        # find a free port; PORT_ANY does not seem to work correctly
        port_available = False
        server_sock = BluetoothSocket(RFCOMM)
        for port in range(1, 10):
            try:
                server_sock.bind((bt_addr, port))
                port_available = True
                break
            except Exception as e:  # IOError does not seem to catch the right exception
                if e[0] == errno.EADDRINUSE:
                    pass
                else:
                    raise e

        if not port_available:
            print 'No free bluetooth port found'
            return

        server_sock.listen(1)
        port = server_sock.getsockname()[1]

        advertise_service( server_sock, "Bitcoin Transaction Submission"
                         , service_id = BITCOIN_BLUETOOTH_UUID
                         , service_classes = [ BITCOIN_BLUETOOTH_UUID ]
                         , profiles = [ ]
                         )

        print "Bluetooth: waiting for connection on RFCOMM channel %d" % port
        while True:
            client_sock, client_info = server_sock.accept()
            print "Accepted connection from ", client_info

            try:
                # header: a single '1' and then the length of the serialized transaction
                unpacker = struct.Struct('! I I')
                header = client_sock.recv(unpacker.size, socket.MSG_WAITALL)
                (just_one, tx_length) = unpacker.unpack(header)

                # some checks
                if just_one != 1:
                    raise IOError

                if tx_length > 2 ** 24:
                    raise IOError

                # body: the data for the serialized transaction
                unpacker = struct.Struct('! %ss' % tx_length)
                body = client_sock.recv(unpacker.size, socket.MSG_WAITALL)
                tx = unpacker.unpack(body)

                self.callback_new_transaction(binascii.hexlify(tx[0]))

                # send ack back
                packer = struct.Struct('! ?')
                packed_data = packer.pack(True)
                client_sock.send(packed_data)
            except IOError:
                pass

            print "Bluetooth client disconnected"
            client_sock.close()
        #server_sock.close()

def debug_bt_addr(addr):
    print addr

def debug_tx_received(tx):
    print tx

if __name__ == '__main__':
    bluetooth_receiver = BluetoothReceiver(debug_bt_addr, debug_tx_received)
    bluetooth_receiver.start()

    while True:
        time.sleep(60)
