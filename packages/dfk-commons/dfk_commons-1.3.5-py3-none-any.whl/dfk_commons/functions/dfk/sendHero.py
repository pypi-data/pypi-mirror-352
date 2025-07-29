from dfk_commons.abi_getters import ERC721ABI
from dfk_commons.classes.APIService import APIService
from dfk_commons.classes.Account import Account
from dfk_commons.classes.RPCProvider import RPCProvider


def sendHero(account: Account, receiver: str, heroId: int, apiService: APIService, rpcProvider: RPCProvider):
    tx =  rpcProvider.w3.eth.contract(address=apiService.contracts["Heroes"]["address"], abi=ERC721ABI).functions.safeTransferFrom(account.address, receiver, int(heroId)).build_transaction({
        "from": account.address,
        "nonce": account.nonce,
    })
    signed_tx =  rpcProvider.w3.eth.account.sign_transaction(tx, account.key)
    hash =  rpcProvider.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    hash =  rpcProvider.w3.to_hex(hash)