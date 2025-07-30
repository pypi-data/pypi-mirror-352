import math
import pytest
from src.ccxtools.huobi import Huobi


@pytest.fixture
def huobi(env_vars):
    return Huobi('', env_vars)


def test_get_funding_rates(huobi, necessary_tickers):
    funding_rates = huobi.get_funding_rates()
    for ticker in necessary_tickers:
        assert ticker in funding_rates
        assert isinstance(funding_rates[ticker], float)


def test_get_contract_sizes(huobi):
    sizes = huobi.get_contract_sizes()
    assert isinstance(sizes, dict)
    assert sizes['BTC'] == 0.001
    assert sizes['ETH'] == 0.01


def test_get_balance(huobi):
    # Test input Start
    ticker = 'USDT'
    balance_input = 2600
    # Test input End

    balance = huobi.get_balance(ticker)
    assert balance_input * 0.9 <= balance <= balance_input * 1.1


def test_get_position(huobi):
    # Test input Start
    ticker = 'GRT'
    amount = -19680
    # Test input End

    position = huobi.get_position(ticker)
    assert isinstance(position, float)
    if amount:
        assert math.isclose(position, amount)


def test_post_market_order(huobi):
    # Test input Start
    ticker = 'XRP'
    amount = 20
    # Test input End

    last_price = huobi.ccxt_inst.fetch_ticker(f'{ticker}-USDT')['last']

    buy_open_price = huobi.post_market_order(ticker, 'buy', 'open', amount)
    assert 0.9 * last_price < buy_open_price < 1.1 * last_price
    sell_close_price = huobi.post_market_order(ticker, 'sell', 'close', amount)
    assert 0.9 * last_price < sell_close_price < 1.1 * last_price
    sell_open_price = huobi.post_market_order(ticker, 'sell', 'open', amount)
    assert 0.9 * last_price < sell_open_price < 1.1 * last_price
    buy_close_price = huobi.post_market_order(ticker, 'buy', 'close', amount)
    assert 0.9 * last_price < buy_close_price < 1.1 * last_price


def test_get_precise_order_amount(huobi):
    ticker = 'BTC'
    ticker_amount = 0.0011
    assert huobi.get_precise_order_amount(ticker, ticker_amount) == 0.001


def test_get_max_trading_qtys(huobi):
    max_qtys = huobi.get_max_trading_qtys()
    assert isinstance(max_qtys, dict)
    assert 'BTC' in max_qtys
    assert max_qtys['BTC'] == 500000
