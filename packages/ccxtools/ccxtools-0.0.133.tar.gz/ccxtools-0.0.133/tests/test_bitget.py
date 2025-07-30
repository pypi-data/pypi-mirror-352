import math
import pytest
from src.ccxtools.bitget import Bitget


@pytest.fixture
def bitget(env_vars):
    return Bitget('', env_vars)


def test_get_contracts(bitget):
    contracts = bitget.get_contracts()

    testing_tickes = ['BTC', 'ETH', 'XRP']
    tested = 0
    for contract in contracts:
        if contract['base'] in testing_tickes:
            tested += 1
            if tested == len(testing_tickes):
                break
    else:
        assert False


def test_get_funding_rates(bitget, necessary_tickers):
    funding_rates = bitget.get_funding_rates()
    for ticker in necessary_tickers:
        assert ticker in funding_rates
        assert isinstance(funding_rates[ticker], float)


def test_get_contract_sizes(bitget):
    sizes = bitget.get_contract_sizes()
    assert isinstance(sizes, dict)
    assert sizes['BTC'] == 0.001
    assert sizes['ETH'] == 0.01


def test_get_balance(bitget):
    # Test input Start
    ticker = 'USDT'
    balance_input = 3813
    # Test input End

    balance = bitget.get_balance(ticker)
    assert balance_input * 0.9 <= balance <= balance_input * 1.1


def test_get_position(bitget):
    # Test input Start
    inputs = [
        {
            'ticker': 'CORE',
            'amount': 0
        },
        {
            'ticker': 'API3',
            'amount': 1137
        }
    ]
    # Test input End

    for data in inputs:
        amount = data['amount']

        position = bitget.get_position(data['ticker'])
        assert isinstance(position, float)
        if amount:
            assert math.isclose(position, amount)


def test_post_market_order(bitget):
    # Test input Start
    ticker = 'XRP'
    amount = 10
    # Test input End

    last_price = bitget.ccxt_inst.fetch_ticker(f'{ticker}USDT')['last']

    buy_open_price = bitget.post_market_order(ticker, 'buy', 'open', amount)
    assert 0.9 * last_price < buy_open_price < 1.1 * last_price
    sell_close_price = bitget.post_market_order(ticker, 'sell', 'close', amount)
    assert 0.9 * last_price < sell_close_price < 1.1 * last_price
    sell_open_price = bitget.post_market_order(ticker, 'sell', 'open', amount)
    assert 0.9 * last_price < sell_open_price < 1.1 * last_price
    buy_close_price = bitget.post_market_order(ticker, 'buy', 'close', amount)
    assert 0.9 * last_price < buy_close_price < 1.1 * last_price


def test_get_precise_order_amount(bitget):
    ticker = 'BTC'
    ticker_amount = 0.0011
    assert bitget.get_precise_order_amount(ticker, ticker_amount) == 0.001
