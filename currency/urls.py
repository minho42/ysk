from django.urls import path

from . import views

app_name = "currency"

urlpatterns = [
    path("api/data/", views.CurrencyAPIViewData.as_view(), name="api_data"),
]
