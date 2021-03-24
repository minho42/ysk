import json
import re
from datetime import datetime
from typing import Callable

import requests
from core.utils import get_chromedriver, timeit
from django.utils import timezone
from lxml import html
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .models import Currency
from .serializers import CurrencySerializer

BASE_AMOUNT = 1000
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
)


class CurrencyHome(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    http_method_names = ["get"]

    def get(self, request):
        return Response({"data": "It's working!"})


class CurrencyAPIViewData(generics.ListAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CurrencySerializer
    http_method_names = ["get"]

    def get_queryset(self):
        return Currency.objects.order_by("-real_rate", "name")


class ChromeScraper:
    def __init__(self):
        self.driver = get_chromedriver(headless=True)

    def __del__(self):
        if self.driver:
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        if self.driver:
            self.driver.quit()


def round_it(rate: float, ndigits: int = 2) -> float:
    return round(float(rate), ndigits)


def get_real_rate(rate: float, fee: float) -> float:
    """Real reate with fees applied"""
    rate = float(rate)
    fee = float(fee)

    if not fee or fee == 0:
        return rate
    return round(((BASE_AMOUNT - fee) * rate), 2) / BASE_AMOUNT


def scrape_gomtransfer():
    # https://www.gomtransfer.com/apilayer.php?key=check567890check56991&_=1576498334524
    # XHR 로 받은 네이버기준환율 (실시간아님) 에서 8원을 빼도록 계산됨
    # selenium 안쓰려면 위와같이 계산하기?

    driver = get_chromedriver()

    url = "https://www.gomtransfer.com/"
    try:
        driver.get(url)
    except TimeoutException:
        driver.quit()
        return (0.0, 0.0)

    try:
        element = WebDriverWait(driver, 10).until(
            # 네이버 기준환율 Loading... -> 네이버 기준환율 xxx.xx원
            EC.text_to_be_present_in_element(
                (By.XPATH, "//label[@id='auau']"), "원"
            )  # This is much faster than "presence_of_element_located"
        )
    except NoSuchElementException:
        return (0.0, 0.0)
    finally:
        try:
            rate = driver.find_element_by_xpath("//td[@id='hohans']").text
        except NoSuchElementException:
            rate = 0

        driver.quit()

        if rate:
            rate = re.findall(r"[\d,.]+", rate.strip())[0]
            # TODO Make sure the fee is correct
            fee = 0
            return (rate, fee)
        else:
            return (0.0, 0.0)


def scrape_wontop():
    driver = get_chromedriver()

    url = "http://www.wontop.com.au/"
    try:
        driver.get(url)
    except TimeoutException:
        driver.quit()
        return (0.0, 0.0)

    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "//div/aside[@id='text-11']")))
    except NoSuchElementException:
        return (0.0, 0.0)
    finally:
        # <iframe class="resp-iframe" style="height: 210px;" src="http://wontop.com.au/wp-content/myfiles/au2kr9.php" frameborder="0"></iframe>
        iframe = driver.find_element_by_xpath("//iframe[@class='resp-iframe']")
        driver.switch_to.frame(iframe)

        try:
            rate = driver.find_element_by_xpath("//div[@id='rate']/strong").text
        except NoSuchElementException:
            rate = 0

        driver.quit()

        if rate:
            rate = re.findall(r"[\d,.]+", rate.strip())[0]
            # TODO Make sure the fee is correct
            fee = 0
            return (rate, fee)
        else:
            return (0.0, 0.0)


def scrape_dondirect():
    # 돈다이렉트
    # Using selenium to scrape as they used angular
    driver = get_chromedriver()

    url = "https://dondirect.com.au/"
    try:
        driver.get(url)
    except TimeoutException:
        driver.quit()
        return (0.0, 0.0)

    try:
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "ng-binding")))
    except NoSuchElementException:
        return (0.0, 0.0)
    finally:
        try:
            rate = driver.find_element_by_xpath(
                "/html/body/div[2]/div/div[1]/md-content/div/span/div[1]/div[1]/div[1]/center/span"
            ).text
        except NoSuchElementException:
            rate = 0

        # 입금가능 / 입금불가
        try:
            note = driver.find_element_by_xpath(
                "/html/body/div[2]/div/div[1]/md-content/div/span/div[1]/div[1]/div[1]/center[2]/div/div"
            ).text
            if not "입금불가" in note:
                note = None
        except:
            note = None

        driver.quit()

        if rate:
            rate = re.findall(r"[\d,.]+", rate.strip())[0]
            # TODO Make sure the fee is correct
            fee = 0
            return (rate, fee, note)
        else:
            return (0.0, 0.0, note)


