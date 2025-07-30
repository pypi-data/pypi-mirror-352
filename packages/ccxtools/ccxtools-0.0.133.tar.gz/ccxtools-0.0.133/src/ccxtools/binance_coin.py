from ccxtools.binance import Binance


class BinanceCoin(Binance):

    def __init__(self, who, env_vars):
        super().__init__(who, env_vars, {
            'options': {
                'defaultType': 'delivery',
                'fetchMarkets': ['inverse']
            }
        })

    def get_mark_price(self, ticker):
        return float(self.ccxt_inst.dapiPublicGetPremiumIndex({'symbol': f'{ticker}USD_PERP'})[0]['markPrice'])

    def get_mark_prices(self, tickers):
        price_datas = self.ccxt_inst.dapiPublicGetPremiumIndex()
        mark_prices = {}

        for price_data in price_datas:
            ticker = price_data['symbol'].replace('USD_PERP', '')
            if ticker in tickers:
                mark_prices[ticker] = float(price_data['markPrice'])
                if len(mark_prices.keys()) == len(tickers):
                    break

        return mark_prices

    def get_best_book_price(self, ticker, side):
        best_book_price_data = self.ccxt_inst.dapiPublicGetDepth({'symbol': f'{ticker}USD_PERP'})[f'{side}s'][0]
        return float(best_book_price_data[0])

    def get_contract_size(self, ticker):
        markets = self.ccxt_inst.dapiPublicGetExchangeInfo()['symbols']
        ticker_market = list(filter(lambda x: x['symbol'] == f'{ticker}USD_PERP', markets))[0]
        return float(ticker_market['contractSize'])

    def get_balance(self, ticker):
        return self.ccxt_inst.fetch_balance()['total'][ticker]

    def get_spot_balances(self, tickers):
        all_balances = self.ccxt_inst.sapiv3_post_asset_getuserasset()

        result = {}
        for ticker in tickers:
            filtered = list(filter(lambda balance: balance['asset'] == ticker, all_balances))
            result[ticker] = float(list(filtered)[0]['free']) if filtered else 0
        return result

    def get_position(self, ticker):
        data = list(filter(lambda position: 'PERP' in position['symbol'],
                           self.ccxt_inst.dapiPrivateGetPositionRisk({'pair': f'{ticker}USD'})))[0]
        contract_size = self.get_contract_size(ticker)
        return float(data['positionAmt']) * contract_size

    def post_market_order(self, ticker, side, open_close, amount):
        """
        :param ticker: <String>
        :param side: <Enum: "buy" | "sell">
        :param open_close: <Enum: "open" | "close">
        :param amount: <Float | Int>
        :return: <Float> average filled price
        """
        trade_info = self.ccxt_inst.create_market_order(f'{ticker}USD_PERP', side, amount // 10)
        return trade_info['average']
