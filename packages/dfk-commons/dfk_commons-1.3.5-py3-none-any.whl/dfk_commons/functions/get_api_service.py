from dfk_commons.classes.APIService import APIService


def get_api_service(url, api_key, chain):
    if chain == "kaia":
        chain = "klay"
    return APIService(url, api_key, chain)