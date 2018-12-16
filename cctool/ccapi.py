import re
import requests
import simplejson as json
from decimal import Decimal
from typing import List, Dict


class CryptoCompareError(Exception):
    pass


def api_call(url, method='POST', auth_key=None, **payload) -> dict:
    res = requests.request(
        url=url,
        method=method,
        json=payload,
        cookies=dict(
            auth_key=auth_key
        )
    )
    data = json.loads(res.text, use_decimal=True)
    if data.get('Response') != 'Success':
        raise CryptoCompareError(data.get('Message'))

    return data.get('Data')


def create_session(email, password) -> dict:
    session = api_call(
        url='https://auth-api.cryptocompare.com/cryptopian/login/web',
        email=email,
        password=password,
        referrer='https://www.cryptocompare.com/',
        campaign='N/A',
        reg_page='https://www.cryptocompare.com/',
        action='Dropdown Menu User Section'
    )
    return session


def destroy_session(auth_key):
    return api_call(
        url='https://auth-api.cryptocompare.com/cryptopian/logout',
        auth_key=auth_key,
        method='GET'
    )


def get_portfolios(auth_key) -> List[dict]:
    url = 'https://www.cryptocompare.com/portfolio/'
    res = requests.get(url, cookies=dict(auth_key=auth_key))
    matches = re.findall('setPortfolioData\((.+\})\);', res.text)
    data = json.loads(matches[0], use_decimal=True)
    return data['Data']


def get_coins() -> Dict[str, dict]:
    return api_call(
        url='https://www.cryptocompare.com/api/data/coinlist/',
        method='GET'
    )


def get_prices(*symbols, base_quote='BTC',
               timestamp=None, scale=Decimal('0.00000001')) -> Dict[str, Decimal]:
    prices = dict()

    def iter_chunks(chunks, max_length):
        max_chunk = str(chunks[0])
        for chunk in chunks:
            if len(max_chunk) + len(chunk) < max_length - 1:
                max_chunk += ',{}'.format(chunk)
            else:
                yield max_chunk
                max_chunk = chunk

        if max_chunk:
            yield max_chunk

    for tsyms in iter_chunks(symbols, max_length=30):
        url = 'https://min-api.cryptocompare.com/data/pricehistorical?fsym={}&tsyms={}'.format(
            base_quote, tsyms)
        if timestamp:
            url += '&ts={}'.format(timestamp)

        res = requests.get(url)
        data = json.loads(res.text, use_decimal=True)

        for symbol, price in data[base_quote].items():
            if price:
                prices[symbol] = (Decimal('1') / price).quantize(scale)
            else:
                prices[symbol] = Decimal()

    return prices


def create_portfolio(auth_key, name, description='', currency='BTC', access='Private') -> dict:
    return api_call(
        url='https://www.cryptocompare.com/api/portfolio/post/create/',
        auth_key=auth_key,
        name=name,
        description=description,
        currency=currency,
        access=access,
        encryption='Off'
    )


def delete_portfolio(auth_key, portfolio_id):
    return api_call(
        url='https://www.cryptocompare.com/api/portfolio/post/delete/',
        auth_key=auth_key,
        id=portfolio_id
    )


def open_position(auth_key, portfolio_id, coin_id, amount, price, timestamp,
                  comment='', base_quote='BTC', exchange='') -> dict:
    return api_call(
        url='https://www.cryptocompare.com/api/portfolio/post/coinadd/',
        auth_key=auth_key,
        portfolioId=portfolio_id,
        coinId=coin_id,
        amount=amount,
        buyPrice=price,
        boughtOnTs=timestamp,
        description=comment,
        buyCurrency=base_quote,
        storedIn='Exchange' if exchange else '',
        address='',
        walletName='',
        exchangeName=exchange
    )


def close_position(auth_key, position_id, amount, price, timestamp,
                   comment='', base_quote='BTC') -> dict:
    return api_call(
        url='https://www.cryptocompare.com/api/portfolio/post/coinsell/',
        auth_key=auth_key,
        id=position_id,
        sellAmount=amount,
        sellPrice=price,
        sellCurrency=base_quote,
        soldOnTs=timestamp,
        soldDescription=comment
    )


def delete_position(auth_key, position_id):
    return api_call(
        url='https://www.cryptocompare.com/api/portfolio/post/coindelete/',
        auth_key=auth_key,
        id=position_id
    )
