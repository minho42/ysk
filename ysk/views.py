from django.shortcuts import render
from currency.views import BASE_AMOUNT


def about(request):
    return render(
        request, template_name="about.html", context={"BASE_AMOUNT": BASE_AMOUNT}
    )
