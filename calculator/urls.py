from django.urls import path
from . import views



urlpatterns = [
    path('manual/',views.manual_data),
    path('excel/',views.excel_data),
]