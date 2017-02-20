import argparse

from library_find import Finding
from iata_codes.cities import IATACodesClient

def inspect_data(args):
    client = IATACodesClient('15be9538-c84a-465d-b82d-6d668e7f1b4e')
    iiata = client.get(code=args.iIATA)
    oiata = client.get(code=args.oIATA)

    if iiata and oiata:
        args.i_name = iiata[0][u'name']
        args.o_name = oiata[0][u'name']

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-iIATA', type=str, help='')
    parser.add_argument('-oIATA', type=str, help='')
    parser.add_argument('-idata', type=str, help='')
    parser.add_argument('-odata', type=str, help='')

    args = parser.parse_args()

    inspect_data(args)
    f = Finding(args)
    f.get_flights()
    f.sort()
    print(f)

if __name__ == "__main__":
    main()