def scrape_instarem():
    # Instarem
    # Using XHR

    url = f"https://www.instarem.com/api/v1/public/transaction/computed-value?source_currency=AUD&destination_currency=KRW&instarem_bank_account_id=135&source_amount={BASE_AMOUNT}"
    s = requests.session()
    r = s.get(url=url)
    rr = json.loads(r.text)

    try:
        #
        rate = rr["data"]["destination_amount"] / BASE_AMOUNT
        fee = rr["data"]["transaction_fee_amount"]
    except KeyError:
        rate = 0
        fee = 0

    return (rate, fee)


def scrape_remitly():
    # Remitly
    # Using XHR

    url = f"https://api.remitly.io/v2/pricing/estimates?amount={BASE_AMOUNT}%20AUD&anchor=SEND&conduit=AUS%3AAUD-KOR%3AKRW"
    s = requests.session()
    r = s.get(url=url)
    rr = json.loads(r.text)

    data = {}
    for res in rr:
        # BANK / DEBIT / CREDIT
        if "payment_method" in res and res["payment_method"].upper() == "DEBIT":
            data = res

    try:
        rate = data["exchange_rate_info"]["base_rate"]
        # e.g. fee: 3.99 AUD
        fee = data["fee_info"]["product_fee_amount"]
    except KeyError:
        rate = 0
        fee = 0

    if rate:
        rate = re.findall(r"[\d,.]+", rate.strip())[0]
        if fee:
            fee = re.findall(r"[\d,.]+", fee.strip())[0]
        # note = "프로모션 적용안함; 수수료 Express delivery 기준"
        # return (rate, fee, note)
        return (rate, fee)
    else:
        return (0.0, 0.0)
    return (rate, fee)


def scrape_wirebarley():
    # 와이어바알리
    # Using XHR

    url = "https://www.wirebarley.com/api/data/composition"
    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-AU,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "Connection": "keep-alive",
        "Cookie": "_ga=GA1.2.455691707.1556844022; __zlcmid=s7iCuUgrnol1nf; wbLocaleCookie=en; _gid=GA1.2.1493689065.1559657242; _gat=1",
        "Host": "www.wirebarley.com",
        "iosVer": "9999",
        "lang": "en",
        "Referer": "https://www.wirebarley.com/",
        "user-agent": USER_AGENT,
        "X-Requested-With": "XMLHttpRequest",
    }
    s = requests.session()
    r = s.get(url=url, headers=headers)

    url2 = "https://www.wirebarley.com/api/tx/exrate/AU/AUD"
    r = s.get(url=url2, headers=headers)
    rr = json.loads(r.text)

    # rr['data']['exRates']['KR'][0]['wbRateData']
    # e.g. 199: 829.2932748 / 200: 829.628309
    # 'wbRateData':
    #     {'threshold': 200.0,
    #     'wbRate': 829.2932748,
    #     'threshold1': 500.0,
    #     'wbRate1': 829.628309,
    #     'threshold2': 1000.0,
    #     'wbRate2': 829.7958261,
    #     'threshold3': None,
    #     'wbRate3': 830.0471017,
    #     'threshold4': None,
    #     'wbRate4': None,
    #     'threshold5': None,
    #     'wbRate5': None,
    #     'threshold6': None,
    #     'wbRate6': None,
    #     'threshold7': None,
    #     'wbRate7': None,
    #     'threshold8': None,
    #     'wbRate8': None,
    #     'wbRate9': None,
    #     'wbBonusRate': None}

    #  e.g. 2999: 2.29 / 3000: 1.99
    #  'transferFees': [{'option': 'BANK_ACCOUNT_KR',
    #     'maxTransferAmount': None,
    #     'country': 'KR',
    #     'currency': 'KRW',
    #     'useDiscountFee': False,
    #     'min': 50.0,
    #     'fee1': 2.49,
    #     'discountFee1': 0.0,
    #     'threshold1': 1000.0,
    #     'fee2': 2.29,
    #     'discountFee2': 0.0,
    #     'threshold2': 3000.0,
    #     'fee3': 1.99,
    #     'discountFee3': 0.0,
    #     'max': 6500.0}],

    try:
        rate = rr["data"]["exRates"]["KR"][0]["wbRateData"]["wbRate3"]
        fee = rr["data"]["exRates"]["KR"][0]["transferFees"][0]["fee2"]
    except KeyError:
        rate = 0
        fee = 0
    # note = "3000불이상 수수료할인"
    # return (rate, fee, note)
    return (rate, fee)


