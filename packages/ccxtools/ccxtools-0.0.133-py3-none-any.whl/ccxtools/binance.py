import ccxt

from ccxtools.base.CcxtFutureExchange import CcxtFutureExchange
from ccxtools.tools import get_async_results


class Binance(CcxtFutureExchange):

    def __init__(self, who, env_vars, extra_config):
        super().__init__(env_vars)

        config = dict({
            'apiKey': env_vars(f'BINANCE_API_KEY{who}'),
            'secret': env_vars(f'BINANCE_SECRET_KEY{who}')
        }, **extra_config)

        self.ccxt_inst = ccxt.binance(config)

    def is_transferring(self):
        has_disabled_rate_limit = False
        if self.ccxt_inst.enableRateLimit:
            self.ccxt_inst.enableRateLimit = False
            has_disabled_rate_limit = True

        [deposits, withdrawals] = get_async_results([
            {'func': self.ccxt_inst.fetch_deposits},
            {'func': self.ccxt_inst.fetch_withdrawals},
        ])

        if has_disabled_rate_limit:
            self.ccxt_inst.enableRateLimit = True

        for transfer in [*deposits, *withdrawals]:
            if transfer['status'] == 'pending':
                return True

        return False

    def post_withdraw(self, ticker, amount, destination):
        address = self.env_vars(f'{destination}_{ticker}_ADDRESS')
        tag = self.env_vars(f'{destination}_{ticker}_TAG') if ticker in self.WITHDRAW_TAG_NECESSARY_TICKERS else None

        self.ccxt_inst.withdraw(ticker, amount, address, tag)
