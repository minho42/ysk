import json
import requests

# TODO Where bearer token and cookies are from???

url = "https://riamoneytransfer.com/api/MoneyTransferCalculator/Calculate"
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-AU,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,en-GB;q=0.6,en-US;q=0.5",
    "Authorization": "",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Cookie": "",
    "CultureCode": "en-AU",
    "Current-Page": "https://riamoneytransfer.com/au/en",
    "Host": "riamoneytransfer.com",
    "IsoCode": "AU",
    "Origin": "https://riamoneytransfer.com",
    "Pragma": "no-cache",
    "Referer": "https://riamoneytransfer.com/au/en",
    "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
}
data = json.dumps(
    {
        "Selections": {
            "countryTo": "KR",
            "stateTo": "null",
            "currencyTo": "KRW",
            "currencyFrom": "AUD",
            "paymentMethod": "null",
            "deliveryMethod": "null",
            "amountFrom": "1000",
            "amountTo": "null",
            "agentToId": "null",
            "agentToLocationId": "null",
            "promoCode": "null",
            "promoId": 0,
            "transferReason": "null",
            "shouldCalcAmountFrom": "false",
        }
    }
)
s = requests.session()
r = s.post(url=url, headers=headers, data=data)
# print(vars(r))
rr = json.loads(r.text)
# print(rr)
# rate = rr[""]


"""
{'errors': [{'key': None, 'errorCode': 'InvalidRequest', 'issueId': None, 'values': None, 'message': 'Invalid input detected.', 'trackingId': None, 'friendlyMessage': None, 'link': None}]}
"""
