import urllib
import json
from PyQt4.Qt import QThread

class Ticker(QThread):
    def __init__(self, source, currency, url, fields, interval, callback):
        QThread.__init__(self)
        self.source = source
        self.url = url
        self.fields = fields
        self.interval = interval
        self.callback = callback

    def run(self):
        while True:
            try:
                f = urllib.urlopen(self.url)
                data = f.read()
                feed = json.loads(data)
                rate = feed
                for field in self.fields:
                    rate = rate[field]
                rate = float(rate)
                self.callback(rate, self.source)
            except (ValueError, KeyError):
                print "Warning: Unable to parse exchange rate ticker"
            except IOError:
                print "Warning: Unable to access exchange rate ticker"
            self.sleep(self.interval)
