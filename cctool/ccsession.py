from typing import List
from pprint import pformat

from cctool.ccapi import create_session, destroy_session, get_portfolios, get_coins, create_portfolio
from cctool.ccportfolio import CCPortfolio


class CCSession:

    def __init__(self, email=None, password=None):
        self.coins = get_coins()
        self.session = dict()
        self.email = email
        self.password = password

    def __repr__(self):
        return pformat(self.session)

    def __enter__(self):
        return self.login(self.email, self.password)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logout()

    def login(self, email, password):
        self.session = create_session(email, password)
        return self

    def logout(self):
        if self.session:
            destroy_session(self.session['AuthKey'])

    def get_portfolios(self) -> List[CCPortfolio]:
        return [
            CCPortfolio(self.session, self.coins, portfolio)
            for portfolio in get_portfolios(self.session['AuthKey'])
        ]

    def find_portfolio(self, part_name) -> CCPortfolio:
        portfolios = get_portfolios(self.session['AuthKey'])
        portfolio = next(x for x in portfolios if part_name.lower() in x['Name'].lower())
        return CCPortfolio(self.session, self.coins, portfolio)

    def create_portfolio(self, name, description='') -> CCPortfolio:
        portfolio = create_portfolio(
            auth_key=self.session['AuthKey'],
            name=name,
            description=description
        )
        return CCPortfolio(self.session, self.coins, portfolio)
