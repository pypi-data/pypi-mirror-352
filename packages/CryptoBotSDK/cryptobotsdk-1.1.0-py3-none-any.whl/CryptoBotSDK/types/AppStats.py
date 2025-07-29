class AppStats:

    def __init__(self,
                 volume: int,
                 conversion: int,
                 unique_users_count: int,
                 created_invoice_count: int,
                 paid_invoice_count: int,
                 start_at: str,
                 end_at: str):
        self.avolume = volume
        self.aconversion = conversion
        self.aunique_users_count = unique_users_count
        self.acreated_invoice_count = created_invoice_count
        self.apaid_invoice_count = paid_invoice_count
        self.astart_at = start_at
        self.aend_at = end_at

    def volume(self):
        return self.avolume
    
    def conversion(self):
        return self.aconversion
    
    def unique_users_count(self):
        return self.aunique_users_count
    
    def created_invoice_count(self):
        return self.acreated_invoice_count
    
    def paid_invoice_count(self):
        return self.apaid_invoice_count

    def start_at(self):
        return self.astart_at
    
    def end_at(self):
        return self.aend_at