def scrape_wise():
    # Transferwise -> wise
    # Using XHR
    url = "https://wise.com/gateway/v3/quotes/"

    headers = {
        "authority": "wise.com",
        "pragma": "no-cache",
        "path": "/gateway/v3/quotes/",
        "scheme": "https",
        "accept": "application/json",
        "accept-encoding": "gzip, deflate",  # <- adding 'br' breaks the result encoding
        "accept-language": "en-GB",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "origin": "https://wise.com",
        "referer": "https://wise.com/au",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "time-zone": "+1100",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
        "x-access-token": "Tr4n5f3rw153",
        # "referrerPolicy": "strict-origin-when-cross-origin",
    }

    data = json.dumps(
        {
            "guaranteedTargetAmount": "false",
            "preferredPayIn": "null",
            "sourceAmount": BASE_AMOUNT,
            "sourceCurrency": "AUD",
            "targetCurrency": "KRW",
        }
    )
    r = requests.post(url=url, headers=headers, data=data)  # without json.dumps() gets 400 error
    rr = json.loads(r.text)

    fee_data = {}
    for payment_option in rr["paymentOptions"]:
        """
        # 'payIn': rr['paymentOptions]['payIn'] options
        OSKO
        BANK_TRANSFER
        POLI
        DEBIT
        CREDIT
        MC_DEBIT_OR_PREPAID
        INTERNATIONAL_DEBIT
        MC_BUSINESS_CREDIT
        MC_CREDIT
        INTERNATIONAL_CREDIT
        CARD
        MAESTRO
        MC_BUSINESS_DEBIT
        VISA_BUSINESS_DEBIT
        VISA_CREDIT
        VISA_DEBIT_OR_PREPAID
        VISA_BUSINESS_CREDIT
        BALANCE
        """
        if payment_option["payIn"] == "BANK_TRANSFER":
            fee_data = payment_option
    try:
        rate = rr["rate"]
        fee = fee_data["fee"]["total"]
    except KeyError:
        rate = 0
        fee = 0
    return (rate, fee)


# def scrape_transferwise():
#     # Using XHR
#     url = f"https://transferwise.com/gateway/v3/comparisons?sendAmount={BASE_AMOUNT}&sourceCurrency=AUD&targetCurrency=KRW"
#     r = requests.get(url)
#     rr = json.loads(r.text)
#     real_rate = 0
#     try:
#         for provider in rr["providers"]:
#             if provider["name"].strip() == "TransferWise":
#                 rate = provider["quotes"][0]["rate"]
#                 fee = provider["quotes"][0]["fee"]
#     except KeyError:
#         rate = 0
#         fee = 0
#     return (rate, fee)


def get_timestamp():
    now = datetime.now()
    ts = datetime.timestamp(now)
    return int(ts)


def scrape_commbank():
    # Commbank, foreign exchange rates
    # Using XHR
    timestamp = get_timestamp()
    url = f"https://www.commbank.com.au/content/data/forex-rates/AUD.json?dt={timestamp}"
    r = requests.get(url)
    rr = json.loads(r.text)

    try:
        for currency in rr["currencies"]:
            if currency["currencyTitle"] == "KRW":
                rate = currency["bsImt"]
                break
    except KeyError:
        pass

    fee = 0
    fee_url = "https://www.commbank.com.au/personal/international/international-money-transfer.html"
    r = requests.get(fee_url)
    node = html.fromstring(r.content)
    try:
        text = node.xpath('//div[@class="target parbase"]//p')[0].text
        fee = re.findall(r"\$([\d,.]+)", text.strip())[0]
    except:
        fee = 0

    return (rate, fee)


