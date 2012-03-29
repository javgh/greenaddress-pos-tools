#### Description

This is a Bitcoin point of sale application. It was mainly written to
demonstrate the use of the green address feature, but can also be used
independently of that. It is written in Python and works in combination with a
standard Bitcoin client. It is targeted at standard PC hardware, e.g. laptop
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

- install dependencies: python-qrencode, python-qt4
- add "server=1" (but not daemon=1) to bitcoin.conf and configure rpcuser & rpcpassword
- create the file $HOME/.greenaddress-pos-tool with this contents:

````
{
    "exchange_rate_ticker": {
        "source": "MtGox.com", 
        "currency": "USD",
        "url": "https://mtgox.com/api/0/data/ticker.php",
        "fields": ["ticker", "last"], 
        "interval": 5 
    }, 
    "green_addresses": {
        "1CDysWzQ5Z4hMLhsj4AKAEFwrgXRC8DqRN": "Verified by Instawallet."
    }, 
    "rpc_url": "http://rpcuser:rpcpassword@127.0.0.1:8332"
}
````

- run: python pos-tool.py

You should see two windows popping up: The merchant back end and the
customer display. If you enter a BTC amount and click "Update display",
a new Bitcoin address and associated QR code will be generated and
displayed to the customer. The tool then listens for transactions to the
Bitcoin address and as soon as it receives something, it changes the
display to read "Payment received". If the payment was done via
Instawallets green address, it will add the phrase "Verified by
Instawallet". The merchant is expected to use their Bitcoin client to
see if the correct amount was sent.

#### Green address technique

You can read more about the green address technique in this thread:
http://bitcointalk.org/index.php?topic=32818.0 . Currently (as of August 2011)
only https://www.instawallet.org implements this convention. If you want to
initiate green address transactions from your mobile phone, you will need a
mobile client for Instawallet. I'm currently only aware of the Android client
BitPay ( https://github.com/warpi/BitPay ), with a few other clients still in
development. The current version of BitPay available in the Android market does
not yet include support for the green address feature. A (self-signed) version
that does, can be found here:
https://github.com/javgh/greenaddress-pos-tools/BitPay.apk/qr_code .

#### Development

I'm developing on Linux, so this is only tested on Linux. But I would
hope this to be fairly portable. Patches to make it work (better) on
Windows and/or Mac OS are welcome.

If you look at the code, you will see that it contains a simple Bitcoin
node implementation. This is used to listen for transactions and get
notified as soon as one arrives. This could be done much easier with a
patch to bitcoind (for example a version of Gavin's monitor patch:
https://github.com/bitcoin/bitcoin/pull/198 ), but an important goal of
this project is to have as few dependencies as possible and especially
be able to run with a vanilla Bitcoin daemon. This is why I went the
route of using ArtForz' "half-a-node" implementation to listen for
transactions manually. (Hopefully this can be dropped at some point in
the future, when the official client allows some form of
push-notification directly.)

If you appreciate this initial release, donations are gladly accepted at
1CQoprPjRmsDQDzgmUK1njmXSv3SMpAjm7 .
