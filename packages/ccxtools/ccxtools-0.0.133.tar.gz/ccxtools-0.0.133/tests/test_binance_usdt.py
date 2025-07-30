import pytest
import math
from src.ccxtools.binance_usdt import BinanceUsdt


@pytest.fixture
def binance_usdt(env_vars):
    return BinanceUsdt('', env_vars)


def test_get_mark_price(binance_usdt):
    assert isinstance(binance_usdt.get_mark_price('BTC'), float)


def test_get_best_book_price(binance_usdt):
    assert isinstance(binance_usdt.get_best_book_price('BTC', 'ask'), float)
    assert isinstance(binance_usdt.get_best_book_price('BTC', 'bid'), float)


def test_get_funding_rates(binance_usdt, necessary_tickers):
    funding_rates = binance_usdt.get_funding_rates()
    for ticker in necessary_tickers:
        assert ticker in funding_rates
        assert isinstance(funding_rates[ticker], float)


def test_get_contract_size(binance_usdt):
    assert binance_usdt.get_contract_size('BTC') == 0.001


def test_get_contract_sizes(binance_usdt):
    sizes = binance_usdt.get_contract_sizes()
    assert isinstance(sizes, dict)
    assert sizes['BTC'] == 0.001
    assert sizes['ETH'] == 0.001


def test_get_max_trading_qtys(binance_usdt):
    max_qtys = binance_usdt.get_max_trading_qtys()
    assert isinstance(max_qtys, dict)
    assert 'BTC' in max_qtys
    assert max_qtys['BTC'] == 120


def test_get_max_position_qtys(binance_usdt):
    qtys = binance_usdt.get_max_position_qtys()
    assert qtys['BTC'] == 300_000_000
    assert qtys['ETH'] == 150_000_000
    assert qtys['XRP'] == 10_000_000


def test_get_balance(binance_usdt):
    # Test input Start
    ticker = 'USDT'
    balance_input = 10459
    # Test input End

    balance = binance_usdt.get_balance(ticker)
    assert balance_input * 0.9 <= balance <= balance_input * 1.1


def test_get_position(binance_usdt):
    # Test input Start
    ticker = 'LPT'
    amount = 0
    # Test input End

    position = binance_usdt.get_position(ticker)
    assert isinstance(position, float)
    if amount:
        assert math.isclose(position, amount)


def test_post_market_order(binance_usdt):
    # Test input Start
    ticker = 'XRP'
    amount = 20
    # Test input End

    last_price = binance_usdt.ccxt_inst.fetch_ticker(f'{ticker}USDT')['last']

    buy_open_price = binance_usdt.post_market_order(ticker, 'buy', 'open', amount)
    assert 0.9 * last_price < buy_open_price < 1.1 * last_price
    sell_close_price = binance_usdt.post_market_order(ticker, 'sell', 'close', amount)
    assert 0.9 * last_price < sell_close_price < 1.1 * last_price
    sell_open_price = binance_usdt.post_market_order(ticker, 'sell', 'open', amount)
    assert 0.9 * last_price < sell_open_price < 1.1 * last_price
    buy_close_price = binance_usdt.post_market_order(ticker, 'buy', 'close', amount)
    assert 0.9 * last_price < buy_close_price < 1.1 * last_price


def test_get_precise_order_amount(binance_usdt):
    ticker = 'BTC'
    ticker_amount = 0.00111
    assert binance_usdt.get_precise_order_amount(ticker, ticker_amount) == 0.001
