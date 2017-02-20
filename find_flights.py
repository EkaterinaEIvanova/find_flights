# -*- coding: utf-8 -*-
import argparse
from datetime import datetime
from iata_codes.cities import IATACodesClient

from library_find import Finding


def inspect_data(args):
    """
    Проверяю правильность введенных IATA кодов, и дат. Если IATA верны сопоставляю им полное название аэропортов.
    :param args:
    :return: True/False
    """
    client = IATACodesClient('15be9538-c84a-465d-b82d-6d668e7f1b4e')
    try:
        args.source_name = client.get(code=args.sourceIATA)[0][u'name']
        args.destin_name = client.get(code=args.destinationIATA)[0][u'name']
    except LookupError:
        print ('IATA-code is not correct. Enter correct code.')
        return False
    try:
        datetime.strptime(args.outbound_date, '%Y-%m-%d')
        if args.return_date:
            datetime.strptime(args.return_date, '%Y-%m-%d')
    except ValueError:
        print ('Incorrect date format. Please, enter the date in the format Y-M-D')
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-sIATA', '--sourceIATA', type=str, required=True, help='IATA source airport code')
    parser.add_argument('-dIATA', '--destinationIATA', type=str, required=True, help='IATA destination airport code')
    parser.add_argument('-odate', '--outbound_date', type=str, required=True, help='Outbound date, format Y-M-D',)
    parser.add_argument('-rdate', '--return_date', type=str, help='Return date, format Y-M-D')
    args = parser.parse_args()

    if inspect_data(args):
        f = Finding(args)
        f.get_flights()
        print(f)

if __name__ == "__main__":
    main()
