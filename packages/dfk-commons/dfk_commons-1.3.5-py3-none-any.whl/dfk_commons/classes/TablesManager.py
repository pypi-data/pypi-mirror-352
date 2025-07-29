import boto3
from boto3 import Session

class TablesManager:
    def __init__(self, prod: bool, dup: bool, region: str) -> None:
        self.session: Session = boto3.session.Session(
            region_name = region,
        )
        self.prod: bool = prod
        self.dup = dup

        #autoplayer tables
        self.accounts = None
        self.autoplayer = None
        self.managers = None

        #gas tables
        self.gas = None
        self.mining_gas = None
        self.gardening_gas = None
        self.foraging_gas = None
        self.fishing_gas = None

        #stats tables
        self.mining_stats = None
        self.gardening_stats = None
        self.foraging_stats = None
        self.fishing_stats = None

        #history tables
        self.history = None
        self.payouts = None
        self.fees = None

        #tracking tables
        self.buyer_tracking = None
        self.autoplayer_tracking = None
        self.profit_tracker = None

        #trading tables
        self.trades = None
        self.active_orders = None
        self.trade_errors = None

        #autodfk tables
        self.settings = None
        self.users = None
        self.user_filters = None
        self.queue = None
        self.analysed_heroes = None

        #fast autobuy tables
        self.best_offers = None
        self.all_offers = None

        if dup:
            self.init_dup_tables()
        else:
            self.init_default_tables()

    def init_default_tables(self):
        if self.prod:
            self.accounts = self.session.resource('dynamodb').Table("dfk-autoplayer-accounts")
            self.autoplayer = self.session.resource('dynamodb').Table("dfk-autoplayer")

            #trading tables
            self.trades = self.session.resource('dynamodb').Table("dfk-trading-trades")
            self.active_orders = self.session.resource('dynamodb').Table("dfk-trading-active-orders")
            self.trade_errors = self.session.resource('dynamodb').Table("dfk-trading-errors")
        else:
            self.accounts = self.session.resource('dynamodb').Table("dfk-autoplayer-accounts-dev")
            self.autoplayer = self.session.resource('dynamodb').Table("dfk-autoplayer-dev")

            #trading tables
            self.trades = self.session.resource('dynamodb').Table("dfk-trading-trades-dev")
            self.active_orders = self.session.resource('dynamodb').Table("dfk-trading-active-orders-dev")
            self.trade_errors = self.session.resource('dynamodb').Table("dfk-trading-errors-dev")

        self.managers = self.session.resource('dynamodb').Table("autodfk-managers")

        #gas tables
        self.gas = self.session.resource('dynamodb').Table("dfk-autoplayer-gas")
        self.mining_gas = self.session.resource('dynamodb').Table("dfk-autoplayer-mining-gas")
        self.gardening_gas = self.session.resource('dynamodb').Table("dfk-autoplayer-gardening-gas")
        self.foraging_gas = self.session.resource('dynamodb').Table("dfk-autoplayer-foraging-gas")
        self.fishing_gas = self.session.resource('dynamodb').Table("dfk-autoplayer-fishing-gas")

        #stats tables
        self.mining_stats = self.session.resource('dynamodb').Table("dfk-autoplayer-mining-stats")
        self.gardening_stats = self.session.resource('dynamodb').Table("dfk-autoplayer-gardening-stats")
        self.foraging_stats = self.session.resource('dynamodb').Table("dfk-autoplayer-foraging-stats")
        self.fishing_stats = self.session.resource('dynamodb').Table("dfk-autoplayer-fishing-stats")

        #history tables
        self.history = self.session.resource('dynamodb').Table("dfk-autoplayer-history")
        self.payouts = self.session.resource('dynamodb').Table("dfk-autoplayer-payouts")
        self.fees = self.session.resource('dynamodb').Table("dfk-autoplayer-fee")

        #tracking tables
        self.buyer_tracking = self.session.resource('dynamodb').Table("dfk-buyer-tracking")
        self.autoplayer_tracking = self.session.resource('dynamodb').Table("dfk-autoplayer-tracking")
        self.profit_tracker = self.session.resource('dynamodb').Table("dfk-profit-tracker")
    
    def init_dup_tables(self):
        self.accounts = self.session.resource('dynamodb').Table("accounts")
        self.settings = self.session.resource('dynamodb').Table("settings")
        self.users = self.session.resource('dynamodb').Table("users")
        self.user_filters= self.session.resource('dynamodb').Table("user-filters")
        self.queue = self.session.resource('dynamodb').Table("autodfk-queue")
        self.managers = self.session.resource('dynamodb').Table("autodfk-managers")
        self.analysed_heroes = self.session.resource('dynamodb').Table("autodfk-analysed-heroes")
        self.best_offers = self.session.resource('dynamodb').Table("autobuy-best-offers")
        self.all_offers = self.session.resource('dynamodb').Table("autobuy-all-offers")
    