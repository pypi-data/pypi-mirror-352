import requests
from dfk_commons.classes.Token import Token


class APIService:
    def __init__(self, url, api_key, chain):
        self.url = url
        self.headers = {
            'x-api-key': api_key,
            'Content-Type': 'application/json'
        }
        self.tokens = self.getTokens(chain)
        self.contracts = self.getContracts(chain)
        self.pairs = self.getPairs("Jewel", chain)

    def getTokens(self, chain):
        response = requests.get(f"{self.url}/dfk/tokens", headers=self.headers,  params={"chain": chain})
        response_json = response.json()
       
        if response.status_code != 200: raise Exception(f"API Error: {response_json}")
        tokens = {}
        for token in response_json:
            tokens[token] = Token(token, chain, response_json[token]["address"], response_json[token]["decimals"], None)
        return tokens

    def getPairs(self, base_token, chain):
        response = requests.get(f"{self.url}/dfk/pairs", headers=self.headers, params={"token": base_token, "chain": chain})
        response_json = response.json()
        if response.status_code != 200: raise Exception(f"API Error: {response_json}")
        return response_json
    
    def getContracts(self, chain):
        response = requests.get(f"{self.url}/dfk/contracts", headers=self.headers, params={"chain": chain})
        response_json = response.json()
        if response.status_code != 200: raise Exception(f"API Error: {response_json}")
        return response_json
    