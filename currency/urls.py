from django.urls import path

from . import views

app_name = "currency"

urlpatterns = [
    path("", views.CurrencyHome.as_view(), name="home"),
    path("data/", views.CurrencyAPIViewData.as_view(), name="data"),
]