def scrape_currency(url, xpath, rate_regex="[\d,.]+"):
    s = requests.session()
    headers = {"user-agent": USER_AGENT}
    r = s.get(url, headers=headers)
    node = html.fromstring(r.content)
    rate = node.xpath(xpath)
    if len(rate) <= 0:
        return 0.0
    rate = rate[0].text.strip()
    rate = re.findall(rf"{rate_regex}", rate)[0]
    return rate


def scrape_naver_usd():
    rate = scrape_currency(
        "https://finance.naver.com/marketindex/exchangeDetail.nhn?marketindexCd=FX_USDKRW",
        '//table[@class="tbl_calculator"]/tbody/tr/td[1]',
    )
    rate = rate.replace(",", "")
    return rate


def scrape_naver_aud():
    rate = scrape_currency(
        "https://finance.naver.com/marketindex/exchangeDetail.nhn?marketindexCd=FX_AUDKRW",
        '//table[@class="tbl_calculator"]/tbody/tr/td[1]',
    )
    rate = rate.replace(",", "")
    fee = 0
    return (rate, fee)


def scrape_ria():
    pass
    """
curl 'https://riamoneytransfer.com/api/MoneyTransferCalculator/Calculate' \
  -H 'Connection: keep-alive' \
  -H 'Pragma: no-cache' \
  -H 'Cache-Control: no-cache' \
  -H 'sec-ch-ua: "Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"' \
  -H 'CultureCode: en-AU' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIzZTFjN2M2Zi01ZTU4LTRmMTAtOTQxYy0xNGQ3YTViMDc3ZWEiLCJpYXQiOjE2MTY1MDcyMTgsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiIxNDEuMTY4LjE3OC4yMzIiLCJybXRFbWFpbCI6IjE0MS4xNjguMTc4LjIzMiIsInNlc3Npb25DYWNoZUtleSI6ImMzMzY0NTA2LTA0MjYtNDE5Zi04N2Q4LWY1OTljNjdjMmVlNSIsImlwSXNvQ29kZSI6IkFVIiwiY2xpZW50SXBBZGRyZXNzIjoiMTQxLjE2OC4xNzguMjMyIiwiY2xpZW50VHlwZSI6IldlYiIsImlzb0NvZGUiOiJBVSIsInNlc3Npb25DdWx0dXJlQ29kZSI6ImVuLUFVIiwiY3VsdHVyZUNvZGUiOiJlbi1BVSIsIlNlc3Npb25JZCI6IjEzOTM5OTUwMDQiLCJuYmYiOjE2MTY1MDcyMTgsImV4cCI6MTYxNjUwODQxOCwiaXNzIjoiQXV0aFNlcnZlciIsImFwaVRva2VuIjoiZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SnBjM01pT2lKelpYTnphVzl1SUdsemMzVmxjaUlzSW1GMVpDSTZJbWgwZEhBNkx5OXpaWE56YVc5dUxuUjBJaXdpYm1KbUlqb3hOakUyTlRBM01qRTRMQ0psZUhBaU9qRTJNVFkxTVRBNE1UZ3NJbXAwYVNJNkltTmpNVFF4WlRJeExUUmxZbVF0TkRjM1pDMDVaVFJoTFdZMU0yTm1ZMlZqTTJOak5TSXNJbWxoZENJNklqRTJNVFkxTURjd01qY2lMQ0pEYkdsbGJuUlVlWEJsSWpvaVYyVmlJaXdpVTJWeWRtVnlTWEJCWkdSeVpYTnpJam9pTVRReExqRTJPQzR4TnpndU1qTXlMQ0F4TUM0ek1TNDRNQzR4TXpnaUxDSkRiR2xsYm5SSmNFRmtaSEpsYzNNaU9pSXhOREV1TVRZNExqRTNPQzR5TXpJaUxDSm9kSFJ3T2k4dlEzVnpkRzl0WlhKVFpYSjJhV05sVkc5dmJHdHBkQzV5YVdGbGJuWnBZUzV1WlhRdmFXUmxiblJwZEhrdlkyeGhhVzF6TDFObGMzTnBiMjVKUkNJNklqRXpPVE01T1RVd01EUWlMQ0oxYm1seGRXVmZibUZ0WlNJNklrRjFRWEJwSWl3aVlYVjBhRjkwYVcxbElqb2lNeTh5TXk4eU1ESXhJREU2TkRNNk5EWWdVRTBpTENKaGRYUm9iV1YwYUc5a0lqb2lhSFIwY0RvdkwzTmphR1Z0WVhNdWJXbGpjbTl6YjJaMExtTnZiUzkzY3k4eU1EQTRMekEyTDJsa1pXNTBhWFI1TDJGMWRHaGxiblJwWTJGMGFXOXViV1YwYUc5a0wzQmhjM04zYjNKa0lpd2lRV2RsYm5SQmNHbFZjMlZ5Ym1GdFpTSTZJa0YxUVhCcElpd2lVbVZqWldsMmFXNW5RV2RsYm5SSlpDSTZJalF6T0RFMU9ERXhJaXdpUVd4c2IzZEZiV0ZwYkZObGJtUnBibWNpT2lKMGNuVmxJaXdpUVd4c2IzZEpjRUZrWkhKbGMzTlZibUpzYjJOcmFXNW5Jam9pZEhKMVpTSXNJa0ZzYkc5M1QzSmtaWEpNYjI5cmRYQnpJam9pZEhKMVpTSjkubWZyYzFxMU4zWmN5NHd1SE5Uel84SE1lOW4yLTNKWFhUN05sTFRuR25BayIsImF1ZCI6IlJNVFdlYiJ9.a5OcCECKuMHwLn4guhgWMrIdx53pFX8U-NMegqQaQKM' \
  -H 'Current-Page: https://riamoneytransfer.com/au/en' \
  -H 'Accept: application/json, text/plain, */*' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36' \
  -H 'IsoCode: AU' \
  -H 'Content-Type: application/json;charset=UTF-8' \
  -H 'Origin: https://riamoneytransfer.com' \
  -H 'Sec-Fetch-Site: same-origin' \
  -H 'Sec-Fetch-Mode: cors' \
  -H 'Sec-Fetch-Dest: empty' \
  -H 'Referer: https://riamoneytransfer.com/au/en' \
  -H 'Accept-Language: en-AU,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,en-GB;q=0.6,en-US;q=0.5' \
  -H 'Cookie: TS013e9518=015d3c15350d823ca19ecb935216e8f4bd0a2870a3e19b22a0ac725baab1ce06400453bce22fb88102b1a2da52f845b1b52ecbd088; TS013e9518030=0123d1b1a707e030ee3286658288043c7539d9023fa9384c414e7a06d65a4c21f679513ce025a88dcb6574a7c5c71df89fed34c89a; TSb08f6b3d027=08870df200ab2000cb2f9affdda6dfb6c388198fe2026cdd416385ba745b08f30eedb066f22541770862ddf77211300021bcc1a07a113d40433ecc2bb0e349360ff545e163811565b4f0752c71b4f8a55673716462ea1ee5485e1e7c1f82d1a6; TOKEN=%7B%22jwtToken%22%3A%22eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiIzZTFjN2M2Zi01ZTU4LTRmMTAtOTQxYy0xNGQ3YTViMDc3ZWEiLCJpYXQiOjE2MTY1MDcyMTgsImh0dHA6Ly9zY2hlbWFzLnhtbHNvYXAub3JnL3dzLzIwMDUvMDUvaWRlbnRpdHkvY2xhaW1zL25hbWUiOiIxNDEuMTY4LjE3OC4yMzIiLCJybXRFbWFpbCI6IjE0MS4xNjguMTc4LjIzMiIsInNlc3Npb25DYWNoZUtleSI6ImMzMzY0NTA2LTA0MjYtNDE5Zi04N2Q4LWY1OTljNjdjMmVlNSIsImlwSXNvQ29kZSI6IkFVIiwiY2xpZW50SXBBZGRyZXNzIjoiMTQxLjE2OC4xNzguMjMyIiwiY2xpZW50VHlwZSI6IldlYiIsImlzb0NvZGUiOiJBVSIsInNlc3Npb25DdWx0dXJlQ29kZSI6ImVuLUFVIiwiY3VsdHVyZUNvZGUiOiJlbi1BVSIsIlNlc3Npb25JZCI6IjEzOTM5OTUwMDQiLCJuYmYiOjE2MTY1MDcyMTgsImV4cCI6MTYxNjUwODQxOCwiaXNzIjoiQXV0aFNlcnZlciIsImFwaVRva2VuIjoiZXlKMGVYQWlPaUpLVjFRaUxDSmhiR2NpT2lKSVV6STFOaUo5LmV5SnBjM01pT2lKelpYTnphVzl1SUdsemMzVmxjaUlzSW1GMVpDSTZJbWgwZEhBNkx5OXpaWE56YVc5dUxuUjBJaXdpYm1KbUlqb3hOakUyTlRBM01qRTRMQ0psZUhBaU9qRTJNVFkxTVRBNE1UZ3NJbXAwYVNJNkltTmpNVFF4WlRJeExUUmxZbVF0TkRjM1pDMDVaVFJoTFdZMU0yTm1ZMlZqTTJOak5TSXNJbWxoZENJNklqRTJNVFkxTURjd01qY2lMQ0pEYkdsbGJuUlVlWEJsSWpvaVYyVmlJaXdpVTJWeWRtVnlTWEJCWkdSeVpYTnpJam9pTVRReExqRTJPQzR4TnpndU1qTXlMQ0F4TUM0ek1TNDRNQzR4TXpnaUxDSkRiR2xsYm5SSmNFRmtaSEpsYzNNaU9pSXhOREV1TVRZNExqRTNPQzR5TXpJaUxDSm9kSFJ3T2k4dlEzVnpkRzl0WlhKVFpYSjJhV05sVkc5dmJHdHBkQzV5YVdGbGJuWnBZUzV1WlhRdmFXUmxiblJwZEhrdlkyeGhhVzF6TDFObGMzTnBiMjVKUkNJNklqRXpPVE01T1RVd01EUWlMQ0oxYm1seGRXVmZibUZ0WlNJNklrRjFRWEJwSWl3aVlYVjBhRjkwYVcxbElqb2lNeTh5TXk4eU1ESXhJREU2TkRNNk5EWWdVRTBpTENKaGRYUm9iV1YwYUc5a0lqb2lhSFIwY0RvdkwzTmphR1Z0WVhNdWJXbGpjbTl6YjJaMExtTnZiUzkzY3k4eU1EQTRMekEyTDJsa1pXNTBhWFI1TDJGMWRHaGxiblJwWTJGMGFXOXViV1YwYUc5a0wzQmhjM04zYjNKa0lpd2lRV2RsYm5SQmNHbFZjMlZ5Ym1GdFpTSTZJa0YxUVhCcElpd2lVbVZqWldsMmFXNW5RV2RsYm5SSlpDSTZJalF6T0RFMU9ERXhJaXdpUVd4c2IzZEZiV0ZwYkZObGJtUnBibWNpT2lKMGNuVmxJaXdpUVd4c2IzZEpjRUZrWkhKbGMzTlZibUpzYjJOcmFXNW5Jam9pZEhKMVpTSXNJa0ZzYkc5M1QzSmtaWEpNYjI5cmRYQnpJam9pZEhKMVpTSjkubWZyYzFxMU4zWmN5NHd1SE5Uel84SE1lOW4yLTNKWFhUN05sTFRuR25BayIsImF1ZCI6IlJNVFdlYiJ9.a5OcCECKuMHwLn4guhgWMrIdx53pFX8U-NMegqQaQKM%22%2C%22expiresInSeconds%22%3A1200%2C%22issuedAt%22%3A%221616507027%22%2C%22tokenType%22%3A%22bearer%22%7D' \
  --data-raw '{"Selections":{"countryTo":"KR","stateTo":null,"currencyTo":null,"currencyFrom":"AUD","paymentMethod":null,"deliveryMethod":null,"amountFrom":1000,"amountTo":null,"agentToId":null,"agentToLocationId":null,"promoCode":null,"promoId":0,"transferReason":null,"shouldCalcAmountFrom":false}}' \
  --compressed
    """


