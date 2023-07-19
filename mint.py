from web3 import Web3
from settings_merkle.RPC import RPC_LIST
from settings_merkle.chains_settings import DATA_CHAINS
from settings_merkle.tmp_function import init, get_balance, get_prices
from loguru import logger
import json



def mint_nft(account, from_chain, to_chain):

    w3_from, w3_to = init(RPC_LIST[from_chain], RPC_LIST[to_chain])

    balance = get_balance(account, w3_from)
    balance = w3_from.from_wei(balance, 'ether')
    if balance < 0.002:
        logger.error(f"insufficient fund balance, need 0.002 ETH")
        return False

    address = w3_from.to_checksum_address(account.address)
    nonce = w3_from.eth.get_transaction_count(address)

    try:
        contract_for_mint = w3_from.eth.contract(address=DATA_CHAINS[from_chain]['contract'], abi=json.load(open(f'abi/{from_chain}.json')))

        # Fee of mint function
        mint_fee = contract_for_mint.functions.fee().call()
        # Gas limit
        gas = contract_for_mint.functions.mint().estimate_gas({'from':address, 'value':mint_fee})
        gas = int(gas * 1.1)
        gasPrice = w3_from.eth.gas_price
        
        # Сделать в будущем привязку к максимальной стоимости минта
        # txnCost = gas * gasPrice + mint_fee

        mint = contract_for_mint.functions.mint().build_transaction({
            'from' : address,
            'value' : mint_fee,
            'gas' : gas,
            'gasPrice':gasPrice,
            'nonce': nonce,
        })

        signed_transaction = account.sign_transaction(mint)
        txn_hash = w3_from.eth.send_raw_transaction(signed_transaction.rawTransaction)

        logger.info(f"Mint txn sent for {account.address}. Txn hash: {txn_hash.hex()}")

        # Wait for transaction will be minted
        receipt = w3_from.eth.wait_for_transaction_receipt(txn_hash)
        if receipt.status == 1:
            logger.success(f"Mint txn success for {account.address}")
            return True
        else:
            logger.error(f"Mint txn failed for {account.address}")
            return False

    except Exception as err:
        logger.error(f'Error when minte nft on {account.address}', err)
        return False


