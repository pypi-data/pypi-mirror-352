import warnings

class Invoice:
    def __init__(self,
                 invoice_id: int,
                 hash: str,
                 currency_type: str,
                 amount: str,
                 bot_invoice_url: str,
                 mini_app_invoice_url: str,
                 web_app_invoice_url: str,
                 status: str,
                 created_at: str,
                 comment: str,
                 hidden_message: str,
                 payload: str
                 ):
        self.pinvoice_id = invoice_id
        self.phash = hash
        self.pcurrency_type = currency_type
        self.pamount = amount
        self.pbot_invoice_url = bot_invoice_url
        self.pmini_app_invoice_url = mini_app_invoice_url
        self.pweb_app_invoice_url = web_app_invoice_url
        self.pstatus = status
        self.pcreated_at = created_at
        self.pcomment = comment
        self.phidden_message = hidden_message
        self.ppayload = payload

    def hash(self):
        return self.phash
    def currency_type(self):
        return self.pcurrency_type
    def amount(self):
        return self.pamount
    def bot_invoice_url(self):
        return self.pbot_invoice_url
    def mini_app_invoice_url(self):
        return self.pmini_app_invoice_url
    def web_app_invoice_url(self):
        return self.pweb_app_invoice_url
    def status(self):
        return self.pstatus
    def comment(self):
        if self.pcomment == "not_provided_stuff":
            warnings.warn("[Invoice]: [self]: [comment]: Stuff Not provided!")
        return self.pcomment
    def hidden_message(self):
        if self.phidden_message == "not_provided_stuff":
            warnings.warn("[Invoice]: [self]: [hidden_message]: Stuff Not provided!")
        return self.phidden_message
    def payload(self):
        if self.ppayload == "not_provided_stuff":
            warnings.warn("[Invoice]: [self]: [payload]: Stuff Not provided!")
        return self.ppayload
    def invoice_id(self):
        return self.pinvoice_id