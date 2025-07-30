import time
import pytest

from src.ccxtools.upbit import Upbit


@pytest.fixture
def upbit(env_vars):
    return Upbit('', env_vars)


def test_get_last_price(upbit):
    price = upbit.get_last_price('BTC')
    assert isinstance(price, float)


def test_get_last_prices(upbit):
    # Test input Start
    tickers = ['ETH', 'XRP']
    # Test input End

    prices = upbit.get_last_prices(tickers)
    assert isinstance(prices, dict)
    for ticker in tickers:
        assert ticker in prices
        assert isinstance(prices[ticker], float)


def test_get_best_book_price(upbit):
    assert isinstance(upbit.get_best_book_price('BTC', 'ask'), float)
    assert isinstance(upbit.get_best_book_price('BTC', 'bid'), float)


def test_get_withdraw_net_type(upbit):
    # Test input Start
    tickers = ['BTC', 'ETH', 'SOL']
    net_types = ['BTC', 'ETH', 'SOL']
    # Test input End

    for ticker, net_type in zip(tickers, net_types):
        assert upbit.get_withdraw_net_type(ticker) == net_type


def test_get_withdraw_decimal_limits(upbit):
    # Test input Start
    tickers = ['XRP', 'ETH', 'SOL']
    expected_result = {
        'ETH': 18,
        'SOL': 9,
        'XRP': 6
    }
    # Test input End

    result = upbit.get_withdraw_decimal_limits(['XRP', 'ETH', 'SOL'])
    assert result == expected_result


def test_is_withdrawable(upbit):
    # Test input Start
    ticker = 'SOL'
    expected_result = True
    # Test input End

    assert upbit.is_withdrawable(ticker) == expected_result


def test_is_transferring(upbit, env_vars):
    # Test input Start
    is_transferring = False
    # withdraw_option = {
    #     'ticker': 'SOL',
    #     'amount': 0.01,
    #     'destination': 'BINANCE',
    # }
    withdraw_option = None
    # Test input End

    result = upbit.is_transferring()
    assert result == is_transferring

    if withdraw_option:
        upbit.post_withdraw(
            withdraw_option['ticker'],
            withdraw_option['amount'],
            withdraw_option['destination']
        )
        time.sleep(3)

        assert upbit.is_transferring() is True


def test_get_balances(upbit):
    # Test input Start
    tickers = ['ETH', 'XRP']
    balances_input = {
        'ETH': 0.004212,
        'XRP': 15698,
    }
    # Test input End

    balances = upbit.get_balances(tickers)
    assert isinstance(balances, dict)
    for ticker in tickers:
        ticker_balance = balances[ticker]
        assert ticker in balances
        assert isinstance(ticker_balance, float)
        assert balances_input[ticker] * 0.9 <= ticker_balance <= balances_input[ticker] * 1.1


def test_post_market_order(upbit):
    # Test input Start
    ticker = 'XRP'
    amount = 10
    # Test input End

    last_price = upbit.get_last_price(ticker)

    buy_price = upbit.post_market_order(ticker, 'buy', amount, last_price)
    assert 0.9 * last_price < buy_price < 1.1 * last_price
    sell_price = upbit.post_market_order(ticker, 'sell', amount, last_price)
    assert 0.9 * last_price < sell_price < 1.1 * last_price
