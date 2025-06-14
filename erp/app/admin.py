from django.contrib import admin
from .models import UserProfile, Product, Order, OrderItem, Category

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    list_filter = ['created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'sku', 'created_at']
    list_filter = ['category', 'created_at']
    search_fields = ['name', 'sku']
    list_editable = ['price', 'stock_quantity']

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'status', 'total_amount', 'order_date']
    list_filter = ['status', 'order_date']
    search_fields = ['customer__username', 'id']
    inlines = [OrderItemInline]
