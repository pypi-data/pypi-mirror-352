from dfk_commons.abi_getters import RouterABI
from dfk_commons.classes.APIService import APIService
from dfk_commons.classes.Account import Account
from dfk_commons.classes.RPCProvider import RPCProvider
from dfk_commons.classes.Token import Token
import time


def buyToken(account: Account, amount: int, expected_cost: int, token: Token, apiService: APIService, rpcProvider: RPCProvider):
    RouterContract = rpcProvider.w3.eth.contract(address=apiService.contracts["Router"]["address"], abi=RouterABI)
    tx = RouterContract.functions.swapETHForExactTokens(
        amount,
        [apiService.tokens["Jewel"].address, token.address],
        account.address,
        int(time.time()+60)
        
    ).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
        "value": expected_cost
    })
    tx["gas"] = int(rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = rpcProvider.w3.to_wei(50, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(3, "gwei")
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)
