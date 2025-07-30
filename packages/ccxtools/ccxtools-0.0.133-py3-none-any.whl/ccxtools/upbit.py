import types
from random import randrange
import ccxt

from ccxtools.base.CcxtExchange import CcxtExchange
from ccxtools.tools import get_async_results


class Upbit(CcxtExchange):
    DEPOSIT_COMPLETE_STATUSES = ['ACCEPTED', 'CANCELLED', 'REJECTED', 'REFUNDED']
    WITHDRAWAL_COMPLETE_STATUSES = ['DONE', 'FAILED', 'CANCELLED', 'REJECTED']

    def __init__(self, who, env_vars):
        super().__init__(env_vars)
        self.ccxt_inst = ccxt.upbit({
            'apiKey': env_vars(f'UPBIT_API_KEY{who}'),
            'secret': env_vars(f'UPBIT_SECRET_KEY{who}')
        })
        self.ccxt_inst.nonce = types.MethodType(nonce, self.ccxt_inst)

        self.withdraw_net_types = {}
        self.withdraw_decimal_limits = {}

    def get_last_price(self, ticker):
        res = self.ccxt_inst.fetch_ticker(f'{ticker}/KRW')
        return res['last']

    def get_last_prices(self, tickers):
        ticker_datas = self.ccxt_inst.fetch_tickers([f'{ticker}/KRW' for ticker in tickers])
        return {ticker: ticker_datas[f'{ticker}/KRW']['last'] for ticker in tickers}

    def get_best_book_price(self, ticker, side):
        order_book = self.ccxt_inst.fetch_order_book(f'{ticker}/KRW')[f'{side}s']
        return order_book[0][0]

    def get_withdraw_net_type(self, ticker):
        if ticker in self.withdraw_net_types:
            return self.withdraw_net_types[ticker]

        datas = self.ccxt_inst.private_get_deposits_coin_addresses()
        for data in datas:
            if data['currency'] == ticker:
                self.withdraw_net_types[ticker] = data['net_type']
                return data['net_type']

        raise Exception(f"Can't find net_type for {ticker}")

    def get_withdraw_decimal_limits(self, tickers):
        not_in_tickers = filter(lambda ticker: ticker not in self.withdraw_decimal_limits, tickers)

        responses = get_async_results(
            {
                'func': self.ccxt_inst.private_get_withdraws_chance,
                'args': [{
                    'currency': ticker,
                    'net_type': self.get_withdraw_net_type(ticker)
                }]
            } for ticker in not_in_tickers
        )

        for i, ticker in enumerate(tickers):
            response = responses[i]
            self.withdraw_decimal_limits[ticker] = int(response['withdraw_limit']['fixed'])

        limits = {}
        for ticker in tickers:
            limits[ticker] = self.withdraw_decimal_limits[ticker]
        return limits

    def is_withdrawable(self, ticker):
        res = self.ccxt_inst.private_get_withdraws_chance({
            'currency': ticker,
            'net_type': self.get_withdraw_net_type(ticker)
        })
        return res['withdraw_limit']['can_withdraw']

    def is_transferring(self):
        [deposits, withdrawals] = get_async_results([
            {'func': self.ccxt_inst.fetch_deposits},
            {'func': self.ccxt_inst.fetch_withdrawals},
        ])

        for deposit in deposits:
            if deposit['info']['state'] not in self.DEPOSIT_COMPLETE_STATUSES:
                return True

        for withdrawal in withdrawals:
            if withdrawal['info']['state'] not in self.WITHDRAWAL_COMPLETE_STATUSES:
                return True

        return False

    def post_market_order(self, ticker, side, amount, price):
        res = self.ccxt_inst.create_order(f'{ticker}/KRW', 'market', side, amount, price)
        order_data = self.ccxt_inst.fetch_order(res['id'])
        return order_data['average']

    def post_withdraw(self, ticker, amount, destination):
        withdraw_decimal_limit = self.get_withdraw_decimal_limits([ticker])[ticker]
        fixed_amount = round(amount, withdraw_decimal_limit)

        address = self.env_vars(f'{destination}_{ticker}_ADDRESS')
        tag = self.env_vars(f'{destination}_{ticker}_TAG') if ticker in self.WITHDRAW_TAG_NECESSARY_TICKERS else None

        self.ccxt_inst.withdraw(ticker, fixed_amount, address, tag, {
            'net_type': self.get_withdraw_net_type(ticker)
        })


def nonce(self):
    return f'{self.milliseconds()}-{randrange(100, 999)}'
