# erp_app/views.py
from django.shortcuts import render
from .models import Mahsulot, SotuvBuyurtmasi

def home(request):
    # Bosh sahifada umumiy statistika yoki tezkor havolalar bo'lishi mumkin
    mahsulotlar_soni = Mahsulot.objects.count()
    buyurtmalar_soni = SotuvBuyurtmasi.objects.count()
    context = {
        'mahsulotlar_soni': mahsulotlar_soni,
        'buyurtmalar_soni': buyurtmalar_soni,
        'page_title': "Bosh Sahifa"
    }
    return render(request, 'erp_app/home.html', context)

def mahsulotlar_list(request):
    mahsulotlar = Mahsulot.objects.all().order_by('nomi')
    context = {
        'mahsulotlar': mahsulotlar,
        'page_title': "Mahsulotlar Ro'yxati"
    }
    return render(request, 'erp_app/mahsulotlar_list.html', context)

def sotuv_buyurtmalari_list(request):
    buyurtmalar = SotuvBuyurtmasi.objects.select_related('mijoz').all().order_by('-buyurtma_sanasi')
    context = {
        'buyurtmalar': buyurtmalar,
        'page_title': "Sotuv Buyurtmalari"
    }
    return render(request, 'erp_app/sotuv_buyurtmalari_list.html', context)

# Kelajakda mahsulot va buyurtma uchun detail viewlar, create, update, delete viewlar qo'shilishi kerak