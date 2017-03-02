# -*- coding: utf-8 -*-
""" Получение с cmd необходимых параметров, проверка на корректность введенной
даты и получение в соотвествии с параметрами всевозможных вариантов рейсов
библиотеки Finding"""
import argparse
from datetime import datetime, date

from library_find import FindingFlights


def create_args(args):
    """
    Генерирую args если все элементы введены в cmd
    :param args
    :return: True/False
    """
    args.sourceIATA = args.sourceIATA or args.sIATA
    if not args.sourceIATA:
        print 'No source IATA. Enter correct IATA.'
        return False
    args.destinationIATA = args.destinationIATA or args.dIATA
    if not args.destinationIATA:
        print 'No destination IATA. Enter correct IATA.'
        return False
    args.outbound_date = args.outbound_date or args.odate
    if not args.outbound_date:
        print 'No outbound date. Enter correct outbound date.'
        return False
    if args.return_date:
        args.return_date = args.return_date or args.rdate
        args.one_way = ''
    else:
        args.return_date = args.outbound_date
        args.one_way = 'on'
    return True


def inspect_date(args):
    """
    Проверяю корректность введенных дат.
    :param args
    :return: True/False
    """
    if args.outbound_date.date() >= date.today() \
            and args.return_date >= args.outbound_date:
        args.return_date = args.return_date.strftime('%Y-%m-%d')
        args.outbound_date = args.outbound_date.strftime('%Y-%m-%d')
        return True
    else:
        print 'Outbound_date is not correct. Enter correct date.'
        return False


def main():
    """
    Получаю входные параметры с cmd, проверяю их на корректность и при наличии
    получаю набор рейсов соотвествующий параметрам.
    :param args: sIATA, dIATA, o_date, r_date
    :return: str
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('sIATA', type=str, nargs='?')
    parser.add_argument('dIATA', type=str, nargs='?')
    parser.add_argument('odate',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        nargs='?')
    parser.add_argument('rdate',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        nargs='?')
    parser.add_argument('-sIATA', '--sourceIATA',
                        type=str,
                        help='Source airport IATA code')
    parser.add_argument('-dIATA', '--destinationIATA',
                        type=str,
                        help='Destination airport IATA code')
    parser.add_argument('-odate', '--outbound_date',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        help='Outbound date, format YYYY-MM-DD')
    parser.add_argument('-rdate', '--return_date',
                        type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        help='Return date, format YYYY-MM-DD')
    args = parser.parse_args()

    if create_args(args) and inspect_date(args):
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
            print "Source IATA {} or destination IATA {} no found. " \
                  "Enter correct IATAs." .format(args.sourceIATA,
                                                 args.destinationIATA)


if __name__ == "__main__":
    main()
