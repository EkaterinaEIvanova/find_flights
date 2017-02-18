import argparse
from iata_codes import IATACodesClient

from library_find import Finding


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-iIATA', type=str, help='')
    parser.add_argument('-oIATA', type=str, help='')
    parser.add_argument('-idata', type=str, help='')
    parser.add_argument('-odata', type=str, help='')

    args = parser.parse_args()
    client = IATACodesClient('BER')
    print(client.get(name='Moscow'))
   # f = Finding(args)

if __name__ == "__main__":
    main()
