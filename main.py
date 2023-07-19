from web3 import Web3, Account
from loguru import logger
from mint import mint_nft
from bridge import bridge
from config import NETWORK_FROM, NETWORK_TO, WAIT_WALLETS, MODUL_BRIDGE, MODUL_MINT
from settings_merkle.chains_settings import text
from settings_merkle.tmp_function import get_prices
from termcolor import cprint
import time

if __name__ == '__main__':

    cprint(text, 'green')
    cprint('       --------------  Crypto-Selkie: https://t.me/tawer_crypt  --------------', 'yellow')
    time.sleep(5)
    
    logger.add("main_log.log", rotation="10 MB", backtrace=True, diagnose=True)

    # get prices of all native currencies for commissions
    prices = get_prices()
    
    with open('private_keys.txt', 'r') as keys_file:
        accounts = [Account.from_key(line.replace("\n", "")) for line in keys_file.readlines()]

    count = 0
    for account in accounts:

        count += 1
        logger.opt(colors=True).info(f'<cyan>Start | {count} wallet | {account.address}</cyan>')

        if MODUL_MINT == True:
            result_mint = mint_nft(account, NETWORK_FROM, NETWORK_TO)
            if result_mint == True and MODUL_BRIDGE == True:
                logger.info(f'Bridge in 20 second')
                time.sleep(20)
                result_bridge = bridge(account, NETWORK_FROM, NETWORK_TO, prices)
                if result_bridge == True:
                    logger.info(f'Succsess! Next wallet in {WAIT_WALLETS} second')
                    time.sleep(WAIT_WALLETS)
                    continue
                else:
                    logger.info(f'Error! Next wallet in {WAIT_WALLETS} second')
                    time.sleep(WAIT_WALLETS)
                    continue

            elif result_mint == True and MODUL_BRIDGE == False:
                logger.info(f'Succsess! Next wallet in {WAIT_WALLETS} second')
                time.sleep(WAIT_WALLETS)
                continue

            else:
                logger.info(f'Error! Next wallet in {WAIT_WALLETS} second')
                time.sleep(WAIT_WALLETS)
                continue
        if MODUL_MINT == False and MODUL_BRIDGE == True:
            logger.info(f'Bridge in 5 second')
            result_bridge = bridge(account, NETWORK_FROM, NETWORK_TO, prices)
            if result_bridge == True:
                logger.info(f'Succsess! Next wallet in {WAIT_WALLETS} second')
                time.sleep(WAIT_WALLETS)
                continue
            else:
                logger.info(f'Error! Next wallet in {WAIT_WALLETS} second')
                time.sleep(WAIT_WALLETS)

    cprint('DONE', 'yellow')


    