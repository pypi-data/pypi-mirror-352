import ccxt
from ccxtools.base.CcxtFutureExchange import CcxtFutureExchange


class Bingx(CcxtFutureExchange):
    BASE_URL = 'https://api-swap-rest.bingx.com/api/v1'

    def __init__(self, who, env_vars):
        super().__init__(env_vars)
        self.ccxt_inst = ccxt.bingx({
            'apiKey': env_vars(f'BINGX_API_KEY{who}'),
            'secret': env_vars(f'BINGX_SECRET_KEY{who}'),
            'options': {
                'defaultType': 'swap'
            }
        })
        self.contract_sizes = self.get_contract_sizes()

    def get_last_prices(self):
        """
        :return: {
            'BTC': 20000.0,
            'ETH': 1000.0,
            ...
        }
        """
        last_prices = {}

        datas = self.ccxt_inst.swap_v2_public_get_quote_ticker()['data']

        for data in datas:
            last_price = float(data['lastPrice'])
            if last_price == 0:
                continue

            ticker = data['symbol'].replace('-USDT', '')
            last_prices[ticker] = last_price
        return last_prices

    def get_last_price(self, ticker: str) -> float:
        last_prices = self.get_last_prices()
        return last_prices[ticker]

    def get_funding_rates(self):
        data_list = self.ccxt_inst.swap_v2_public_get_quote_premiumindex()['data']

        if len(data_list) == 0:
            raise Exception('No funding rate data')

        funding_rates = {}
        for rate_data in data_list:
            ticker = rate_data['symbol'][:rate_data['symbol'].find('-')]
            funding_rates[ticker] = float(rate_data['lastFundingRate'])

        return funding_rates

    def get_contract_sizes(self):
        """
        :return: {
            'BTC': 0.1,
            'ETH': 0.01,
            ...
        }
        """
        sizes = {}

        datas = self.ccxt_inst.swap_v2_public_get_quote_contracts()['data']
        for data in datas:
            quantity_size = 10 ** (-int(data['quantityPrecision']))
            sizes[data['asset']] = quantity_size

        return sizes

    def get_balance(self, ticker):
        """
        :param ticker: <String> ticker name. ex) 'USDT', 'BTC'
        :return: <Int> balance amount
        """
        if ticker != 'USDT':
            raise Exception

        data = self.ccxt_inst.swap_v2_private_get_user_balance()['data']['balance']
        return float(data['equity'])

    def get_position(self, ticker: str) -> float:
        total = 0

        positions = self.ccxt_inst.swap_v2_private_get_user_positions({
            'symbol': f'{ticker}-USDT',
        })['data']

        for position in positions:
            absolute_amount = float(position['positionAmt'])
            if position['positionSide'] == 'LONG':
                total += absolute_amount
            else:
                total -= absolute_amount
        return total

    def post_market_order(self, ticker, side, open_close, amount):
        """
        :param ticker: <String>
        :param side: <Enum: "buy" | "sell">
        :param open_close: <Enum: "open" | "close">
        :param amount: <Float | Int>
        :return: <Float> average filled price
        """
        symbol = f'{ticker}-USDT'

        res = self.ccxt_inst.swap_v2_private_post_trade_order({
            'symbol': symbol,
            'side': side.upper(),
            'positionSide': 'BOTH',
            'type': 'MARKET',
            'quantity': amount,
        })

        try:
            order_id = res['data']['order']['orderId']
        except:
            raise Exception(res)
        order_info = self.ccxt_inst.swap_v2_private_get_trade_order({
            'symbol': symbol,
            'orderId': order_id,
        })['data']['order']
        return float(order_info['avgPrice'])
