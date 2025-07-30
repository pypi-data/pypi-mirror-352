from ccxtools.binance import Binance


class BinanceUsdt(Binance):

    def __init__(self, who, env_vars):
        super().__init__(who, env_vars, {
            'options': {
                'defaultType': 'future',
                'fetchMarkets': ['linear']
            }
        })
        self.contract_sizes = self.get_contract_sizes()

    def get_contracts(self):
        all_contracts = self.ccxt_inst.fetch_markets()

        usdt_contracts = []
        for contract in all_contracts:
            info = contract['info']

            if info['contractType'] != 'PERPETUAL' or info['marginAsset'] != 'USDT' or info['status'] != 'TRADING':
                continue

            usdt_contracts.append(contract)

        return usdt_contracts

    def get_mark_price(self, ticker):
        return float(self.ccxt_inst.fapiPublicGetPremiumIndex({'symbol': f'{ticker}USDT'})['markPrice'])

    def get_best_book_price(self, ticker, side):
        best_book_price_data = self.ccxt_inst.fapiPublicGetDepth({'symbol': f'{ticker}USDT'})[f'{side}s'][0]
        return float(best_book_price_data[0])

    def get_funding_rates(self):
        res = self.ccxt_inst.fetch_funding_rates()
        funding_rates = {}

        for symbol, data in res.items():
            if symbol[-10:] != '/USDT:USDT':
                continue

            ticker = symbol[:-10]
            funding_rates[ticker] = data['fundingRate']

        return funding_rates

    def get_contract_size(self, ticker):
        return self.contract_sizes[ticker]

    def get_contract_sizes(self):
        """
        :return: {
            'BTC': 0.1,
            'ETH': 0.01,
            ...
        }
        """
        sizes = {}
        for market in self.get_contracts():
            ticker = market['base']
            for fil in market['info']['filters']:
                if fil['filterType'] == 'LOT_SIZE':
                    size = float(fil['stepSize'])

            sizes[ticker] = size

        return sizes

    def get_max_trading_qtys(self):
        """
        :return: {
            'BTC': 120,
            'ETH': 2000,
            ...
        """
        qtys = {}
        for market in self.get_contracts():
            ticker = market['base']
            max_qty = list(filter(lambda x: x['filterType'] == 'MARKET_LOT_SIZE', market['info']['filters']))[0][
                'maxQty']

            qtys[ticker] = float(max_qty)

        return qtys

    def get_max_position_qtys(self):
        """
        :return: {
            'BTC': 20000000,
            'ETH': 5000000,
            ...
        }
        """
        positions = self.ccxt_inst.fapiprivatev2_get_account()['positions']

        qtys = {}
        for position in positions:
            symbol = position['symbol']
            if symbol[-4:] == 'USDT':
                ticker = symbol.replace('USDT', '')
                qtys[ticker] = int(position['maxNotional'])
        return qtys

    def get_balance(self, ticker):
        return super().get_balance(ticker)

    def get_position(self, ticker):
        return float(self.ccxt_inst.fapiprivatev2_get_positionrisk({'symbol': f'{ticker}USDT'})[0]['positionAmt'])

    def post_market_order(self, ticker, side, open_close, amount):
        """
        :param ticker: <String>
        :param side: <Enum: "buy" | "sell">
        :param open_close: <Enum: "open" | "close">
        :param amount: <Float | Int>
        :return: <Float> average filled price
        """
        if open_close == 'open':
            extra_params = {}
        elif open_close == 'close':
            extra_params = {'reduceOnly': 'true'}

        trade_info = self.ccxt_inst.create_market_order(f'{ticker}USDT', side, amount, params=extra_params)
        return trade_info['average']
