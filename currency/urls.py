from django.urls import path

from . import views

app_name = "currency"

urlpatterns = [
    path("", views.CurrencyView.as_view(), name="list"),
    path("api/new/", views.CurrencyAPIViewNew.as_view(), name="api_new"),
    path("api/old/", views.CurrencyAPIViewOld.as_view(), name="api_old"),
]
