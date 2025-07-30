import pytest
import math
from src.ccxtools.binance_coin import BinanceCoin


@pytest.fixture
def binance_coin(env_vars):
    return BinanceCoin('', env_vars)


def test_get_mark_price(binance_coin):
    assert isinstance(binance_coin.get_mark_price('BTC'), float)


def test_get_mark_prices(binance_coin):
    # Test input Start
    tickers = ['BTC', 'ETH']
    # Test input End

    prices = binance_coin.get_mark_prices(tickers)
    assert isinstance(prices, dict)
    for ticker in tickers:
        assert ticker in prices
        assert isinstance(prices[ticker], float)


def test_get_best_book_price(binance_coin):
    assert isinstance(binance_coin.get_best_book_price('BTC', 'ask'), float)
    assert isinstance(binance_coin.get_best_book_price('BTC', 'bid'), float)


def test_get_contract_size(binance_coin):
    assert binance_coin.get_contract_size('BTC') == 100
    assert binance_coin.get_contract_size('XRP') == 10


def test_get_balance(binance_coin):
    # Test input Start
    ticker = 'XRP'
    balance_input = 22400
    # Test input End

    balance = binance_coin.get_balance(ticker)
    assert isinstance(balance, float)
    assert balance_input * 0.9 <= balance <= balance_input * 1.1


def test_get_balances(binance_coin):
    # Test input Start
    tickers = ['ETH', 'XRP']
    balances_input = {
        'ETH': 0.49,
        'XRP': 24023,
    }
    # Test input End

    balances = binance_coin.get_balances(tickers)
    assert isinstance(balances, dict)
    for ticker in tickers:
        ticker_balance = balances[ticker]
        assert ticker in balances
        assert isinstance(ticker_balance, float)
        assert balances_input[ticker] * 0.9 <= ticker_balance <= balances_input[ticker] * 1.1


def test_get_spot_balances(binance_coin):
    # Test input Start
    tickers = ['XRP', 'ETH', 'SOLO']
    balances_input = {
        'XRP': 0,
        'ETH': 0,
        'SOLO': 0.05521,
    }
    # Test input End

    balances = binance_coin.get_spot_balances(tickers)
    assert isinstance(balances, dict)
    for ticker in tickers:
        assert ticker in balances
        ticker_balance = balances[ticker]
        assert isinstance(ticker_balance, float) or isinstance(ticker_balance, int)
        assert balances_input[ticker] * 0.9 <= ticker_balance <= balances_input[ticker] * 1.1


def test_get_position(binance_coin):
    # Test input Start
    ticker = 'XRP'
    amount = 1000
    # Test input End

    position = binance_coin.get_position(ticker)
    assert isinstance(position, float)
    if amount:
        assert math.isclose(position, amount)


def test_post_market_order(binance_coin):
    # Test input Start
    ticker = 'XRP'
    amount = 10
    # Test input End

    last_price = binance_coin.ccxt_inst.fetch_ticker(f'{ticker}USD_PERP')['last']

    buy_open_price = binance_coin.post_market_order(ticker, 'buy', 'open', amount)
    assert 0.9 * last_price < buy_open_price < 1.1 * last_price
    sell_close_price = binance_coin.post_market_order(ticker, 'sell', 'close', amount)
    assert 0.9 * last_price < sell_close_price < 1.1 * last_price
    sell_open_price = binance_coin.post_market_order(ticker, 'sell', 'open', amount)
    assert 0.9 * last_price < sell_open_price < 1.1 * last_price
    buy_close_price = binance_coin.post_market_order(ticker, 'buy', 'close', amount)
    assert 0.9 * last_price < buy_close_price < 1.1 * last_price
