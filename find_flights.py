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
    args.sourceIATA = args.sIATA or args.sourceIATA
    if not (args.sourceIATA and args.sourceIATA.isalpha()):
        print 'No correct source IATA. Enter correct IATA.'
        return False
    args.destinationIATA = args.dIATA or args.destinationIATA
    if not (args.destinationIATA and args.destinationIATA.isalpha()):
        print 'No correct destination IATA. Enter correct IATA.'
        return False
    args.outbound_date = args.odate or args.outbound_date
    if not args.outbound_date:
        print 'No correct outbound date. Enter correct outbound date.'
        return False
    args.return_date = args.rdate or args.return_date
    if args.return_date:
        args.one_way = ''
        return True
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
        find_fl.get_content()
        if find_fl.content:
            find_fl.get_flights()
            find_fl.get_flights_full()
            find_fl.sort()
            print find_fl
        else:
            print "Couldn't find flights from {} to {} on" \
                  " {}/{}".format(
                      args.sourceIATA,
                      args.destinationIATA,
                      args.outbound_date,
                      args.return_date, )


if __name__ == "__main__":
    main()
