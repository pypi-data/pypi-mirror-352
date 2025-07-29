class Currencies:
    def __init__(self,
                 code: str,
                 decimals: int,
                 is_blockchain: bool,
                 is_fiat: bool,
                 is_stablecoin: bool,
                 name: str, 
                 url = None):
        self.ccode = code
        self.cdecimals = decimals
        self.cis_blockchain = is_blockchain
        self.cis_fiat = is_fiat
        self.cis_stablecoin = is_stablecoin
        self.cname = name
        self.curl = url

    def code(self):
        return self.ccode
    
    def decimals(self):
        return self.cdecimals
    
    def is_blockchain(self):
        return self.cis_blockchain
    
    def is_fiat(self):
        return self.cis_fiat
    
    def is_stablecoin(self):
        return self.cis_stablecoin
    
    def name(self):
        return self.cname
    
    def url(self):
        return self.curl