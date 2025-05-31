# erp_app/admin.py
from django.contrib import admin
from .models import Kategoriya, Mahsulot, Mijoz, SotuvBuyurtmasi, SotuvBuyurtmasiElementi

class SotuvBuyurtmasiElementiInline(admin.TabularInline):
    model = SotuvBuyurtmasiElementi
    extra = 1 # Nechta bo'sh forma ko'rsatish
    readonly_fields = ('umumiy_element_summasi',) # Faqat o'qish uchun maydon

@admin.register(Kategoriya)
class KategoriyaAdmin(admin.ModelAdmin):
    list_display = ('nomi',)
    search_fields = ('nomi',)

@admin.register(Mahsulot)
class MahsulotAdmin(admin.ModelAdmin):
    list_display = ('nomi', 'artikul', 'kategoriya', 'sotish_narxi', 'qoldiq', 'rangi', 'olchami')
    list_filter = ('kategoriya', 'rangi', 'olchami')
    search_fields = ('nomi', 'artikul', 'tavsif')
    list_editable = ('sotish_narxi', 'qoldiq') # Ro'yxatda tahrirlash mumkin bo'lgan maydonlar

@admin.register(Mijoz)
class MijozAdmin(admin.ModelAdmin):
    list_display = ('kompaniya_nomi', 'aloqa_shaxs', 'telefon', 'email')
    search_fields = ('kompaniya_nomi', 'aloqa_shaxs', 'telefon')

@admin.register(SotuvBuyurtmasi)
class SotuvBuyurtmasiAdmin(admin.ModelAdmin):
    list_display = ('id', 'mijoz', 'buyurtma_sanasi', 'umumiy_summa', 'status')
    list_filter = ('status', 'buyurtma_sanasi')
    search_fields = ('mijoz__kompaniya_nomi', 'id')
    inlines = [SotuvBuyurtmasiElementiInline] # Buyurtma elementlarini birgalikda ko'rsatish
    readonly_fields = ('umumiy_summa',) # Bu maydon avtomatik hisoblanishi kerak (signal yoki save metodi orqali)

    # Umumiy summani avtomatik hisoblash uchun save metodini qayta yozish mumkin
    # Yoki signal ishlatish yaxshiroq yechim bo'lishi mumkin
    # Hozircha admin panelda readonly qilib qo'yamiz

@admin.register(SotuvBuyurtmasiElementi)
class SotuvBuyurtmasiElementiAdmin(admin.ModelAdmin):
    list_display = ('buyurtma', 'mahsulot', 'miqdori', 'narx', 'umumiy_element_summasi')
    readonly_fields = ('umumiy_element_summasi',)