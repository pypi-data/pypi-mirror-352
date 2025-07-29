class Transfer:
    def __init__(self,
                 transfer_id: int,
                 spend_id: str,
                 user_id: str,
                 asset: str,
                 amount: str,
                 status: str,
                 completed_at: str,
                 comment = None):
        self.ttransfer_id = transfer_id
        self.tspend_id = spend_id
        self.tuser_id = user_id
        self.tasset = asset
        self.tamount = amount
        self.tstatus = status
        self.tcompleted_at = completed_at
        self.tcomment = comment

    def transfer_id(self):
        return self.ttransfer_id
    def spend_id(self):
        return self.tspend_id
    def user_id(self):
        return self.tuser_id
    def asset(self):
        return self.tasset
    def amount(self):
        return self.tamount
    def status(self):
        return self.tstatus
    def completed_at(self):
        return self.tcompleted_at
    def comment(self):
        return self.tcomment
    