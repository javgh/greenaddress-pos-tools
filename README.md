#### Description

This is a Bitcoin point of sale application. It was mainly written to
demonstrate the use of the green address feature, but can also be used
independently of that. It is written in Python and works in combination with the
standard Bitcoin-Qt client. It is targeted at standard PC hardware, e.g. laptop
(used by merchant) + external monitor (facing the customer). See a video of the
system in action at http://www.youtube.com/watch?v=o84SfChQ-S8 .

#### Screenshots

- System idle
  - Merchant view: https://github.com/downloads/javgh/greenaddress-pos-tools/screenshot_after_startup_merchant.png
  - Customer view: https://github.com/downloads/javgh/greenaddress-pos-tools/screenshot_after_startup_customer.png
- Entering a new amount
  - Merchant view: https://github.com/downloads/javgh/greenaddress-pos-tools/screenshot_entering_amount_merchant.png
  - Customer view: https://github.com/downloads/javgh/greenaddress-pos-tools/screenshot_entering_amount_customer.png
- Receiving a transaction from Instawallet's green address
  - Merchant view: https://github.com/downloads/javgh/greenaddress-pos-tools/screenshot_received_from_green_address_merchant.png
  - Customer view: https://github.com/downloads/javgh/greenaddress-pos-tools/screenshot_received_from_green_address_customer.png

#### Getting started

The system requires at least Bitcoin-Qt 0.8.2, as it is making use of the
'walletnotify' feature. To check for green addresses a complete transaction
index is also required, which can be enabled by adding 'txindex=1' to
bitcoin.conf and starting the daemon with '-reindex' to build the index the
first time. The configuration file ~/.bitcoin/bitcoin.conf should look something
like this:

````
server=1
txindex=1
rpcuser=rpcuser
rpcpassword=rpcpassword
````

Then start bitcoind like listed below (-reindex is only needed on the first
run). Make sure that the queue-tx utility is executable, so that bitcoind can
call it when new transactions are received.

````
./bitcoind -reindex -walletnotify="/path/to/greenaddress-pos-tools/utils/queue-tx %s"
````

Afterwards you are ready to start the Python app:

- install dependencies: python-qrencode, python-qt4, python-zmq
- create the file $HOME/.greenaddress-pos-tool with this contents (or let the
  app create this default configuration file when first starting up):

````
{
    "exchange_rate_ticker": {
        "currency": "USD", 
        "fields": [
            "return", 
            "last", 
            "value"
        ], 
        "interval": 60, 
        "source": "MtGox.com", 
        "url": "http://data.mtgox.com/api/1/BTCUSD/ticker"
    }, 
    "green_addresses": {
        "1LNWw6yCxkUmkhArb2Nf2MPw6vG7u5WG7q": "Verified by Mt.Gox.", 
        "1MAxx46Dp3tFw933PxPwEYYGCpxYda2pyH": "Verified by Bridgewalker."
    }, 
    "rpc_url": "http://rpcuser:rpcpassword@127.0.0.1:8332", 
    "single_screen_mode": false
}
````

- run: python pos-tool.py

You should see two windows popping up: The merchant back end and the customer
display. If you enter a BTC amount and click "Update display", a new Bitcoin
address and associated QR code will be generated and displayed to the customer.
The tool then listens for transactions to the Bitcoin address and as soon as it
receives something, it changes the display to read "Payment received". If the
payment was done via Bridgewalker's green address, it will add the phrase
"Verified by Bridgewalker". The merchant is expected to use their Bitcoin client
to see if the correct amount was sent.

#### Green address technique

You can read more about the green address technique in this thread:
http://bitcointalk.org/index.php?topic=32818.0 or on the wiki:
https://en.bitcoin.it/wiki/Green_address . Currently (as of June 2013)
Mt.Gox and Bridgewalker ( https://www.bridgewalkerapp.com/ ) implement this
convention and allow to send transactions that will be recognized by the Python
app as originating from a green address.

#### Development

I'm developing on Linux, so this is only tested on Linux. But I would
hope this to be fairly portable. Patches to make it work (better) on
Windows and/or Mac OS are welcome.

If you appreciate this release, donations are gladly accepted at
1CQoprPjRmsDQDzgmUK1njmXSv3SMpAjm7 .
