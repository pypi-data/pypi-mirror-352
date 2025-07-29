from web3 import Web3
from web3.middleware import geth_poa_middleware
import requests

from dfk_commons.classes.RPCProvider import RPCProvider

def try_rpc(rpc, logger):
    try:
        session = requests.Session()
        if "id" in rpc and "password" in rpc:
            session.auth = (rpc["id"], rpc["password"])
        w3 = Web3(Web3.HTTPProvider(rpc["url"], session=session))
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        w3.client_version
        w3.eth.get_block("latest")
        return w3
    except Exception as e:
        logger.info(f"RPC {rpc['url']} failed: {e}")
    return False


def get_rpc_provider(chain, logger):
    if chain == "dfk":
        rpc_list = [
            {
                "url":"https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc",
            },
        ]
        chainId= 53935
    elif chain == "klay" or chain == "kaia":
        rpc_list = [
            {
                "url":"https://kaia.rpc.defikingdoms.com",
            },
            {
                "url":"https://public-en.node.kaia.io",
            },
        ]
        chainId = 8217

    for rpc in rpc_list:
        w3 = try_rpc(rpc, logger)
        if w3:
            return RPCProvider(chain, w3, rpc["url"], chainId)
        
    raise Exception("No RPC available")
