# -*- coding: utf-8 -*-
""" Библиотека для получение всевозможных вариантов рейсов
согласно ресурсу www.flyniki.com по заданным параметрам Пользоватаеля."""
import requests
from lxml import html


class FindingFlights(object):
    """ args(sIATA, dIATA, o_date, r_date) --> flights_str/error_str """
    def __init__(self, args):
        args.outbound_date = args.outbound_date.strftime('%Y-%m-%d')
        args.return_date = args.return_date.strftime('%Y-%m-%d')
        self.args = args
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Cookie': 'startConnection={}@{}@{}@{};ABSESS='
                                   'kbfj0b77ueq4sh5s9gpg'
                                   '8np392;'.format(self.args.sourceIATA,
                                                    self.args.destinationIATA,
                                                    self.args.outbound_date,
                                                    self.args.return_date)}
        self.args.source_name = self._get_airport(args.sourceIATA)
        self.args.destination_name = self._get_airport(args.destinationIATA)
        self.outbound_data = ''
        self.return_data = ''
        self.currency = ''
        self.content = []
        self.flights = []
        self.flights_full = []

    def _get_airport(self, iata):
        """
        Делаю запрос на получение имени аэропорта соотвествующего IATA.
        :param args: iata:
        :return:airport_name or None
        """
        payload = {'searchfor': 'departures',
                   'searchflightid': '0',
                   'departures[]': [iata, 'City, airport'],
                   'destinations[]': ['', 'City, airport'],
                   'suggestsource[0]': 'activeairports',
                   'withcountries': '0',
                   'withoutroutings': '0',
                   'promotion[id]': '',
                   'promotion[type]': '',
                   'get_full_suggest_list': 'true',
                   'routesource[0]': 'airberlin',
                   'routesource[1]': 'partner'}
        url = 'http://www.flyniki.com/en/site/json/suggestAirport.php'
        content = requests.post(url, params=payload,
                                headers=self._headers).json()
        if content.get('suggestList'):
            for dct in content.get('suggestList'):
                if dct['code'] == iata:
                    return dct['name']
        else:
            return None

    def get_content(self):
        """
        Делаю http-запрос к сайту по исходным параметрам и получаю ответ.
        _url, _headers, _data --> content
        """
        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php'
        payload = {'sid': 'ba9d2bc0faf73daf9c69'}
        data = {'_ajax[templates][]':
                ['main', 'priceoverview', 'infos', 'flightinfo'],
                '_ajax[requestParams]'
                '[departure]': '{}'.format(self.args.source_name),
                '_ajax[requestParams]'
                '[destination]': '{}'.format(self.args.destination_name),
                '_ajax[requestParams][returnDeparture]': '',
                '_ajax[requestParams][returnDestination]': '',
                '_ajax[requestParams]'
                '[outboundDate]': '{}'.format(self.args.outbound_date),
                '_ajax[requestParams]'
                '[returnDate]': '{}'. format(self.args.return_date),
                '_ajax[requestParams][adultCount]': '1',
                '_ajax[requestParams][childCount]': '0',
                '_ajax[requestParams][infantCount]': '0',
                '_ajax[requestParams][openDateOverview]': '',
                '_ajax[requestParams]'
                '[oneway]': '{}'.format(self.args.one_way), }
        content = requests.post(url, headers=self._headers, params=payload,
                                data=data).json()
        if content.get('templates') and content['templates'].get('main'):
            if content['templates']['main'] != \
                    ' <div id="vacancy_infos"></div> ':
                self.content = content['templates']['main']

    def get_flights(self):
        """
        Извлекаю необходимые данные по рейсам при наличии.
        content --> flights
        """
        if self.content:
            tree = html.fromstring(self.content)
            self.outbound_data = tree.xpath('// *[@id="flighttables"]/div[1]/'
                                            'div[1]/div[1]/div/div/text()')[0]
            if not self.args.one_way:
                self.return_data = tree.xpath('//*[@id="flighttables"]/div[3]/'
                                              'div[1]/div[1]/div/div/'
                                              'text()')[0]
            table = tree.xpath('.//table[@class="flighttable"]')[0]
            self.currency = table.xpath('./thead/tr//th/text()')[-1]
            classes = table.xpath('./thead/tr[1]/td/div/label//text()')
            for table in tree.xpath('.//table[@class="flighttable"]'):
                flights = []
                for row in table.xpath('./tbody/tr[position() mod 2 = 1]'):
                    data = row.xpath('./td[2]/span/*/text()|td[3]/text()|./'
                                     'td[4]/span/text()')
                    for i, clss in enumerate(classes):
                        # Получаю стоимость билетов в ячейках td[5-9] для
                        # всех классов из списка classes.
                        price = row.xpath('./td[{}]/span/text()|./td[{}]/'
                                          'label/div[1]/span//text()'.
                                          format(i+5, i+5))
                        if price:
                            flights.append(data + [clss, self.currency,
                                                   price[0].replace(',', '')])
                self.flights.append(flights)

    def get_flights_full(self):
        """
        Генерирую всевозможные варианты перелетов, при необходимости
        подсчитываю суммарную стоимость.
        flights --> flights_full
        """
        if self.args.one_way:
            self.flights_full = [fl for fl in self.flights[0]
                                 if unicode(fl[-1]) != u' \u2014 ']
        else:
            for o_fl in self.flights[0]:
                for r_fl in self.flights[1]:
                    if unicode(o_fl[-1]) != u' \u2014 ' and\
                                    unicode(r_fl[-1]) != u' \u2014 ':
                        self.flights_full.append(o_fl + ['  '] +
                                                 r_fl + ['  '] +
                                                 [self.currency,
                                                  str(float(o_fl[-1]) +
                                                      float(r_fl[-1]))])

    def sort(self):
        """ Сортировка по возрастанию стоимости перелета. """
        self.flights_full.sort(key=lambda j: float(j[-1]), reverse=False)

    def __str__(self):
        """ Формирую заголовок таблицы и вывожу рейсы на
        экран в наглядном виде.
        :return: flights_str"""
        if self.args.one_way:
            head = 'Outbound ' \
                   'flight:{}'.format(self.outbound_data.encode('utf-8'))
        else:
            head = 'Outbound flight:{}\nReturn flight:{}\n' \
                   'Outbound flight{}Return flight{}Total ' \
                   'price'.format(self.outbound_data.encode('utf-8'),
                                  self.return_data.encode('utf-8'),
                                  ' '*(len(' '.join(self.flights[0][0]))-11),
                                  ' '*(len(' '.join(self.flights[1][0]))-9))
        flights_str = '\n'.join([' '.join(fl) for fl in self.flights_full])
        return '{}\n{}'.format(head, flights_str.encode('utf-8'))
