class Balance:
    def __init__(self, currencry_code: str, available: str, onhold: str):
        self.ccurrency_code = currencry_code
        self.caavailable = available
        self.conhold = onhold
        
    def currencry_code(self):
        return self.ccurrency_code
    def available(self):
        return self.caavailable
    def onhold(self):
        return self.conhold