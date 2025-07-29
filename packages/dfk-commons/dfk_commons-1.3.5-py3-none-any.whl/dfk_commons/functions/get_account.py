from cryptography.fernet import Fernet
from dfk_commons.classes.Account import Account
from dfk_commons.classes.RPCProvider import RPCProvider
from dfk_commons.classes.TablesManager import TablesManager

def get_account(tablesManager: TablesManager, cypher_key: str, address: str, rpcProvider: RPCProvider):
    f = Fernet(cypher_key.encode())
    account_data = tablesManager.accounts.query(
            KeyConditionExpression="address_ = :address_",
            ExpressionAttributeValues={
                ":address_": address,
            })["Items"][0]
    key = account_data["key_"]
    decrypted_key = f.decrypt(key.encode()).decode()
    return Account(rpcProvider.w3.eth.account.from_key(decrypted_key), rpcProvider, account_data)

def get_account_from_private_key(private_key: str, rpcProvider: RPCProvider):
    return Account(rpcProvider.w3.eth.account.from_key(private_key), rpcProvider, None)