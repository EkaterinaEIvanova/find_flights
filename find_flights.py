# -*- coding: utf-8 -*-
""" Получение с cmd необходимых параметров, проверка на корректность введенной
даты и получение в соотвествии с параметрами всевозможных вариантов рейсов
библиотеки Finding"""
import argparse
from datetime import datetime, date

from library_find import FindingFlights


def create_args(args):
    args.sourceIATA = args.sourceIATA or args.sIATA
    args.destinationIATA = args.destinationIATA or args.dIATA
    args.outbound_date = args.outbound_date or args.odate
    args.return_date = args.return_date or args.rdate


def inspect_date(args):
    """
    Проверяю правильность введенных дат.
    :param args
    :return: True/False
    """
    print args, date.today()
    if args.outbound_date.date() >= date.today():
        if args.return_date:
            if args.return_date >= args.outbound_date:
                args.return_date = args.return_date.strftime('%Y-%m-%d')
                args.outbound_date = args.outbound_date.strftime('%Y-%m-%d')
                args.one_way = ''
                return True
            else:
                print 'Return_date is not correct. Enter correct date.'
                return False
        else:
            args.outbound_date = args.outbound_date.strftime('%Y-%m-%d')
            args.return_date = args.outbound_date
            args.one_way = 'on'
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
    parser.add_argument('odate', type=lambda d: datetime.strptime(d, '%Y-%m-%d'), nargs='?')
    parser.add_argument('rdate', type=lambda d: datetime.strptime(d, '%Y-%m-%d'), nargs='?')
    parser.add_argument('-sIATA', '--sourceIATA', type=str,
                        help='Source airport IATA code')
    parser.add_argument('-dIATA', '--destinationIATA',type=str,
                        help='Destination airport IATA code')
    parser.add_argument('-odate', '--outbound_date', type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        help='Outbound date, format YYYY-MM-DD')
    parser.add_argument('-rdate', '--return_date', type=lambda d: datetime.strptime(d, '%Y-%m-%d'),
                        help='Return date, format YYYY-MM-DD')
    args = parser.parse_args()
    create_args(args)

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


if __name__ == "__main__":
    main()
