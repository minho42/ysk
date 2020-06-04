from django.contrib import admin

from core.utils import get_all_fields

from .models import Currency


class CurrencyAdmin(admin.ModelAdmin):
    list_display = get_all_fields(Currency)
    # fields = ['name', rate']
    list_editable = ["fee"]


admin.site.register(Currency, CurrencyAdmin)
