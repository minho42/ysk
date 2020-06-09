from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", include("currency.urls")),
    path("about/", views.about, name="about"),
    path("paigeisawesome/", admin.site.urls),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
