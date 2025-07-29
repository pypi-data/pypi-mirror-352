import json
from requests import get, post
from .types.Invoice import Invoice
from .types.Check import Check
from .types.Transfer import Transfer
from .types.Balance import Balance
from .types.ExchangeRate import ExchangeRate
from .types.Currencies import Currencies
from .types.AppStats import AppStats


class CryptoBot():
    def __init__(self, api_key: str, isTestnet = False):
        """
        CryptoBot is class for using the library
        Params:
        api_key = using for communicate with the cryptobot api
        isTestnet = (Optional) Using for testing the bot with testnet
        """

        self.headers = {'Content-Type': 'application/json', 'Crypto-Pay-API-Token': api_key}  
        if isTestnet:
            self.url = "https://testnet-pay.crypt.bot/api"
        else:
            self.url = "https://pay.crypt.bot/api"

    def createInvoice(self, 
                           amount: str,
                           asset: str, 
                           fiat = None,
                           accepted_assets = None,
                           descriptoion = None,
                           hidden_message = None,
                           paid_btn_name = None,
                           paid_btn_url = None,
                           payload = None,
                           expires_in = None,
                           allow_comments = True,
                           allow_anonymous = True,
                           currency_type = "crypto"):
        """
        createInvoice - function for creating a payment invoice
        
        Params:
            amount {string} - amount of the invoice, in fload
            asset {string}- Currency code, (BTC, TON, ETH)
            fiat {string} | Optional - Fiat code, (RUB, EUR, USD)
            accepted_assets {string} | Optional - List of cryptocurrency alphabetic codes separated comma. Assets which can be used to pay the invoice. Available only if currency_type is “fiat”. 
            descriptoion {string} | Optional - description of invoice
            hidden_message {string} | Optional - Text of the message which will be presented to a user after the invoice is paid. Up to 2048 characters.
            paid_btn_name {string} | Optional - Label of the button which will be presented to a user after the invoice is paid ( viewItem , openChannel , openBot , callback )
            paid_btn_url {string} | Optional - Required if paid_btn_name is specified. URL opened using the button which will be presented to a user after the invoice is paid. You can set any callback link 
            payload {string} | Optional - Any data you want to attach to the invoice (for example, user ID, payment ID, ect). Up to 4kb.
            expires_in {int} | Optional - You can set a payment time limit for the invoice in seconds. Values between 1-2678400 are accepted
            allow_comments {bool} | Optional - allow comments
            allow_anonymous {bool} | Optional - allow anonymous pay
            currency_type {string} | Optional - crypto or fiat):

        Responce
            Invoice - Invoice DataClass       
        """
        
        data_payload = {
            "currency_type": currency_type,
            "amount": amount,
            "asset": asset,
            "allow_anonymous": allow_anonymous,
            "allow_comments": allow_comments
        }

        if fiat is not None: data_payload.update({"fiat": fiat})
        if accepted_assets is not None: data_payload.update({"accepted_assets": accepted_assets})
        if descriptoion is not None: data_payload.update({"descriptoion": descriptoion})
        if hidden_message is not None: data_payload.update({"hidden_message": hidden_message})
        if paid_btn_name is not None: data_payload.update({"paid_btn_name": paid_btn_name})
        if paid_btn_url is not None: data_payload.update({"paid_btn_url": paid_btn_url})
        if payload is not None: data_payload.update({"payload": payload})
        if expires_in is not None: data_payload.update({"expires_in": expires_in})

        req = post(f"{self.url}/createInvoice", json=data_payload, headers=self.headers)
        jsonobj = json.loads(json.dumps(req.json()))["result"]

        # FIXME: Implement the items loop, because cryptobot can give a items list
        if "items" in jsonobj:
            pass

        comment_res = "not_provided_stuff"
        if "comment" in jsonobj: comment_res = jsonobj['comment']
        hidden_message_res = "not_provided_stuff"
        if "hidden_message" in jsonobj: hidden_message_res = jsonobj['comment']
        payload_res = "not_provided_stuff"
        if "payload" in jsonobj: payload_res = jsonobj['payload']
        

        return Invoice(
            invoice_id=jsonobj['invoice_id'],
            hash=jsonobj['hash'],
            currency_type=jsonobj['currency_type'],
            amount=jsonobj['amount'],
            bot_invoice_url=jsonobj['bot_invoice_url'],
            mini_app_invoice_url=jsonobj['mini_app_invoice_url'],
            web_app_invoice_url=jsonobj['web_app_invoice_url'],
            status=jsonobj['status'],
            created_at=jsonobj['created_at'],
            comment=comment_res,
            hidden_message=hidden_message_res,
            payload=payload_res
        )
    
    def getInvoices(self,
                    asset = None,
                    fiat = None,
                    invoice_ids = None,
                    status = None,
                    offset = None,
                    count = None):
        data_payload = {}
        if fiat is not None: data_payload.update({"fiat": fiat})
        if invoice_ids is not None: data_payload.update({"invoice_ids": invoice_ids})
        if status is not None: data_payload.update({"status": status})
        if asset is not None: data_payload.update({"asset": asset})
        if offset is not None: data_payload.update({"offset": offset})
        if count is not None: data_payload.update({"count": count})

        items = []

        req = get(f"{self.url}/getInvoices", headers=self.headers, json=data_payload)
        for i in req.json()["result"]["items"]:
            comment_res = "not_provided_stuff"
            if "comment" in i: comment_res = i['comment']
            hidden_message_res = "not_provided_stuff"
            if "hidden_message" in i: hidden_message_res = i['comment']
            payload_res = "not_provided_stuff"
            if "payload" in i: payload_res = i['payload']
            items.append(Invoice(
                invoice_id=i['invoice_id'],
                hash=i['hash'],
                currency_type=i['currency_type'],
                amount=i['amount'],
                bot_invoice_url=i['bot_invoice_url'],
                mini_app_invoice_url=i['mini_app_invoice_url'],
                web_app_invoice_url=i['web_app_invoice_url'],
                status=i['status'],
                created_at=i['created_at'],
                comment=comment_res,
                hidden_message=hidden_message_res,
                payload=payload_res
            ))
        return items
    
    
    def checkInvoice(self, invoice: Invoice):
        """
        checkInvoice - Check invoice Status
        Params:
            invoice {Invoice} - Invoice DataClass

        Responce: 
            have a three station
                active
                paid
                expierd
        """
        invoice_id = invoice.invoice_id()
        req = self.getInvoices(invoice_ids=invoice_id)
        if req[0]:
            return req[0].status()
        else:
            return "notfound"
        
    def deleteInvoice(self, invoice: Invoice):
        """
        deleteInvoice - delete a invoice created by your app
        Params:
            invoice {Invoice} - invoice dataclass

        Responce:
            fail - on error
            succes - on succes

        """
        data_payload = {"invoice_id": invoice.invoice_id()}
        res = post(f"{self.url}/deleteInvoice", json=data_payload, headers=self.headers)
        if res.status_code != 200:
            return "fail"
        return "succes"

    def createCheck(self,
                    amount: str,
                    asset = "USDT",
                    pin_to_user_id = None,
                    pin_to_username = None
                    ):
        
        """
        createCheck - Function for creating checks using app balance

        WARNING: for use this u need to enable checks in app settings!

        Params:

            amount {string} - amount of check
            asset {string} | Optional - asset, currently, can be “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC”, default is USDT
            pin_to_user_id {int} | Optional - pin check only for user, pin by userid
            pin_to_username {string} | Optional - pin check only for user, pin by username

        Responce:

            Check - Check DataClass
        """

        data_payload = {
            "asset": asset,
            "amount": amount
        }
        if pin_to_user_id is not None: data_payload.update({"pin_to_user_id": pin_to_user_id})
        if pin_to_username is not None: data_payload.update({"pin_to_username": pin_to_username})

        req = post(f"{self.url}/createCheck", json=data_payload, headers=self.headers)

        if req.json()["ok"] == False:
            return f"Error code: {req.json()["error"]["code"]} | name: {req.json()["error"]["name"]}"
        
        activated_at_res = "check_not_activated"
        if req.json()["result"]["status"] == "activated": activated_at_res = req.json()["result"]["activated_at"]
        
        return Check(check_id=req.json()["result"]["check_id"],
                     hash=req.json()["result"]["hash"],
                     asset=req.json()["result"]["asset"],
                     amount=req.json()["result"]["amount"],
                     bot_check_url=req.json()["result"]["bot_check_url"],
                     status=req.json()["result"]["status"],
                     created_at=req.json()["result"]["created_at"],
                     activated_at=activated_at_res)
    
    def deleteCheck(self, check: Check):
        """
        deleteCheck - Use this method to delete checks created by your app. Returns True on success
        Params:
            check {Check} - check dataclass

        Responce:
            fail - on error
            succes - on succes

        """
        data_payload = {"check_id": check.check_id()}
        res = post(f"{self.url}/deleteCheck", json=data_payload, headers=self.headers)
        if res.status_code != 200:
            return "fail"
        return "succes"
    
    def getChecks(self, 
                  asset = None,
                  check_ids = None,
                  status = None,
                  offset = None,
                  count = None):
        data_payload = {}
        if asset is not None: data_payload.update({"asset": asset})
        if check_ids is not None: data_payload.update({"check_ids": check_ids})
        if status is not None: data_payload.update({"status": status})
        if offset is not None: data_payload.update({"offset": offset})
        if count is not None: data_payload.update({"count": count})

        items = []

        req = get(f"{self.url}/getChecks", headers=self.headers, json=data_payload)
        for i in req.json()["result"]["items"]:
            activated_res = "check_not_activated"
            if "activated_at" in i: activated_res = i['activated_at']
            items.append(Check(
                check_id=i["check_id"],
                hash=i['hash'],
                asset=i["asset"],
                amount=i["amount"],
                bot_check_url=i["bot_check_url"],
                status=i["status"],
                created_at=i["created_at"],
                activated_at=activated_res
            ))
        return items
    
    def checkCheck(self, check: Check):
        """
        checkCheck - View Check Status
        Params:
            check {Check} - Check DataClass

        Responce: 
            have a three station
                active
                activated
        """
        check_id = check.check_id()
        req = self.getChecks(check_ids=check_id)
        if req[0]:
            return req[0].status()
        else:
            return "notfound"
        
    
    def transfer(self,
                 user_id: int,
                 amoun: str,
                 spend_id: str,
                 asset = "USDT",
                 comment = None,
                 disable_send_notification = False):
        
        """
        Transfer - Use this method to send coins from your app's balance to a user. On success, returns completed transfer.
        
        Params:

            user_id (Number) - User ID in Telegram. User must have previously used @CryptoBot (@CryptoTestnetBot for testnet).
            
            asset (String) - Cryptocurrency alphabetic code. Supported assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet).
            
            amount (String) - Amount of the transfer in float. The minimum and maximum amount limits for each of the supported assets roughly correspond to 1-25000 USD. Use getExchangeRates to convert amounts. For example: 125.50
            
            spend_id (String) - Random UTF-8 string unique per transfer for idempotent requests. The same spend_id can be accepted only once from your app. Up to 64 symbols.
            
            comment (String) - ​Optional. Comment for the transfer. Users will see this comment in the notification about the transfer. Up to 1024 symbols.
            
            disable_send_notification (Boolean) - ​Optional. Pass true to not send to the user the notification about the transfer. Defaults to false.

        Responce:

        Transfer datatype
        
        """
        data_payload = {
            "user_id": user_id,
            "amount": amoun,
            "spend_id": spend_id,
            "asset": asset
        }

        if comment is not None: data_payload.update({"comment": comment})
        if disable_send_notification is not None: data_payload.update({"disable_send_notification": disable_send_notification})
        
        req = get(f"{self.url}/transfer", headers=self.headers, json=data_payload)
        req_data = req.json()

        if req_data['ok'] == False:
            return f"error:code:{req_data["result"]["code"]}:name:{req_data["result"]["name"]}:message:{req_data["result"]["message"]}"
        
        commented = "comment_not_provided"
        if "comment" in req_data["result"]: commented = req_data["result"]['comment']
        return Transfer(
            transfer_id=req_data["result"]["transfer_id"],
            spend_id=req_data["result"]["spend_id"],
            user_id=req_data["result"]["user_id"],
            asset=req_data["result"]["asset"],
            amount=req_data["result"]["amount"],
            status=req_data["result"]["status"],
            completed_at=req_data["result"]["completed_at"],
            comment=commented,
            )
    
    def getTransfers(self,
                     asset = None,
                     transfer_ids = None,
                     spend_id = None,
                     offset = None,
                     count = None):
        
        """
        getTransfers - Use this method to get transfers created by your app. On success, returns array of Transfer
        Params: 
            asset (String) - Optional. Cryptocurrency alphabetic code. Supported assets: “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC” (and “JET” for testnet). Defaults to all currencies.

            transfer_ids (String) - ​Optional. List of transfer IDs separated by comma.

            spend_id (String) - Optional. Unique UTF-8 transfer string.

            offset (Number) - ​Optional. Offset needed to return a specific subset of transfers. Defaults to 0.

            count (Number) - ​Optional. Number of transfers to be returned. Values between 1-1000 are accepted. Defaults to 100.

        Responce:
            list of Transfer dataclass
        """

        data_payload = {}
        if asset is not None: data_payload.update({"asset": asset})
        if transfer_ids is not None: data_payload.update({"transfer_ids": transfer_ids})
        if spend_id is not None: data_payload.update({"transfer_ids": transfer_ids})
        if offset is not None: data_payload.update({"offset": offset})
        if count is not None: data_payload.update({"count": count})

        items = []

        req = get(f"{self.url}/getTransfers", headers=self.headers, json=data_payload)
        for i in req.json()["result"]["items"]:
            comment_res = "comment_not_avaliable"
            if "comment" in i: comment_res = i['comment']
            items.append(Transfer(
                transfer_id=i["transfer_id"],
                spend_id=i["spend_id"],
                user_id=i["user_id"],
                asset=i["asset"],
                amount=i["amount"],
                status=i["status"],
                completed_at=["completed_at"],
                comment=comment_res
            ))
        return items
    
    def getBalance(self, currency_code = None):
        """
        getBalance - Get Ur Balance in any of currency
        Params:
            currency_code (strng) - “USDT”, “TON”, “BTC”, “ETH”, “LTC”, “BNB”, “TRX” and “USDC”

        Responce:
            Balance Dataclass
        """
        req = get(f"{self.url}/getBalance", headers=self.headers)
        # FIXME: Make prettier error code responce
        if req.json()["result"] == False:
            return False
        
        for i in req.json()["result"]:
            if i["currency_code"] == currency_code:
                return Balance(currencry_code=i["currency_code"], available=i["available"], onhold=i["onhold"])
            
    def getExchangesRates(self):
        """
        getExchangesRate - Use this method to get exchange rates of supported currencies.
        Parameters:
            none
        
        Returns:
            array of ExchangeRate
        """
        req = get(url=f"{self.url}/getExchangeRates", headers=self.headers)

        if req.json()["ok"] == False:
            return "error"

        data_list = []
        for i in req.json()["result"]:
            data_list.append(ExchangeRate(
                is_valid=i["is_valid"],
                is_fiat=i["is_fiat"],
                is_crypto=i["is_crypto"],
                source=i["source"],
                target=i["target"],
                rate=i["rate"]
                ))
        
        return data_list

    def getExchangeRate(self, source: str, target: str):
        req = get(url=f"{self.url}/getExchangeRates", headers=self.headers)

        if req.json()["ok"] == False:
            return "error"
        
        for i in req.json()["result"]:
            if i["source"] == source and i["target"] == target:
                return ExchangeRate(
                    is_valid=i["is_valid"],
                    is_fiat=i["is_fiat"],
                    is_crypto=i["is_crypto"],
                    source=i["source"],
                    target=i["target"],
                    rate=i["rate"]
                )
        return ExchangeRate(
            is_valid="source_or_target_not_avaliable",
            is_fiat="source_or_target_not_avaliable",
            is_crypto="source_or_target_not_avaliable",
            source="source_or_target_not_avaliable",
            target="source_or_target_not_avaliable",
            rate="source_or_target_not_avaliable"
        )
            
    def getCurrencies(self):
        req = get(url=f"{self.url}/getCurrencies", headers=self.headers)

        if req.json()["ok"] == False:
            return Currencies(code="error", decimals="error", is_blockchain=False, is_fiat=False, is_stablecoin=False, name="error")
        
        data_list = []

        for i in req.json()["result"]:
            blockchain_url = "fiat" 
            if i["is_blockchain"] == True: blockchain_url == i["url"]  
            data_list.append(Currencies(
                code=i["code"],
                decimals=i["decimals"],
                is_blockchain=i["is_blockchain"],
                is_fiat=i["is_fiat"],
                is_stablecoin=i["is_stablecoin"],
                name=i["name"],
                url=blockchain_url
            ))
        return data_list


    def getCurrency(self, name: str):
        req = get(url=f"{self.url}/getCurrencies", headers=self.headers)

        if req.json()["ok"] == False:
            return Currencies(code="error", decimals="error", is_blockchain=False, is_fiat=False, is_stablecoin=False, name="error")
        
        
        for currency in req.json()["result"]:
            if currency["name"] == name:
                blockchain_url = "fiat" 
                if currency["is_blockchain"] == True: blockchain_url == currency["url"]  
                return Currencies(code=currency["code"], 
                                  decimals=currency["decimals"],
                                  is_blockchain=currency["is_blockchain"],
                                  is_fiat=currency["is_fiat"],
                                  is_stablecoin=currency["is_stablecoin"],
                                  name=currency["name"],
                                  url=blockchain_url)
            
        return Currencies(code="not_found", decimals="not_found", is_blockchain=False, is_fiat=False, is_stablecoin=False, name="not_found")
    
    def getStats(self, start_at = None, end_at = None):
        """
        getStats - Use this method to get app statistics. On success, returns AppStats
        
        Parameters:

            start_at (String) - ​Optional. Date from which start calculating statistics in ISO 8601 format. Defaults is current date minus 24 hours.
        
            end_at (String) - ​Optional. The date on which to finish calculating statistics in ISO 8601 format. Defaults is current date.
        """
        data_payload = {}
        if start_at is not None: data_payload.update({"start_at": start_at})
        if end_at is not None: data_payload.update({"end_at": end_at})
        req = get(f"{self.url}/getStats", headers=self.headers, json=data_payload)
        
        if req.json()["ok"] == False:
            return AppStats(volume="error", conversion="error", unique_users_count="error", created_invoice_count="error", paid_invoice_count="error", start_at="error", end_at="error")
        
        #return req.json()
        return AppStats(volume=req.json()["result"]["volume"], 
                        conversion=req.json()["result"]["conversion"], 
                        unique_users_count=req.json()["result"]["unique_users_count"], 
                        created_invoice_count=req.json()["result"]["created_invoice_count"], 
                        paid_invoice_count=req.json()["result"]["paid_invoice_count"], 
                        start_at=req.json()["result"]["start_at"], 
                        end_at=req.json()["result"]["end_at"])

        
        
        
        



