# erp_app/models.py
from django.db import models
from django.utils import timezone
from decimal import Decimal # <--- QO'SHING



class Kategoriya(models.Model):
    nomi = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya Nomi")

    def __str__(self):
        return self.nomi

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

class Mahsulot(models.Model):
    nomi = models.CharField(max_length=200, verbose_name="Mahsulot Nomi")
    artikul = models.CharField(max_length=50, unique=True, verbose_name="Artikul (SKU)")
    kategoriya = models.ForeignKey(Kategoriya, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategoriyasi")
    rangi = models.CharField(max_length=50, blank=True, null=True, verbose_name="Rangi")
    olchami = models.CharField(max_length=50, blank=True, null=True, verbose_name="O'lchami")
    sotib_olish_narxi = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Sotib Olish Narxi ($)")
    sotish_narxi = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name="Sotish Narxi ($)")
    qoldiq = models.PositiveIntegerField(default=0, verbose_name="Ombordagi Qoldiq (dona)")
    tavsif = models.TextField(blank=True, null=True, verbose_name="Qo'shimcha Tavsif")
    qoshilgan_sana = models.DateTimeField(auto_now_add=True, verbose_name="Qo'shilgan Sana")
    yangilangan_sana = models.DateTimeField(auto_now=True, verbose_name="Yangilangan Sana")

    def __str__(self):
        return f"{self.nomi} ({self.artikul})"

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-qoshilgan_sana']

class Mijoz(models.Model):
    kompaniya_nomi = models.CharField(max_length=200, verbose_name="Kompaniya Nomi")
    aloqa_shaxs = models.CharField(max_length=100, verbose_name="Mas'ul Shaxs")
    telefon = models.CharField(max_length=20, unique=True, verbose_name="Telefon Raqami")
    email = models.EmailField(blank=True, null=True, verbose_name="Email Manzili")
    manzil = models.TextField(blank=True, null=True, verbose_name="Manzil")
    qoshilgan_sana = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.kompaniya_nomi

    class Meta:
        verbose_name = "Mijoz"
        verbose_name_plural = "Mijozlar"

class SotuvBuyurtmasi(models.Model):
    STATUS_CHOICES = [
        ('Yangi', 'Yangi'),
        ('Tasdiqlangan', 'Tasdiqlangan'),
        ('Jo\'natilgan', 'Jo\'natilgan'),
        ('Yetkazilgan', 'Yetkazilgan'),
        ('Bekor qilingan', 'Bekor qilingan'),
    ]
    mijoz = models.ForeignKey(Mijoz, on_delete=models.CASCADE, verbose_name="Mijoz")
    buyurtma_sanasi = models.DateTimeField(default=timezone.now, verbose_name="Buyurtma Sanasi")
    # Decimal('0.00') default qiymat sifatida ishlatilishi kerak
    umumiy_summa = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'), verbose_name="Umumiy Summa ($)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Yangi', verbose_name="Statusi")
    izoh = models.TextField(blank=True, null=True, verbose_name="Izoh")

    def __str__(self):
        return f"Buyurtma #{self.id} - {self.mijoz.kompaniya_nomi if self.mijoz else 'Mijoz belgilanmagan'}"

    def update_total_sum(self):
        """Buyurtmaning umumiy summasini elementlar asosida yangilaydi."""
        total = Decimal('0.00')
        for item in self.elementlar.all(): # related_name 'elementlar'
            # umumiy_element_summasi None qaytarmasligiga ishonch hosil qilish kerak
            item_sum = item.umumiy_element_summasi
            if item_sum is not None: # Agar umumiy_element_summasi None bo'lmasa
                total += item_sum
        self.umumiy_summa = total
        # Faqat umumiy_summa ni saqlash uchun update_fields dan foydalanish mumkin,
        # lekin hozircha to'liq save qilamiz.
        self.save(update_fields=['umumiy_summa'])


    class Meta:
        verbose_name = "Sotuv Buyurtmasi"
        verbose_name_plural = "Sotuv Buyurtmalari"
        ordering = ['-buyurtma_sanasi']

class SotuvBuyurtmasiElementi(models.Model):
    buyurtma = models.ForeignKey(SotuvBuyurtmasi, related_name='elementlar', on_delete=models.CASCADE, verbose_name="Sotuv Buyurtmasi")
    mahsulot = models.ForeignKey(Mahsulot, on_delete=models.CASCADE, verbose_name="Mahsulot")
    miqdori = models.PositiveIntegerField(default=1, verbose_name="Miqdori (dona)")
    # null=True va blank=True qo'shildi, yoki default qiymat bering
    narx = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Narxi (birlik uchun $)",
        null=True,  # Bazada None bo'lishiga ruxsat beradi
        blank=True  # Formalarda bo'sh qoldirishga ruxsat beradi
        # Yoki default=Decimal('0.00')
    )

    def __str__(self):
        # mahsulot None bo'lishi mumkin emas (ForeignKey cheklovi tufayli, agar o'chirilmasa)
        return f"{self.mahsulot.nomi if self.mahsulot else 'Noma\'lum mahsulot'} x {self.miqdori}"

    @property
    def umumiy_element_summasi(self):
        if self.miqdori is not None and self.narx is not None:
            # miqdori int, narx Decimal bo'lishi kerak (yoki None)
            return Decimal(self.miqdori) * self.narx
        return Decimal('0.00') # Agar hisoblash mumkin bo'lmasa, 0.00 qaytaradi

    def save(self, *args, **kwargs):
        # Agar narx None bo'lsa va mahsulot tanlangan bo'lsa, mahsulotning sotish narxini olish
        if self.narx is None and self.mahsulot:
            self.narx = self.mahsulot.sotish_narxi # Yoki boshqa logikaga ko'ra
        
        super().save(*args, **kwargs)
        # Element saqlangandan yoki o'zgartirilgandan so'ng buyurtmaning umumiy summasini yangilash
        if self.buyurtma:
            self.buyurtma.update_total_sum()

    def delete(self, *args, **kwargs):
        buyurtma_instance = self.buyurtma # O'chirishdan oldin buyurtmani saqlab qolish
        super().delete(*args, **kwargs)
        # Element o'chirilgandan so'ng buyurtmaning umumiy summasini yangilash
        if buyurtma_instance:
            buyurtma_instance.update_total_sum()

    class Meta:
        verbose_name = "Sotuv Buyurtmasi Elementi"
        verbose_name_plural = "Sotuv Buyurtmasi Elementlari"