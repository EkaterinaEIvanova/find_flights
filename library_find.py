from lxml import etree
from lxml import html
import json
import requests
from six import BytesIO
from six import StringIO


class Finding(object):
    def __init__(self, args):
        self.iiata = args.iIATA
        self.oiata = args.oIATA
        self.idata = args.idata
        self.odata = args.odata
        self.r = self.get_rbody()
        self.get_flights()

    def get_rbody(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cookie':'startConnection=DME@MUC@2017-03-31@2017-03-31; ABSESS=kbfj0b77ueq4sh5s9gpg8np392;'
                   }

        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?sid=ba9d2bc0faf73daf9c69'
        data = {'_ajax[templates][]': ['main','priceoverview', 'infos','flightinfo'],
                '_ajax[requestParams][departure]':'Moscow - Domodedovo',
                '_ajax[requestParams][destination]':'Munich',
                '_ajax[requestParams][returnDeparture]':'',
                '_ajax[requestParams][returnDestination]':'',
                '_ajax[requestParams][outboundDate]': '2017-03-31',
                '_ajax[requestParams][returnDate]':'2017-03-31',
                '_ajax[requestParams][adultCount]':'1',
                '_ajax[requestParams][childCount]':'0',
                '_ajax[requestParams][infantCount]':'0',
                '_ajax[requestParams][openDateOverview]':'',
                '_ajax[requestParams][oneway]':'',
                }
        return requests.post(url, headers=headers, data=data).json()['templates']['main']

    def get_flights(self):
        tree = html.fromstring(self.r)
        outbound_flight = tree.xpath('// *[@id="flighttables"]/div[1]/div[1]/div[1]/div/div/text()')[0]
        return_flight = tree.xpath('//*[@id="flighttables"]/div[3]/div[1]/div[1]/div/div/text()')[0]
        cur = tree.xpath('//*[@id="flight-table-header-price-ECO_COMF"]/text()')[0]
        if not cur:
            cur = tree.xpath('//*[@id="flight-table-header-price-ECO_PREM"]/text()')[0]
        time = tree.xpath('.//table[@class="flighttable"]/tbody/tr/td[2]/span/*/text()')
        stop =  tree.xpath('.//table[@class="flighttable"]/tbody/tr/td[3]/text()')
        duration = tree.xpath('.//table[@class="flighttable"]/tbody/tr/td[4]/span/text()')
        eco_price = tree.xpath('.//table[@class="flighttable"]/tbody/tr/td[5]/label/div[2]/span/text()')
        comf_price = tree.xpath('.//table[@class="flighttable"]/tbody/tr/td[6]/label/div[1]/span/text()')



