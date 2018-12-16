import logging
import numpy as np
import pandas as pd
from pandas.errors import ParserError
from decimal import Decimal
from typing import List

logger = logging.getLogger('cctool')
deprecated_symbols = {
    'STR': 'XLM',
    'BCC': 'BCH'
}


def get_symbol(symbol):
    return deprecated_symbols.get(symbol, symbol)


def aggregate_trades(df: pd.DataFrame, scale) -> pd.DataFrame:
    return df.groupby(['comment', 'exchange', 'direction', 'symbol'], as_index=False).agg(dict(
        timestamp='first',
        amount='sum',
        price=lambda x: np.average(x, weights=df.loc[x.index, "amount"]).quantize(scale)
    ))


def load_poloniex_trades(filename, scale=Decimal('0.00000001')) -> List[dict]:
    df = pd.read_csv(filename, dtype=str)
    df['exchange'] = 'Poloniex'
    df['comment'] = df['Order Number'].apply(lambda x: 'Order #{}'.format(x))
    df['symbol'] = df['Market'].apply(lambda x: get_symbol(x.split('/')[0]))
    df['direction'] = df['Type'].apply(lambda x: x.lower())
    df['timestamp'] = pd.to_datetime(df['Date']).astype('int64') // 1000000000
    df['amount'] = df['Quote Total Less Fee'].apply(lambda x: abs(Decimal(x).quantize(scale)))
    df['price'] = df.apply(
        lambda x: (abs(Decimal(x['Base Total Less Fee'])) / x['amount']).quantize(scale),
        axis=1
    )
    df = aggregate_trades(df, scale).sort_values(by='timestamp')
    trades = df.to_dict('records')
    return trades


def load_bittrex_trades(filename, scale=Decimal('0.00000001')) -> List[dict]:
    df = pd.read_csv(filename, dtype=str, encoding='utf_16_le', engine='python')
    df['exchange'] = 'Bittrex'
    df['comment'] = df['OrderUuid'].apply(lambda x: 'Order #{}'.format(x))
    df['symbol'] = df['Exchange'].apply(lambda x: get_symbol(x.split('-')[1]))
    df['direction'] = df['Type'].apply(lambda x: x.split('_')[1].lower())
    df['timestamp'] = pd.to_datetime(df['Opened']).astype('int64') // 1000000000
    df['amount'] = df['Quantity'].apply(lambda x: Decimal(x))
    df['fee'] = df.apply(
        lambda x: Decimal(x['ComissionPaid']) * (1 if x['direction'] == 'buy' else -1),
        axis=1
    )
    df['price'] = df.apply(
        lambda x: ((Decimal(x['Price']) + x['fee']) / x['amount']).quantize(scale),
        axis=1
    )
    df = aggregate_trades(df, scale).sort_values(by='timestamp')
    trades = df.to_dict('records')
    return trades


def autoload(filename) -> List[dict]:
    loaders = [
        load_poloniex_trades,
        load_bittrex_trades
    ]
    for loader in loaders:
        try:
            trades = loader(filename)
        except (KeyError, UnicodeDecodeError, ParserError):
            continue
        else:
            if trades:
                logger.info('{} trades loaded from {}'.format(len(trades), trades[0]['exchange']))
            else:
                raise ValueError('No trades loaded')
            return trades

    raise NotImplementedError
