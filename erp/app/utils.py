from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Order, Product, User

def get_dashboard_stats():
    """Get dashboard statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_users': User.objects.count(),
        'total_revenue': Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'orders_this_week': Order.objects.filter(order_date__gte=week_ago).count(),
        'orders_this_month': Order.objects.filter(order_date__gte=month_ago).count(),
        'avg_order_value': Order.objects.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
        'low_stock_count': Product.objects.filter(stock_quantity__lt=10).count(),
    }
    
    return stats

def get_recent_activities():
    """Get recent system activities"""
    recent_orders = Order.objects.select_related('customer').order_by('-order_date')[:5]
    low_stock_products = Product.objects.filter(stock_quantity__lt=10).order_by('stock_quantity')[:5]
    
    return {
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
    }
