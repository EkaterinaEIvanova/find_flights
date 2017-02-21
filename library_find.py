# -*- coding: utf-8 -*-
import requests
from lxml import html


class Finding(object):
    def __init__(self, args):
        self.outbound_data = ''
        self.return_data = ''
        self.currency = ''
        self.one_way = args.one_way
        self.content = []
        self.flights = []
        self.flights_full = []
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Cookie': 'startConnection={}@{}@{}@{}; ABSESS=kbfj0b77ueq4sh5s9gpg8np392;'.format(
                          args.sourceIATA,
                          args.destinationIATA,
                          args.outbound_date,
                          args.return_date)
                         }
        self._url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?sid=ba9d2bc0faf73daf9c69'
        self._data = {'_ajax[templates][]': ['main', 'priceoverview', 'infos', 'flightinfo'],
                      '_ajax[requestParams][departure]': '{}'.format(args.source_name),
                      '_ajax[requestParams][destination]': '{}'.format(args.destination_name),
                      '_ajax[requestParams][returnDeparture]': '',
                      '_ajax[requestParams][returnDestination]': '',
                      '_ajax[requestParams][outboundDate]': '{}'.format(args.outbound_date),
                      '_ajax[requestParams][returnDate]': '{}'.format(args.return_date),
                      '_ajax[requestParams][adultCount]': '1',
                      '_ajax[requestParams][childCount]': '0',
                      '_ajax[requestParams][infantCount]': '0',
                      '_ajax[requestParams][openDateOverview]': '',
                      '_ajax[requestParams][oneway]': '{}'.format(args.one_way),
                      }

    def get_content(self):
        """
        Делаю http-запрос к сайту, получаю ответ. Если контент содержит полезную информацию, то забираю ее.
        :return:content
        """
        content = requests.post(self._url, headers=self._headers, data=self._data).json()
        if content.get('templates') and content['templates'].get('main') and \
                        content['templates']['main'] != ' <div id="vacancy_infos"></div> ':
                self.content = content['templates']['main']

    def get_flights(self):
        """
        Извлекаю из контента только необходимые данные по рейсам, заношу их в список.
        :return: self.flights
        """
        if self.content:
            tree = html.fromstring(self.content)
            self.outbound_data = tree.xpath('// *[@id="flighttables"]/div[1]/div[1]/div[1]/div/div/text()')[0]
            if not self.one_way:
                self.return_data = tree.xpath('//*[@id="flighttables"]/div[3]/div[1]/div[1]/div/div/text()')[0]
            self.currency = tree.xpath('//*[@id="flight-table-header-price-ECO_COMF"]/text()')[0]

            for tb in tree.xpath('.//table[@class="flighttable"]'):
                flights = []
                for tr in tb.xpath('./tbody/tr[position() mod 2 = 1]'):
                    data = tr.xpath('./td[2]/span/*/text()|td[3]/text()|./td[4]/span/text()')
                    econ_data = tr.xpath('./td[6]/span/text()|./td[6]/label/div[1]/span//text()')[0]
                    comf_data = tr.xpath('./td[5]/span/text()|./td[5]/label/div[1]/span//text()')[0]
                    flights.append(data + ['econ', self.currency, econ_data.replace(',', '')])
                    flights.append(data + ['comf', self.currency, comf_data.replace(',', '')])
                self.flights.append(flights)

    def mix(self):
        """
        Из self.flights извлекаю все варианты рейсов, при необходимости подсчитываю суммарную стоимость перелета.
        :return:
        """
        if self.one_way:
            self.flights_full = [fl for fl in self.flights[0] if unicode(fl[-1]) != u' \u2014 ']
        else:
            for o_fl in self.flights[0]:
                for r_fl in self.flights[1]:
                    if unicode(o_fl[-1]) != u' \u2014 ' and unicode(r_fl[-1]) != u' \u2014 ':
                        self.flights_full.append(o_fl + r_fl + [self.currency, str(float(o_fl[-1]) + float(r_fl[-1]))])

    def sort(self):
        self.flights_full.sort(key=lambda j: float(j[-1]))

    def __str__(self):
        flights_str = '\n'.join([' '.join(fl) for fl in self.flights_full])
        return '{}\n{}\n{}'.format(self.outbound_data.encode('utf-8').lstrip(),
                                   self.return_data.encode('utf-8').lstrip(),
                                   (flights_str).encode('utf-8'))
