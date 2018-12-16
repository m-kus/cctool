import logging
import getpass
from argparse import ArgumentParser

from cctool.loaders import autoload
from cctool.ccsession import CCSession

logger = logging.getLogger('cctool')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = ArgumentParser()
    parser.add_argument('filename', help='Path to the order/trade history in csv format')
    parser.add_argument('-p', '--portfolio', help='Portfolio name, full or partial')
    parser.add_argument('-i', '--ignore-errors', help='Ignore import errors', action='store_true',
                        default=False)
    args = parser.parse_args()

    trades = autoload(args.filename)
    email = input('Email for CryptoCompare.com:\n')
    password = getpass.getpass('Password for CryptoCompare.com [{}]:\n'.format(email))

    with CCSession(email, password) as ccs:
        if args.portfolio:
            portfolio = ccs.find_portfolio(args.portfolio)
        else:
            portfolio = ccs.create_portfolio('New portfolio')
            logger.warning('Portfolio name is not specified, using default')
        portfolio.import_trades(trades, args.ignore_errors)
