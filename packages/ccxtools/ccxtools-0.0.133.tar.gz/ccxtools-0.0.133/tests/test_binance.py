import pytest

from src.ccxtools.binance import Binance


@pytest.fixture
def binance(env_vars):
    return Binance('', env_vars, {})


def test_is_transferring(binance):
    # Test input Start
    is_transferring = False
    # withdraw_option = {
    #     'ticker': 'SOL',
    #     'amount': 0.02,
    #     'destination': 'UPBIT',
    # }
    withdraw_option = None
    # Test input End

    result = binance.is_transferring()
    assert result == is_transferring

    if withdraw_option:
        binance.post_withdraw(
            withdraw_option['ticker'],
            withdraw_option['amount'],
            withdraw_option['destination']
        )

        assert binance.is_transferring() is True
