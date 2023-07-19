from web3 import Web3
from settings_merkle.RPC import RPC_LIST
from settings_merkle.chains_settings import DATA_CHAINS
from settings_merkle.tmp_function import init, get_balance, get_prices
from config import API_KEY_MORALIS, MAX_LZ_FEE
from loguru import logger
from moralis import evm_api
import time
import json

def check_nft(account, from_chain):
    api_key = API_KEY_MORALIS
    params = {
        "chain": from_chain,
        "format": "decimal",
        "limit": 10,
        "token_addresses": [DATA_CHAINS[from_chain]['contract']],
        "media_items": False,
        "address": account.address,
        "normalizeMetadata": True,
    }

    try:
        result = evm_api.nft.get_wallet_nfts(api_key=api_key, params=params)
        id = int(result['result'][0]['token_id'])
        if id:
            logger.success(f'{account.address} - Merkly {id} nft founded on {from_chain}...')
            return id
    except Exception as err:
        logger.error(f'Error when check nft - {err}')
        return False




def bridge(account, from_chain, to_chain, prices):
    # check connection
    try:
        w3_from, w3_to = init(RPC_LIST[from_chain], RPC_LIST[to_chain])
    except:
        logger.error(f"Problen connetction to {from_chain} or {to_chain}")
        return False
    
    # check balance
    balance = get_balance(account, w3_from)
    balance = w3_from.from_wei(balance, 'ether')
    nonce = w3_from.eth.get_transaction_count(account.address)

    if balance < DATA_CHAINS[from_chain]['min_balance']:
        logger.error(f"insufficient fund balance, need {DATA_CHAINS[from_chain]['min_balance']} native")
        return False

    # check nft
    id = check_nft(account, from_chain)

    # check fee LZ and est_gas
    try:
        contract_merkly = w3_from.eth.contract(address=w3_from.to_checksum_address(DATA_CHAINS[from_chain]['contract']), abi=json.load(open(f'abi/{from_chain}.json')))

        _dstChainId = DATA_CHAINS[to_chain]['chain_id']
        _userApplication = DATA_CHAINS[from_chain]['contract']
        _tokenId = id
        _payInZRO = False
        _adapterParams = bytes.fromhex('00010000000000000000000000000000000000000000000000000000000000061a80')

        lzFees = contract_merkly.functions.estimateSendFee(
                                            _dstChainId,                                              
                                            _userApplication,                                                                    
                                            _tokenId,                                                              
                                            _payInZRO,                                                                 
                                            _adapterParams,
                                        ).call()
        lzFee = lzFees[0]
        lzFeeHuman = w3_from.from_wei(lzFee, 'ether')

    except Exception as err:
        logger.error(err)
        return False
    
    while True:
        if (MAX_LZ_FEE / prices[DATA_CHAINS[from_chain]['native']]) > lzFeeHuman:
            try:
                #  check estimate_gas
                _from = account.address
                _dstChainId = DATA_CHAINS[to_chain]['chain_id']
                _toAddress = account.address
                _tokenId = id
                _refundAddress = account.address
                _zroPaymentAddress = '0x0000000000000000000000000000000000000000'
                _adapterParams = bytes.fromhex('00010000000000000000000000000000000000000000000000000000000000061a80')

                gas = contract_merkly.functions.sendFrom(
                                                    _from,                                              
                                                    _dstChainId,                                                                    
                                                    _toAddress,                                                              
                                                    _tokenId,                                                                 
                                                    _refundAddress,
                                                    _zroPaymentAddress,
                                                    _adapterParams,
                                                ).estimate_gas({
                                                                    'from': account.address,
                                                                    'value': lzFee,
                                                                    'nonce': nonce,
                                                                            })
                break

            except Exception as err:
                logger.error(err)
                return False
        else:
            logger.info(f'комиссия LZ {lzFeeHuman} выше, чем максимальная')
            time.sleep(30)
            continue
            
    # start bridge
    try:

        _from = account.address
        _dstChainId = DATA_CHAINS[to_chain]['chain_id']
        _toAddress = account.address
        _tokenId = id
        _refundAddress = account.address
        _zroPaymentAddress = '0x0000000000000000000000000000000000000000'
        _adapterParams = bytes.fromhex('00010000000000000000000000000000000000000000000000000000000000061a80')

        bridge = contract_merkly.functions.sendFrom(
                                            _from,                                              
                                            _dstChainId,                                                                    
                                            _toAddress,                                                              
                                            _tokenId,                                                                 
                                            _refundAddress,
                                            _zroPaymentAddress,
                                            _adapterParams,
                                        ).build_transaction({
                                                            'from': account.address,
                                                            'value': lzFee,
                                                            'gas': gas,
                                                            'gasPrice': w3_from.eth.gas_price,
                                                            'nonce': nonce,
                                                                    })
        signed_transaction = account.sign_transaction(bridge)
        txn_hash = w3_from.eth.send_raw_transaction(signed_transaction.rawTransaction)

        logger.info(f"Bridge txn sent for {account.address}. Txn hash: {txn_hash.hex()}")

        # Wait for transaction will be minted
        receipt = w3_from.eth.wait_for_transaction_receipt(txn_hash)
        if receipt.status == 1:
            logger.success(f"Bridge txn success for {account.address}")
            return True
        else:
            logger.error(f"Bridge txn failed for {account.address}")
            return False
    except Exception as err:
        logger.error(err)
        return False


    
