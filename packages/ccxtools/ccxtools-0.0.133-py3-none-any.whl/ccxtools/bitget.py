import time
import ccxt
from ccxtools.base.CcxtFutureExchange import CcxtFutureExchange


class Bitget(CcxtFutureExchange):

    def __init__(self, who, env_vars):
        super().__init__(env_vars)

        self.ccxt_inst = ccxt.bitget({
            'apiKey': env_vars(f'BITGET_API_KEY{who}'),
            'secret': env_vars(f'BITGET_SECRET_KEY{who}'),
            'password': env_vars(f'BITGET_PASSWORD{who}'),
            'options': {
                'defaultType': 'swap',
                'fetchMarkets': ['swap'],
            },
        })
        self.contract_sizes = self.get_contract_sizes()

    def get_contracts(self):
        contracts = []
        for contract in self.ccxt_inst.fetch_markets():
            if not contract['active'] or contract['future'] or not contract['linear'] or contract['settle'] != 'USDT':
                continue

            contracts.append(contract)

        return contracts

    def get_funding_rates(self):
        contracts = self.ccxt_inst.public_mix_get_mix_v1_market_tickers({
            'productType': 'UMCBL'
        })['data']

        funding_rates = {}
        for contract in contracts:
            ticker = contract['symbol'][:contract['symbol'].find('USDT_')]
            funding_rates[ticker] = float(contract['fundingRate'])

        return funding_rates

    def get_contract_sizes(self):
        sizes = {}
        for contract in self.get_contracts():
            sizes[contract['base']] = contract['precision']['amount']

        return sizes

    def get_balance(self, ticker):
        datas = self.ccxt_inst.fetch_balance()['info']
        for data in datas:
            if data['marginCoin'] == ticker:
                return float(data['usdtEquity'])
        return 0

    def get_position(self, ticker):
        res = self.ccxt_inst.fetch_position(f'{ticker}USDT')
        abs_size = res['contracts']
        if abs_size is None:
            return 0.0
        return abs_size if res['side'] == 'long' else -abs_size

    def post_market_order(self, ticker, side, open_close, amount):
        symbol = f'{ticker}USDT'
        res = self.ccxt_inst.create_market_order(symbol, side, amount, params={
            'reduceOnly': open_close == 'close',
        })

        for i in range(10):
            try:
                order = self.ccxt_inst.fetch_order(res['id'], symbol)
                if order['status'] == 'open':
                    time.sleep(0.1)
                    continue

                return order['average']
            except Exception as error:
                if i < 9:
                    time.sleep(0.1)
                    continue

                raise error

        raise Exception('order not filled')
