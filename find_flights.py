# -*- coding: utf-8 -*-
""" Получение с cmd необходимых параметров, проверка на корректность введенной
даты и получение в соотвествии с параметрами всевозможных вариантов рейсов
библиотеки Finding"""
import argparse
from datetime import datetime

from library_find import FindingFlights


def inspect_date(args):
    """
    Проверяю правильность введенных дат.
    :param args
    :return: True/False
    """
    try:
        args.outbound_date = datetime.strptime(args.outbound_date, '%Y-%m-%d')
        if args.return_date:
            args.return_date = datetime.strptime(args.return_date, '%Y-%m-%d')
            args.one_way = ''
        else:
            args.return_date = args.outbound_date
            args.one_way = 'on'
    except ValueError:
        print 'Incorrect date format. Please, enter the correct date in ' \
              'the format YYYY-MM-DD.'
        return False
    return True


def main():
    """
    Получаю входные параметры с cmd, проверяю их на корректность и при наличии
    получаю набор рейсов соотвествующий параметрам.
    :param args: sIATA, dIATA, o_date, r_date
    :return: str
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-sIATA', '--sourceIATA', type=str, required=True,
                        help='Source airport IATA code')
    parser.add_argument('-dIATA', '--destinationIATA', type=str, required=True,
                        help='Destination airport IATA code')
    parser.add_argument('-odate', '--outbound_date', type=str, required=True,
                        help='Outbound date, format YYYY-MM-DD',)
    parser.add_argument('-rdate', '--return_date', type=str,
                        help='Return date, format YYYY-MM-DD')
    args = parser.parse_args()

    if inspect_date(args):
        find_fl = FindingFlights(args)
        if find_fl.args.source_name and find_fl.args.destination_name:
            find_fl.get_content()
            if find_fl.content:
                find_fl.get_flights()
                find_fl.get_flights_full()
                find_fl.sort()
                print find_fl
            else:
                print "Couldn't find flights from {}({}) to {}({}) on" \
                      " {}/{}".format(
                          find_fl.args.source_name,
                          args.sourceIATA,
                          find_fl.args.destination_name,
                          args.destinationIATA,
                          args.outbound_date,
                          args.return_date, )
        else:
            print 'IATA-code is not correct. Enter correct code.'


if __name__ == "__main__":
    main()