def scrape_orbitremit():
    url = "https://www.orbitremit.com/api/rates"
    headers = {
        "authority": "www.orbitremit.com",
        "method": "POST",
        "path": "/api/rates",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-AU,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "cache-control": "no-cache",
        "content-type": "application/json",
        # TODO: cookies are static for now -> check if cookies change or are set dynamically
        "cookie": "__cfduid=d91dc221200fee64cc6ef8b8553f0bd561616507020; sendCurrency=AUD; track=%5B%7B%22Params%22:%7B%22keyword%22:%22orbit%2520remit%22,%22matchtype%22:%22e%22,%22device%22:%22m%22,%22creative%22:%22337323736282%22,%22network%22:%22g%22,%22campaignid%22:%221729107244%22,%22adgroupid%22:%2267601175357%22,%22targetid%22:%22kwd-38866474671%22,%22loc_physical_ms%22:%229071758%22,%22_gcamp%22:%22Brand%22,%22gclid%22:%22Cj0KCQjwutaCBhDfARIsAJHWnHsQo1T4IDtf-6CQ2bdMkkXgAKfGjIlobJnpMR9rAxiKw8RSfGrOHkwaAqcSEALw_wcB%22%7D,%22Time%22:1616507022101%7D%5D",
        "origin": "https://www.orbitremit.com",
        "pragma": "no-cache",
        "referer": "https://www.orbitremit.com/",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    data = json.dumps({"amount": "%.2f" % BASE_AMOUNT, "focus": "send", "payout": "KRW", "send": "AUD"})
    s = requests.session()
    r = s.post(url=url, headers=headers, data=data)
    rr = json.loads(r.text)

    try:
        rate = rr["data"]["attributes"]["rate"]

        fee_url = f"https://www.orbitremit.com/api/fees?send=AUD&payout=KRW&amount={'%.2f' % BASE_AMOUNT}"
        r_fee = s.get(fee_url)
        rr_fee = json.loads(r_fee.text)
        fee = rr_fee["fee"] or 0  # It returns 'None' instead of 0 when there is no fee

    except (KeyError, IndexError):
        rate = 0
        fee = 0

    return (rate, fee)


def scrape_azimo():
    # Azimo
    # Using XHR

    url = f"https://api.azimo.com/service-rates/v1/public/en/prices/current?sendingCountry=AUS&sendingCurrency=AUD&receivingCountry=KOR&receivingCurrency=USD&deliveryMethod=SWIFT"
    headers = {
        "authority": "api.azimo.com",
        "method": "GET",
        "path": "/service-rates/v1/public/en/prices/current?sendingCountry=AUS&sendingCurrency=AUD&receivingCountry=KOR&receivingCurrency=USD&deliveryMethod=SWIFT",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-AU,en;q=0.9,ko-KR;q=0.8,ko;q=0.7,en-GB;q=0.6,en-US;q=0.5",
        "cache-control": "no-cache",
        "origin": "https://azimo.com",
        "pragma": "no-cache",
        "referer": "https://azimo.com/en/send-money-to-korea-republic-of",
        "sec-ch-ua": '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": USER_AGENT,
        "x-api-version": "3.27.0",
        "x-app-version": "LEGO-CLIENT,4.49.48",
        "x-application-calculator": "INDIVIDUAL",
        "x-azimo-utdm": "10407fcc-1be8-4231-bf15-d3b2da5dd434",
        "x-correlation-id": "LEGO-CLIENT-51e5fdfa-19ae-4c23-9d0f-6eeab29507d7",
        "x-platform-version": "2021.12",
    }
    s = requests.session()
    r = s.get(url=url, headers=headers)
    rr = json.loads(r.text)

    try:
        fee = rr["rates"][0]["adjustments"]["fee"]["max"]["was"]
        rate_in_usd = rate = rr["rates"][0]["adjustments"]["rate"]["value"]["was"]
        # Convert USD -> KRW
        usd_krw_rate = scrape_naver_usd()
        if usd_krw_rate:
            rate = float(rate_in_usd) * float(usd_krw_rate)
        else:
            print("Can't convert USD->KRW")
            return (0, 0)
    except (KeyError, IndexError):
        rate = 0
        fee = 0

    if rate:
        # note = "Receive in USD"
        note = f"USD->KRW: {rate_in_usd} x {usd_krw_rate} = {round_it(rate)}"

        return (rate, fee, note)

    return (rate, fee)


def scrape_stra():
    rate = scrape_currency("http://1472.com.au/", '//div[@class="aukr"]/div[@class="ex_bg"]/span')
    # TODO Login to scrape fee
    # NO FEE over $1000
    fee = 0
    return (rate, fee)


def scrape_wiztoss():
    # "1AUD = 813KRW" --> "813"
    rate = scrape_currency(
        "https://wiztoss.com/",
        "//h5[contains(text(), '1AUD')]",
        rate_regex="1AUD = ([\d,.]+)KRW",
    )
    s = requests.session()
    rr = s.get("https://wiztoss.com/faq-exchange-transfer")
    node2 = html.fromstring(rr.content)
    fee = node2.xpath("//h5[contains(text(), '수수료가 있나요')]/ancestor::div[@class='card-header']/following-sibling::div//p")
    if len(fee) <= 0:
        fee = 0
    fee = fee[0].text.strip()
    fee = re.findall(r"\$([\d,.]+)", fee)[0]

    return (rate, fee)


def save_currency(name: str, url: str, func: Callable) -> float:
    returned_values = func()
    if len(returned_values) == 2:
        (rate, fee) = func()
        note = None
    elif len(returned_values) == 3:
        (rate, fee, note) = func()
    else:
        print(f"save_currency returned wrong tuple values: {func.__name__}")
        rate = 0
        fee = 0
        note = None

    rate = round_it(rate)
    real_rate = get_real_rate(rate, fee)
    real_rate = round_it(real_rate)

    c, created = Currency.objects.update_or_create(
        name=name,
        defaults={
            "url": url,
            "rate": rate,
            "fee": fee,
            "real_rate": real_rate,
            "note": note,
            "modified": timezone.now(),
        },
    )
    return c


@timeit
def save_wise():
    return save_currency("Wise", "https://wise.com/au", scrape_wise)


@timeit
def save_wirebarley():
    return save_currency("WireBarley", "https://www.wirebarley.com", scrape_wirebarley)


@timeit
def save_remitly():
    return save_currency("Remitly", "https://www.remitly.com", scrape_remitly)


@timeit
def save_azimo():
    return save_currency("Azimo", "https://azimo.com/en/send-money-to-korea-republic-of", scrape_azimo)


@timeit
def save_orbitremit():
    return save_currency("OrbitRemit", "https://www.orbitremit.com", scrape_orbitremit)


@timeit
def save_instarem():
    return save_currency("InstaReM", "https://www.instarem.com/en-au", scrape_instarem)


@timeit
def save_wontop():
    return save_currency("Wontop", "http://www.wontop.com.au", scrape_wontop)


@timeit
def save_dondirect():
    return save_currency("DonDirect", "https://dondirect.com.au", scrape_dondirect)


@timeit
def save_gomtransfer():
    return save_currency("GomTransfer", "https://www.gomtransfer.com", scrape_gomtransfer)


@timeit
def save_naver():
    return save_currency(
        "Naver",
        "https://finance.naver.com/marketindex/exchangeDetail.nhn?marketindexCd=FX_AUDKRW",
        scrape_naver_aud,
    )


@timeit
def save_wiztoss():
    return save_currency("Wiztoss", "https://wiztoss.com", scrape_wiztoss)


@timeit
def save_commbank():
    return save_currency(
        "Commbank",
        "https://www.commbank.com.au/personal/international/foreign-exchange-rates.html?ei=cb-fx-calc-full-fx-list",
        scrape_commbank,
    )


@timeit
def save_stra():
    return save_currency("Stra", "http://1472.com.au", scrape_stra)

    # @timeit
    # def get_all():
    """
    No need to use "fetch_new_data" anymore since ditched chart/vue part
    Count how many companies are to be fetched
    Only save if the result count matches
    Same all results at once rather than one by one to prevent user only seeing partial results
    """
    # pass


@timeit
def fetch_new_data():
    # deleting all makes modified useless as created_at shares same value...
    # Currency.objects.all().delete()

    # # Using requests with lxml/xpath
    # save_naver(),
    # save_stra(),
    # save_wiztoss(),
    # # Using requests, XHR
    # save_commbank(),
    # save_wise(),
    # save_wirebarley(),
    # save_remitly(),
    # save_instarem(),
    # save_azimo(),
    save_orbitremit(),
    # # Using selenium
    # save_dondirect(),
    # save_wontop(),
    # save_gomtransfer(),
