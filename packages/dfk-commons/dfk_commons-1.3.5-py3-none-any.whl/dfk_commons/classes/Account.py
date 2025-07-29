from dfk_commons.classes.RPCProvider import RPCProvider

class Account:
    def __init__(self, account, rpcProvider: RPCProvider, account_data) -> None:
        self.account = account
        self.address = account.address
        self.key = account.key
        self.rpcProvider = rpcProvider
        if account_data != None:
            self.manager_id = account_data["manager"] if "manager" in account_data else None
            self.profession = account_data["profession"] if "profession" in account_data else "mining"
            self.enabled_quester = account_data["enabled_quester"] if "enabled_quester" in account_data else False
            self.enabled_manager = account_data["enabled_manager"] if "enabled_manager" in account_data else False
            self.questing = account_data["questing"] if "questing" in account_data else False
            self.disabled = account_data["disabled"] if "disabled" in account_data else False
        else:
            self.manager_id = None
            self.profession = None
            self.enabled_quester = False
            self.enabled_manager = False
            self.questing = False
    
    @property
    def nonce(self):
        return self.rpcProvider.w3.eth.get_transaction_count(self.address, "pending")