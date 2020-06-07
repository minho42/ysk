import json

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Currency
from .views import round_it, get_real_rate


class CurrencyModelTests(TestCase):
    def setUp(self):
        c = Currency.objects.create(name="new", rate=123.45, fetch_time=timezone.now())
        self.assertLess(c.created_at, timezone.now())

    def test_currency_unique_name(self):
        Currency.objects.create(
            name="same name", rate=123.45, fetch_time=timezone.now()
        )
        try:
            Currency.objects.create(
                name="same name", rate=123.45, fetch_time=timezone.now()
            )
        except:
            # It's intended to raise exception
            pass
        else:
            raise self.failureException("Name is not unique")


class CurrencyViewsTests(TestCase):
    def setUp(self):
        c = Currency.objects.create(name="new", rate=123.45, fetch_time=timezone.now())
        self.assertLess(c.created_at, timezone.now())

    def test_currency_list_view(self):
        response = self.client.get(reverse("currency:list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "currency/currency_list.html")

    # this should be mocked
    # def test_currency_api_new(self):
    #     response = self.client.get(reverse('currency:api_new'))
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     # this doesn't work with those who use selenium to fetch...
    #     self.assertGreater(len(data), 0)

    def test_currency_api_old(self):
        response = self.client.get(reverse("currency:api_old"))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertGreater(len(data), 0)

    def test_xpath(self):
        pass


class CurrencyFunctionTests(TestCase):
    def test_round_it(self):
        pass

    def test_get_real_rate(self):
        pass

