class Check:
    def __init__(self,
                 check_id: str,
                 hash: str,
                 asset: str,
                 amount: str,
                 bot_check_url: str,
                 status: str,
                 created_at: str,
                 activated_at: str):
         self.ccheck_id = check_id
         self.chash = hash
         self.casset = asset
         self.camount = amount
         self.cbot_check_url = bot_check_url
         self.cstatus = status
         self.ccreated_at = created_at
         self.cactivated_at = activated_at

    def check_id(self):
         return self.ccheck_id
    def hash(self):
         return self.chash
    def asset(self):
         return self.casset
    def amount(self):
         return self.camount
    def bot_check_url(self):
         return self.cbot_check_url
    def status(self):
         return self.cstatus
    def created_at(self):
         return self.ccreated_at
    def activated_at(self):
         return self.cactivated_at