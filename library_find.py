# -*- coding: utf-8 -*-
""" Библиотека для получение всевозможных вариантов рейсов
согласно ресурсу www.flyniki.com по заданным параметрам Пользоватаеля."""
import requests
from lxml import html


class FindingFlights(object):
    """ args(sIATA, dIATA, o_date, r_date) --> flights_str/error_str """
    def __init__(self, args):
        self.args = args
        self._url = ''
        self._headers = {'Content-Type': 'application/x-www-form-urlencoded',
                         'Cookie': 'ABSESS={}'.format(self._get_parametrs())}
        dct = self._get_airport()
        self.args.source_name = dct[self.args.sourceIATA]
        self.args.destination_name = dct[self.args.destinationIATA]
        self._get_airport()
        self.currency = ''
        self.content = []
        self.flights = []
        self.flights_full = []

    def _get_parametrs(self):
        """
        Делаю запрос для получение Cookie.ABSESS и url для основного запроса.
        :return:params{url, absess}
        """
        url = 'http://www.flyniki.com/en/booking/flight/vacancy.php'
        resp = requests.post(url)
        self._url = resp.request.url
        # Получаю из Cookie-строки значение ABSESS
        return resp.request.headers['Cookie'].split(' ')[1][7:-1]

    def _get_airport(self):
        """
        Делаю запрос на получение имени аэропортов соотвествующих введеным IATA
        :return:airports_name{airport_IATA: airport_names}
        """
        airports_name = {self.args.destinationIATA: '',
                         self.args.sourceIATA: ''}
        url = 'http://www.flyniki.com/en/site/json/suggestAirport.php'
        payload = {'searchfor': 'departures',
                   'searchflightid': '0',
                   'departures[]': ['', 'City, airport'],
                   'destinations[]': ['', 'City, airport'],
                   'suggestsource[0]': 'activeairports',
                   'withcountries': '0',
                   'withoutroutings': '0',
                   'promotion[id]': '',
                   'promotion[type]': '',
                   'get_full_suggest_list': 'true',
                   'routesource[0]': 'airberlin',
                   'routesource[1]': 'partner'}
        content = requests.post(url,
                                params=payload,
                                headers=self._headers).json()
        if content.get('fullSuggestList'):
            airports_name.update(
                {dct['code']: dct['name'] for dct in content.get('suggestList')
                 if dct['code'] == self.args.destinationIATA
                 or dct['code'] == self.args.sourceIATA})
        return airports_name

    def get_content(self):
        """
        Делаю http-запрос к сайту по исходным параметрам и получаю ответ.
        _url, _headers, data --> content
        """
        data = {'_ajax[templates][]':
                ['main', 'priceoverview', 'infos', 'flightinfo'],
                '_ajax[requestParams]'
                '[departure]': self.args.sourceIATA,
                '_ajax[requestParams]'
                '[destination]': self.args.destinationIATA,
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
        content = requests.post(self._url, headers=self._headers,
                                data=data).json()
        if content and content.get('templates'):
            # Если ресы в данную дату остувуют, то значение
            # content['templates']['priceoverview'] всегда пустое
            if content['templates']['priceoverview']:
                self.content = content['templates']['main']
                self.content = content['templates']['main']

    def get_flights(self):
        """
        Извлекаю необходимые данные по рейсам при наличии.
        content --> flights
        """
        if self.content:
            tree = html.fromstring(self.content)
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
                        price = row.xpath('./td[{}]/label/div[1]'
                                          '/span//text()'.format(i + 5))
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
        head = 'Outbound flight'
        if not self.args.one_way:
            head = 'Outbound flight{}Return flight{}Total ' \
                   'price'.format(' '*(len(' '.join(self.flights[0][0]))-11),
                                  ' '*(len(' '.join(self.flights[1][0]))-9))
        flights_str = '\n'.join([' '.join(fl) for fl in self.flights_full])
        return '{}\n{}'.format(head, flights_str.encode('utf-8'))
