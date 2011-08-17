import os
import json
from controller import Controller
from greenaddresscheck.greenaddresscheck import GreenAddressCheck
from ticker import Ticker

# check for configuration file
settings = { 'rpc_url': 'http://rpcuser:rpcpassword@127.0.0.1:8332'
           , 'green_addresses':
                { '1CDysWzQ5Z4hMLhsj4AKAEFwrgXRC8DqRN': 'Verified by Instawallet.' }
           , 'exchange_rate_ticker':
                { 'source': 'MtGox.com'
                , 'url': 'https://mtgox.com/api/0/data/ticker.php'
                , 'field': 'last'
                , 'interval': 5
                }
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

controller = Controller(settings)
green_address_check = GreenAddressCheck(settings['green_addresses'], controller.new_transaction_received)
ticker_settings = settings['exchange_rate_ticker']
ticker = Ticker(ticker_settings['source'], ticker_settings['url'],
        ticker_settings['field'], ticker_settings['interval'],
        controller.exchange_rate_updated)

green_address_check.start()
ticker.start()
controller.run()
