class RPCProvider:
     def __init__(self, chain, provider, url, chainId) -> None:
            self.w3 = provider
            self.chain = chain
            self.url = url
            self.chainId = chainId
         



