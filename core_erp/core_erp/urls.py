# core_erp/urls.py
from django.contrib import admin
from django.urls import path, include # `include` ni import qiling

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('erp_app.urls')), # Ilovamiz URLlarini qo'shing
]