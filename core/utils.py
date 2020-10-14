import os
import re
import time
from functools import wraps
from typing import List

from django.conf import settings
from selenium import webdriver
from selenium.common.exceptions import WebDriverException

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
    options.add_argument("--remote-debugging-port=9222")
    options.add_experimental_option("prefs", prefs)

    try:
        if settings.DEBUG:
            driver = webdriver.Chrome(
                os.environ.get("CHROME_DRIVER_PATH"), options=options
            )
        else:
            # Heroku
            options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")

            driver = webdriver.Chrome(
                executable_path=os.environ.get("CHROME_DRIVER_PATH"),
                chrome_options=options,
            )
    except WebDriverException:
        driver = None

    return driver


def get_all_fields(model) -> List[str]:
    r = []
    try:
        r = [f.name for f in model._meta.__dict__["local_fields"]]
    except KeyError:
        pass
    else:
        pass
    return r
