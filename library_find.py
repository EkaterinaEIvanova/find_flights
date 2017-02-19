import requests
from lxml import html


class Finding(object):
    def __init__(self, args):
        self.i_iata = args.iIATA
        self.o_iata = args.oIATA
        self.i_name = args.i_name
        self.o_name = args.o_name
        self.idata = args.idata
        self.odata = args.odata
        self.resp_body  = ''
        self.flights = []

    def get_body(self):
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cookie':'startConnection={}@{}@{}@{}1; ABSESS=kbfj0b77ueq4sh5s9gpg8np392;'.
                       format(self.i_iata, self.o_iata, self.idata, self.odata)
                   }

        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?sid=ba9d2bc0faf73daf9c69'
        data = {'_ajax[templates][]': ['main', 'priceoverview', 'infos', 'flightinfo'],
                '_ajax[requestParams][departure]': '{}'.format(self.i_name),
                '_ajax[requestParams][destination]': '{}'.format(self.o_name),
                '_ajax[requestParams][returnDeparture]': '',
                '_ajax[requestParams][returnDestination]': '',
                '_ajax[requestParams][outboundDate]': '{}'.format(self.idata),
                '_ajax[requestParams][returnDate]': '{}'.format(self.odata),
                '_ajax[requestParams][adultCount]': '1',
                '_ajax[requestParams][childCount]': '0',
                '_ajax[requestParams][infantCount]': '0',
                '_ajax[requestParams][openDateOverview]': '',
                '_ajax[requestParams][oneway]': '',
                }
        self.resp_body = requests.post(url, headers=headers, data=data).json()['templates']['main']

    def get_flights(self):
        tree = html.fromstring(self.resp_body)
        outbound_data = tree.xpath('// *[@id="flighttables"]/div[1]/div[1]/div[1]/div/div/text()')[0]
        return_data = tree.xpath('//*[@id="flighttables"]/div[3]/div[1]/div[1]/div/div/text()')[0]
        currency = tree.xpath('//*[@id="flight-table-header-price-ECO_COMF"]/text()')[0]

        for tb in tree.xpath('.//table[@class="flighttable"]'):
            flights = []
            for tr in tb.xpath('./tbody/tr[position() mod 2 = 1]'):
                flights.append(tr.xpath('./td//text()[string-length()>1]'))
            self.flights.append(flights)
