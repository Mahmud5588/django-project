# erp_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('mahsulotlar/', views.mahsulotlar_list, name='mahsulotlar_list'),
    path('buyurtmalar/', views.sotuv_buyurtmalari_list, name='sotuv_buyurtmalari_list'),
]