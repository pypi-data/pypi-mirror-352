from dfk_commons.classes.TablesManager import TablesManager


def get_tables_manager(isProd, isDup = False, region="us-east-1"):
    return TablesManager(isProd, isDup, region)
