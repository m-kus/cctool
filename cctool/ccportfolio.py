import logging
from datetime import datetime
from pprint import pformat
from typing import List

from cctool.ccapi import get_portfolios, delete_portfolio, open_position, \
    close_position, delete_position, get_prices

logger = logging.getLogger('cctool')


class MemberAlreadyExists(Exception):
    pass


class MemberNotFound(Exception):
    pass


class CCPortfolio:

    def __init__(self, session: dict, coins: dict, portfolio: dict):
        self.session = session
        self.coins = coins
        self.portfolio = portfolio

    def __repr__(self):
        return pformat(self.portfolio)

    def __getitem__(self, item):
        return self.portfolio[item]

    def refresh(self):
        portfolios = get_portfolios(self.session['AuthKey'])
        self.portfolio = next(x for x in portfolios if x['Id'] == self.portfolio['Id'])

    def iter_member_lists(self, include_sold=False):
        keys = ['Members', 'MembersCollapsed']
        if include_sold:
            keys.extend(['SoldMembers', 'SoldMembersCollapsed'])
        for key in keys:
            members = self.portfolio.get(key)
            if members:
                yield members

    def iter_members(self, include_sold=False):
        for members in self.iter_member_lists(include_sold):
            for member in members:
                yield member

    def find_member(self, comment):
        for member in self.iter_members(include_sold=True):
            if member['Sold']:
                description = member['SoldDescription']
            else:
                description = member['Description']
            if description == comment:
                return member

    def delete_member(self, member):
        for members in self.iter_member_lists(include_sold=True):
            if member in members:
                members.remove(member)

    def get_positions(self) -> List[dict]:
        return list(self.iter_members())

    def find_positions(self, symbol, exchange=''):
        for member in self.iter_members():
            if exchange and member['ExchangeName'] != exchange:
                continue
            if member['Coin']['Symbol'] == symbol:
                yield member

    def delete_all_positions(self):
        for member in self.iter_members(include_sold=True):
            delete_position(self.session['AuthKey'], member['Id'])
        self.refresh()

    def delete(self):
        return delete_portfolio(self.session['AuthKey'], self.portfolio['Id'])

    def open_position(self, symbol, amount, price=None, timestamp=None, comment='', exchange=''):
        if comment and self.find_member(comment):
            raise MemberAlreadyExists(comment)

        if price is None:
            price = get_prices(symbol, timestamp=timestamp)[symbol]
        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp())

        member = open_position(
            auth_key=self.session['AuthKey'],
            portfolio_id=self.portfolio['Id'],
            coin_id=self.coins[symbol]['Id'],
            amount=amount,
            price=price,
            timestamp=timestamp,
            comment=comment,
            exchange=exchange
        )
        self.portfolio['Members'].append(member)

    def close_position(self, symbol, price=None, timestamp=None, amount=None, comment='', exchange=''):
        if comment and self.find_member(comment):
            raise MemberAlreadyExists(comment)

        if price is None:
            price = get_prices(symbol, timestamp=timestamp)[symbol]
        if timestamp is None:
            timestamp = int(datetime.utcnow().timestamp())

        for position in self.find_positions(symbol, exchange):  # FIFO
            if amount:
                sold_amount = min(position['Amount'], amount)
            else:
                sold_amount = position['Amount']

            sold_member = close_position(
                auth_key=self.session['AuthKey'],
                position_id=position['Id'],
                amount=sold_amount,
                price=price,
                timestamp=timestamp,
                comment=comment
            )
            self.portfolio['SoldMembers'].append(sold_member)

            if sold_member['ActionType'] == 'Full':
                self.delete_member(position)
            else:
                position['Amount'] -= sold_amount

            if amount:
                amount -= sold_amount
                if amount == 0:
                    return

        if amount and amount > 0:
            raise MemberNotFound(symbol)

    def import_trades(self, trades: List[dict], ignore_errors=None):
        for trade in trades:
            try:
                if trade.pop('direction') == 'buy':
                    self.open_position(**trade)
                else:
                    self.close_position(**trade)
            except (MemberNotFound, MemberAlreadyExists) as e:
                if ignore_errors:
                    logger.error('{}: {}', type(e), str(e))
                else:
                    logger.exception('', exc_info=True)
                    return
