import datetime
import json
import os
import pprint
import re
import time
from functools import wraps
from typing import List, Tuple

import requests
from selenium import webdriver


# from django.apps import apps

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"


def timeit(func):
    @wraps(func)
    def closure(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        print("<%s> took %0.3fs." % (func.__name__, te - ts))
        return result

    return closure


def get_chromedriver(headless: bool = True) -> object:
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    if headless:
        options.add_argument("headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--remote-debugging-port=9222")
        # options.add_argument("--window-size=1920x1080")
    options.add_experimental_option("prefs", prefs)
    # options.add_argument(f'user-agent={USER_AGENT}')
    # options.add_argument("disable-infobars") --> flag removed: https://chromium.googlesource.com/chromium/src/+/d869ab3350d8ebd95222b4a47adf87ce3d3214b1
    # options.add_argument("--disable-extensions")
    # options.add_argument("--profile-directory=Default")
    # options.add_argument("--incognito")
    # options.add_argument("--disable-plugins-discovery")
    # options.add_argument("--start-maximized")
    # options.add_argument("--no-proxy-server")
    # driver = webdriver.Chrome(os.environ.get("CHROME_DRIVER_PATH"), options=options)

    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

    driver = webdriver.Chrome(
        executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=options
    )
    return driver


def get_all_fields(model) -> List[str]:
    # print('---------------------------')
    # pprint.pprint(model._meta.__dict__)
    # print('---------------------------')

    r = []
    try:
        r = [f.name for f in model._meta.__dict__["local_fields"]]
    except KeyError:
        pass
    else:
        pass
    return r


def get_m2m_fields(model) -> List[str]:
    # 'many_to_many' or 'local_many_to_many'
    return [f.name for f in model._meta.__dict__["local_many_to_many"]]


def get_all_fields_excluding(model, exclude_list: List[str]) -> List[str]:
    if type(exclude_list) is not list:
        raise TypeError("exclude_list must be list")

    include_list = get_all_fields(model)

    for i in include_list:
        for e in exclude_list:
            e = e.strip()
            if e in include_list:
                include_list.remove(e)

    return include_list
