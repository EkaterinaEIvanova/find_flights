# -*- coding: utf-8 -*-
import requests
from lxml import html


class Finding(object):
    def __init__(self, args):
        self.s_iata = args.sourceIATA
        self.d_iata = args.destinationIATA
        self.s_name = args.source_name
        self.d_name = args.destination_name
        self.r_date = args.return_date
        self.o_date = args.outbound_date
        self.one_way = args.one_way
        self.outbound_data = ''
        self.return_data = ''
        self.currency = ''
        self.flights = []
        self.flights_mix = []
        self.content = []

    def get_content(self):
        """
        Делаю http-запрос к сайту, получаю ответ. Если контент содержит полезную информацию, то забираю ее.
        :return:content
        """
        headers = {'Content-Type': 'application/x-www-form-urlencoded',
                   'Cookie': 'startConnection={}@{}@{}@{}; ABSESS=kbfj0b77ueq4sh5s9gpg8np392;'.format(
                       self.s_iata,
                       self.d_iata,
                       self.o_date,
                       self.r_date)
                   }

        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php?sid=ba9d2bc0faf73daf9c69'
        data = {'_ajax[templates][]': ['main', 'priceoverview', 'infos', 'flightinfo'],
                '_ajax[requestParams][departure]': '{}'.format(self.s_name),
                '_ajax[requestParams][destination]': '{}'.format(self.d_name),
                '_ajax[requestParams][returnDeparture]': '',
                '_ajax[requestParams][returnDestination]': '',
                '_ajax[requestParams][outboundDate]': '{}'.format(self.o_date),
                '_ajax[requestParams][returnDate]': '{}'.format(self.r_date),
                '_ajax[requestParams][adultCount]': '1',
                '_ajax[requestParams][childCount]': '0',
                '_ajax[requestParams][infantCount]': '0',
                '_ajax[requestParams][openDateOverview]': '',
                '_ajax[requestParams][oneway]': '{}'.format(self.one_way),
                }
        content = requests.post(url, headers=headers, data=data).json()
        if content.get('templates') and content['templates'].get('main'):
            if content['templates']['main'] != ' <div id="vacancy_infos"></div> ':
                self.content = content['templates']['main']

    def get_flights(self):
        """
        Забираю из контента только нужные данные по рейсам.
        :return:
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
                    flights.append(data + ['econ', self.currency, float(econ_data.replace(',', ''))])
                    flights.append(data + ['comf', self.currency, float(comf_data.replace(',', ''))])
                self.flights.append(flights)

    def mix(self):
        if self.one_way:
            self.flights_mix = self.flights[0]
            self.flights_mix.sort(key=lambda j: j[-1])
            for i, fl in enumerate(self.flights_mix):
                self.flights_mix[i][-1] = str(self.flights_mix[i][-1])
        else:
            self.flights_mix = [outb_fl + return_fl + [float(outb_fl[-1]) + float(return_fl[-1])]
                                for outb_fl in self.flights[0] for return_fl in self.flights[1]]
            self.flights_mix.sort(key=lambda j: j[-1])
            for i, fl in enumerate(self.flights_mix):
                self.flights_mix[i][-1] = str(self.flights_mix[i][-1])
                self.flights_mix[i][-2] = str(self.flights_mix[i][-2])
                self.flights_mix[i][6] = str(self.flights_mix[i][6])

    def __str__(self):
        flights_str = '\n'.join([' '.join(fl) for fl in self.flights_mix])
        return '{}\n{}\n{}'.format(self.outbound_data.encode('utf-8').lstrip(),
                                 self.return_data.encode('utf-8').lstrip(),
                                 (flights_str).encode('utf-8'))
