# -*- coding: utf-8 -*-
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
        self.content = self._get_content()
        self.outbound_data = ''
        self.return_data = ''
        self.currency = ''
        self.flights = []
        self.flights_str = []

    def _get_content(self):
        '''
        Делаю http-запрос к сайту, получаю ответ и если есть, то забираю из него контент.
        :return:content
        '''
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cookie':'startConnection={}@{}@{}@{}; ABSESS=kbfj0b77ueq4sh5s9gpg8np392;'.
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
        content = requests.post(url, headers=headers, data=data).json()['templates']['main']
        if content != ' <div id="vacancy_infos"></div> ':
            return content
        else:
            return None

    def get_flights(self):
        '''
           Забираю из контента только нужные данные по рейсам.
        :return:
        '''
        if self.content:
            tree = html.fromstring(self.content)
            self.outbound_data = tree.xpath('// *[@id="flighttables"]/div[1]/div[1]/div[1]/div/div/text()')[0]
            self.return_data = tree.xpath('//*[@id="flighttables"]/div[3]/div[1]/div[1]/div/div/text()')[0]
            self.currency = tree.xpath('//*[@id="flight-table-header-price-ECO_COMF"]/text()')[0]

            for tb in tree.xpath('.//table[@class="flighttable"]'):
                flights = []
                for tr in tb.xpath('./tbody/tr[position() mod 2 = 1]'):
                    flights.append(tr.xpath('./td//text()[not(contains(.,"seat"))][string-length()>1]'))
                self.flights.append(flights)

    def sort(self):
        '''
         В полученный рейсах высчитывается общая стоимость переета, данные преобразуются в строки для вывода
        :return:
        '''
        if self.flights:
            for i, flights in enumerate(self.flights):
                for n, fl in enumerate(flights):
                    flights[n].append(float(fl[3].replace(',', '')) + float(fl[-1].replace(',', '')))
                flights.sort(key=lambda j: j[-1])
                self.flights[i] = flights

    def __str__(self):
        if self.flights:
            for flights in self.flights:
                for fl in flights:
                    fl[-1] = str(fl[-1])
                self.flights_str.append('\n'.join([' '.join(fl) for fl in flights]))
            head = u'start  end    duration   {},econ{},econ1{},comf{},sum{}'.format(self.currency.rstrip(),
                                                                            self.currency.rstrip(),
                                                                            self.currency.rstrip(),
                                                                            self.currency.rstrip(),
                                                                            self.currency.rstrip())
            return '{}\n{}\n{}\n\n{}\n{}\n{}'.format(self.outbound_data.encode('utf-8').lstrip(),
                                                 head.encode('utf-8'),
                                                 self.flights_str[0].encode('utf-8'),
                                                 self.return_data.encode('utf-8').lstrip(),
                                                 head.encode('utf-8'),
                                                 self.flights_str[1].encode('utf-8'))
