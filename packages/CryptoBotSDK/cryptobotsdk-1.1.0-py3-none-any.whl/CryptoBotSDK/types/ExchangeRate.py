class ExchangeRate:
    def __init__(self,
                 is_valid: bool,
                 is_crypto: bool,
                 is_fiat: bool,
                 source: str,
                 target: str,
                 rate: str):
        self.eis_valid = is_valid
        self.eis_crypto = is_crypto
        self.eis_fiat = is_fiat
        self.esource = source
        self.etarget = target
        self.erate = rate

    def is_valid(self):
        return self.eis_valid
    
    def is_crypto(self):
        return self.eis_crypto
    
    def is_fiat(self):
        return self.eis_fiat
    
    def source(self):
        return self.esource
    
    def target(self):
        return self.etarget
    
    def rate(self):
        return self.erate