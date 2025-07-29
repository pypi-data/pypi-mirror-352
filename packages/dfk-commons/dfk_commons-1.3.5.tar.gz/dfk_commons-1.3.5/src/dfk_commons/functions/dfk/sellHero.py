from dfk_commons.classes.Account import Account
from dfk_commons.classes.APIService import APIService
from dfk_commons.classes.RPCProvider import RPCProvider
from dfk_commons.abi_getters import HeroSaleABI
from dfk_commons.constants import ZERO_ADDRESS

def sellHero(account: Account, heroId: int, heroPrice: int, apiService: APIService, rpcProvider: RPCProvider):
    HeroSaleContract = rpcProvider.w3.eth.contract(address=apiService.contracts["HeroSale"]["address"], abi=HeroSaleABI)
    tx = HeroSaleContract.functions.createAuction(heroId, heroPrice, heroPrice, 999999999, ZERO_ADDRESS).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    signed_tx = rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash = rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash = rpcProvider.w3.to_hex(hash)
    rpcProvider.w3.eth.wait_for_transaction_receipt(hash)