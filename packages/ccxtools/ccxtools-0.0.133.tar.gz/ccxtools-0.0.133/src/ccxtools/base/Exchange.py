from abc import ABCMeta, abstractmethod


class Exchange(metaclass=ABCMeta):
    WITHDRAW_TAG_NECESSARY_TICKERS = ['XRP']

    def __init__(self, env_vars):
        self.env_vars = env_vars

    @abstractmethod
    def get_balance(self, ticker):
        raise NotImplementedError
