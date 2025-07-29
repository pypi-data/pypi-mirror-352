from dfk_commons.classes.APIService import APIService
from dfk_commons.classes.Account import Account
from dfk_commons.classes.RPCProvider import RPCProvider
from dfk_commons.classes.Token import Token
from dfk_commons.abi_getters import ERC20ABI, ERC721ABI, RouterABI

def getJewelBalance(account: Account, rpcProvider: RPCProvider):
    return int(rpcProvider.w3.eth.get_balance(account.address))

def getCrystalBalance(account: Account, apiService: APIService, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= apiService.tokens["Crystal"].address, abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def getTokenAmount(account: Account, token: Token, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= token.address, abi=ERC20ABI)
    return int(contract.functions.balanceOf(account.address).call())

def getTokenPriceInJewel(token: Token, apiService: APIService, rpcProvider: RPCProvider):
    RouterContract = rpcProvider.w3.eth.contract(address=apiService.contracts["Router"]["address"], abi=RouterABI)
    try:
        price = RouterContract.functions.getAmountsOut(1*(10**token.decimals), [token.address, apiService.tokens["Jewel"].address]).call()[1]
        price = price/(10**token.decimals)
    except Exception as e:
        price = 0
    return price

def heroNumber(account: Account, apiService: APIService, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= apiService.contracts["Heroes"]["address"], abi=ERC721ABI)
    return int(contract.functions.balanceOf(account.address).call())

def sendJewel(account: Account, payout_address: str, amount: int, rpcProvider: RPCProvider):
    tx = {
        "from": account.address,
        "to": payout_address,
        "value": amount,
        "nonce": account.nonce,
        "chainId": rpcProvider.chainId
    }
    tx["gas"] = int(rpcProvider.w3.eth.estimate_gas(tx))
    tx["maxFeePerGas"] = rpcProvider.w3.to_wei(12, 'gwei')
    tx["maxPriorityFeePerGas"] = rpcProvider.w3.to_wei(1, "gwei")
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)

def sendToken(account: Account, payout_address, amount, token: Token, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= token.address, abi=ERC20ABI)
    tx = contract.functions.transfer(
        payout_address,
        amount,
    ).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)

def checkAllowance(account: Account, token: Token, address, abi, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= token.address, abi=abi)
    if int(contract.functions.allowance(account.address, address).call()) == 0:
        return True
    else: 
        return False
    
def addAllowance(account: Account, token: Token, address, abi, rpcProvider: RPCProvider):
    contract = rpcProvider.w3.eth.contract(address= token.address, abi=abi)
    tx = contract.functions.approve(address, 115792089237316195423570985008687907853269984665640564039457584007913129639935).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)