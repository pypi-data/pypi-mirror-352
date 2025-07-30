import asyncio
import os
import time

import requests
import re
from bs4 import BeautifulSoup
from ccxtools.ccserver.server_fetcher import ServerFetcher
from decouple import Config, RepositoryEnv
from selenium import webdriver


def get_current_directory():
    return os.path.abspath(os.curdir)


def get_env_vars():
    current_directory = get_current_directory()
    return Config(RepositoryEnv(f'{current_directory}/.env'))


def get_async_results(func_list):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError as error:
        if 'There is no current event loop in thread' in str(error):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        else:
            raise error

    async def run_func(func_info):
        func = func_info['func']
        args = func_info.get('args', ())
        return await loop.run_in_executor(None, func, *args)

    results = loop.run_until_complete(asyncio.gather(*[
        run_func(func_info) for func_info in func_list
    ]))
    return results


def add_query_to_url(base_url, queries):
    url = f'{base_url}?'
    for field, value in queries.items():
        url += f'{field}={value}&'
    return url[:-1]


def get_usdkrw_rate():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    driver = webdriver.Chrome(options=chrome_options)

    url = "https://www.xe.com/currencyconverter/convert/?Amount=1&From=USD&To=KRW"
    driver.get(url)

    time.sleep(2)

    b_soup = BeautifulSoup(driver.page_source, "html.parser")
    driver.quit()

    one_usd_element = b_soup.find(lambda tag: tag.name == 'p' and 'US Dollar' in tag.text)
    usd_krw_text = one_usd_element.find_next_sibling().text
    exch_rate = float(re.search(r'[\d,]+\.\d+', usd_krw_text).group().replace(',', ''))

    if not 1000 < exch_rate < 1500:
        server_fetcher = ServerFetcher(
            'http://ec2-43-202-43-133.ap-northeast-2.compute.amazonaws.com',
            get_env_vars()('SERVER_TOKEN'),
            'CCXTOOLS'
        )
        server_fetcher.post_log_error(
            'get_usdkrw_rate 오류',
            'xe.com 환율 1000 < x < 1500 이 아님'
        )

        alter_url = "https://finance.naver.com/marketindex/"
        selector = "#exchangeList > li:nth-child(1) > a.head.usd > div > span.value"

        b_soup = BeautifulSoup(requests.get(alter_url).text, "html.parser")
        tags = b_soup.select(selector)
        exch_rate = float(tags[0].text.replace(',', ''))

    return exch_rate
