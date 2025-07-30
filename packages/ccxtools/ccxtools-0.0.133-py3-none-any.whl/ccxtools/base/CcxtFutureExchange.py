from ccxt.base.decimal_to_precision import decimal_to_precision, TRUNCATE
from ccxtools.base.CcxtExchange import CcxtExchange
from ccxtools.base.FutureExchange import FutureExchange


class CcxtFutureExchange(CcxtExchange, FutureExchange):

    def __init__(self, env_vars):
        FutureExchange.__init__(self, env_vars)
        CcxtExchange.__init__(self, env_vars)

    def get_contract_sizes(self):
        raise NotImplementedError

    def get_position(self, ticker):
        raise NotImplementedError

    def post_market_order(self, ticker, side, open_close, amount):
        raise NotImplementedError

    def get_precise_order_amount(self, ticker, ticker_amount):
        contract_size = self.contract_sizes[ticker]
        precision = self.ccxt_inst.precision_from_string(str(contract_size))

        return float(decimal_to_precision(ticker_amount, TRUNCATE, precision))
