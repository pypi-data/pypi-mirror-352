import pytest
import math
from src.ccxtools.bingx import Bingx


@pytest.fixture
def bingx(env_vars):
    return Bingx('', env_vars)


def test_get_last_prices(bingx, necessary_tickers):
    last_prices = bingx.get_last_prices()
    for ticker in necessary_tickers:
        assert ticker in last_prices
        assert isinstance(last_prices[ticker], float)


def test_get_last_price(bingx):
    last_price = bingx.get_last_price('BTC')
    assert isinstance(last_price, float)
    assert last_price > 10000


def test_get_funding_rates(bingx, necessary_tickers):
    funding_rates = bingx.get_funding_rates()
    for ticker in necessary_tickers:
        assert ticker in funding_rates
        assert isinstance(funding_rates[ticker], float)


def test_get_contract_sizes(bingx):
    sizes = bingx.get_contract_sizes()
    assert isinstance(sizes, dict)
    assert sizes['BTC'] == 0.0001
    assert sizes['ETH'] == 0.01


def test_get_balance(bingx):
    # Test input Start
    ticker = 'USDT'
    balance_input = 4908
    # Test input End

    balance = bingx.get_balance(ticker)
    assert balance_input * 0.9 <= balance <= balance_input * 1.1


def test_get_position(bingx):
    # Test input Start
    ticker = 'SEI'
    amount = 937
    # Test input End

    position = bingx.get_position(ticker)
    assert isinstance(position, float)
    if amount:
        assert math.isclose(position, amount)


def test_post_market_order(bingx):
    # Test input Start
    ticker = 'XRP'
    amount = 10
    # Test input End

    last_price = bingx.get_last_price(ticker)

    buy_open_price = bingx.post_market_order(ticker, 'buy', 'open', amount)
    assert 0.9 * last_price < buy_open_price < 1.1 * last_price
    sell_close_price = bingx.post_market_order(ticker, 'sell', 'close', amount)
    assert 0.9 * last_price < sell_close_price < 1.1 * last_price
    sell_open_price = bingx.post_market_order(ticker, 'sell', 'open', amount)
    assert 0.9 * last_price < sell_open_price < 1.1 * last_price
    buy_close_price = bingx.post_market_order(ticker, 'buy', 'close', amount)
    assert 0.9 * last_price < buy_close_price < 1.1 * last_price


def test_get_precise_order_amount(bingx):
    ticker = 'BTC'
    ticker_amount = 0.00011
    assert bingx.get_precise_order_amount(ticker, ticker_amount) == 0.0001
