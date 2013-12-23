import os
import json

from controller import Controller
from ticker import Ticker
from txmonitor import TxMonitor
from nfcbroadcast import NFCBroadcast
from bluetoothreceiver import BluetoothReceiver

# check for configuration file
settings = { 'rpc_url': 'http://rpcuser:rpcpassword@127.0.0.1:8332'
           , 'green_addresses':
                { '1LNWw6yCxkUmkhArb2Nf2MPw6vG7u5WG7q': 'Verified by Mt.Gox.'
                , '1MAxx46Dp3tFw933PxPwEYYGCpxYda2pyH': 'Verified by Bridgewalker.'
                }
           , 'exchange_rate_ticker':
                { 'source': 'MtGox.com'
                , 'url': 'http://data.mtgox.com/api/1/BTCUSD/ticker'
                , 'currency' : 'USD'
                , 'fields': ['return', 'last', 'value']
                , 'interval': 60
                }
           , 'single_screen_mode': False
           }
conffile = os.path.expanduser('~/.greenaddress-pos-tool')
if os.path.isfile(conffile):
    try:
        with open(conffile, 'r') as f:
            settings = json.loads(f.read())
    except ValueError:
        print "Warning: Unable to parse configuration file."
else:
    # looks like no configuration exists -> create default one
    with open(conffile, 'w') as f:
        f.write(json.dumps(settings, sort_keys=True, indent=4) + "\n")

nfc_broadcast = NFCBroadcast()
controller = Controller(settings, nfc_broadcast)
bluetooth_receiver = BluetoothReceiver(
                        controller.bluetooth_available,
                        controller.new_transaction_via_bluetooth)
tx_monitor = TxMonitor(controller.new_transaction_received)
ticker_settings = settings['exchange_rate_ticker']
ticker = Ticker(ticker_settings['source'], ticker_settings['currency'], ticker_settings['url'],
        ticker_settings['fields'], ticker_settings['interval'],
        controller.exchange_rate_updated)

nfc_broadcast.start()
bluetooth_receiver.start()
tx_monitor.start()
ticker.start()
controller.run()
