#### Getting started

- install dependencies: python-qrencode, python-qt4
- add "server=1" (but not daemon=1) to bitcoin.conf and configure rpcuser & rpcpassword
- create the file $HOME/.greenaddress-pos-tool with this contents:

````
{
    "exchange_rate_ticker": {
        "source": "MtGox.com", 
        "url": "https://mtgox.com/api/0/data/ticker.php",
        "field": "last", 
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
