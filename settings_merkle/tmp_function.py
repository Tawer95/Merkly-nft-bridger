from web3 import Web3
from settings_merkle.chains_settings import text
import requests
from loguru import logger
import time


def init(rpc_from, rpc_to):
    try:
        w3_from = Web3(Web3.HTTPProvider(rpc_from))
        w3_to = Web3(Web3.HTTPProvider(rpc_to))

        return w3_from, w3_to
    except Exception as err:
        print(err)
    
def get_balance(account, w3_from):
    return w3_from.eth.get_balance(account.address)

def get_prices():

    try:
        logger.info('get prices')

        prices = {
            'ETH': 0, 
            'BNB': 0, 
            'AVAX': 0, 
            'MATIC': 0, 
            'AVAX': 0, 
            'FTM': 0,
        }

        for symbol in prices:

            url =f'https://min-api.cryptocompare.com/data/price?fsym={symbol}&tsyms=USDT'
            response = requests.get(url)

            try:
                result  = [response.json()]
                price   = result[0]['USDT']
                prices[symbol] = float(price)
            except Exception as error:
                logger.error(f'{error}. set price : 0')
                prices[symbol] = 0

        logger.info(prices)

        return prices
    except Exception as error:
        logger.error(f'Error when get prices {error}. Try again')
        time.sleep(5)
        return get_prices()
    