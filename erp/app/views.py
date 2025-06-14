from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.db.models import Sum, Count, Q, Avg
from django.contrib.auth.models import User
from .models import Product, Order, OrderItem, Category, UserProfile
from .forms import UserRegisterForm, ProductForm, OrderForm, CategoryForm
from datetime import datetime, timedelta
from django.utils import timezone
import json

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'app/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get statistics
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_users = User.objects.count()
    total_categories = Category.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    # Recent orders
    recent_orders = Order.objects.select_related('customer').order_by('-order_date')[:5]
    
    # Low stock products
    low_stock_products = Product.objects.filter(stock_quantity__lt=10)[:5]
    
    # Popular categories with product count
    popular_categories = Category.objects.annotate(
        product_count=Count('product')
    ).order_by('-product_count')[:5]
    
    context = {
        'total_products': total_products,
        'total_orders': total_orders,
        'total_users': total_users,
        'total_categories': total_categories,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'popular_categories': popular_categories,
    }
    return render(request, 'app/dashboard.html', context)

@login_required
def user_list(request):
    users = User.objects.select_related('userprofile').order_by('-date_joined')
    return render(request, 'app/user_list.html', {'users': users})

@login_required
def user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_orders = Order.objects.filter(customer=user).order_by('-order_date')
    return render(request, 'app/user_detail.html', {'user': user, 'user_orders': user_orders})

# Product Views
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'app/product_list.html'
    context_object_name = 'products'
    paginate_by = 10
    
    def get_queryset(self):
        return Product.objects.select_related('category').order_by('-created_at')

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'app/product_detail.html'
    
    def get_object(self):
        return get_object_or_404(Product.objects.select_related('category'), pk=self.kwargs['pk'])

class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Product created successfully!')
        return super().form_valid(form)

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'app/product_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully!')
        return super().form_valid(form)

class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'app/product_confirm_delete.html'
    success_url = reverse_lazy('product-list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Product deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Order Views
class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'app/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        return Order.objects.select_related('customer').order_by('-order_date')

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'app/order_detail.html'
    
    def get_object(self):
        return get_object_or_404(
            Order.objects.select_related('customer').prefetch_related('items__product'), 
            pk=self.kwargs['pk']
        )

class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'app/order_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Order created successfully!')
        return super().form_valid(form)

class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'app/order_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Order updated successfully!')
        return super().form_valid(form)

# Category Views
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'app/category_list.html'
    context_object_name = 'categories'
    paginate_by = 12
    
    def get_queryset(self):
        return Category.objects.annotate(
            product_count=Count('product')
        ).order_by('-created_at')

class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Category
    template_name = 'app/category_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.product_set.select_related('category').order_by('-created_at')
        context['product_count'] = context['products'].count()
        return context

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app/category_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Category created successfully!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'app/category_form.html'
    
    def form_valid(self, form):
        messages.success(self.request, 'Category updated successfully!')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'app/category_confirm_delete.html'
    success_url = reverse_lazy('category-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_count'] = self.object.product_set.count()
        return context
    
    def delete(self, request, *args, **kwargs):
        if self.get_object().product_set.count() > 0:
            messages.error(request, 'Cannot delete category that contains products!')
            return redirect('category-detail', pk=self.get_object().pk)
        messages.success(request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def statistics(request):
    return render(request, 'app/statistics.html')

@login_required
def chart_data(request):
    try:
        # Monthly sales data for the last 12 months
        monthly_sales = []
        current_date = timezone.now()
        
        for i in range(12):
            # Calculate the start of the month
            if current_date.month - i <= 0:
                month = current_date.month - i + 12
                year = current_date.year - 1
            else:
                month = current_date.month - i
                year = current_date.year
            
            month_start = datetime(year, month, 1)
            
            # Calculate the end of the month
            if month == 12:
                month_end = datetime(year + 1, 1, 1)
            else:
                month_end = datetime(year, month + 1, 1)
            
            # Get sales for this month
            sales = Order.objects.filter(
                order_date__gte=month_start,
                order_date__lt=month_end,
                status__in=['delivered', 'shipped', 'processing']  # Only count meaningful orders
            ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0
            
            monthly_sales.append({
                'month': month_start.strftime('%B %Y'),
                'sales': float(sales)
            })
        
        # Reverse to show chronological order
        monthly_sales.reverse()
        
        # Product categories data
        categories = Category.objects.annotate(
            product_count=Count('product'),
            total_stock=Sum('product__stock_quantity'),
            avg_price=Avg('product__price')
        ).values('name', 'product_count', 'total_stock', 'avg_price')
        
        # Convert Decimal to float for JSON serialization
        categories_list = []
        for cat in categories:
            categories_list.append({
                'name': cat['name'],
                'product_count': cat['product_count'] or 0,
                'total_stock': cat['total_stock'] or 0,
                'avg_price': float(cat['avg_price'] or 0)
            })
        
        # Order status data
        order_status = Order.objects.values('status').annotate(
            count=Count('status')
        ).order_by('status')
        
        # Top selling products
        top_products = Product.objects.annotate(
            total_sold=Sum('orderitem__quantity')
        ).filter(total_sold__isnull=False).order_by('-total_sold')[:5]
        
        top_products_data = []
        for product in top_products:
            top_products_data.append({
                'name': product.name,
                'total_sold': product.total_sold or 0,
                'revenue': float((product.total_sold or 0) * product.price)
            })
        
        # Calculate additional statistics
        total_revenue = sum(item['sales'] for item in monthly_sales)
        total_orders = Order.objects.count()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
        
        data = {
            'monthly_sales': monthly_sales,
            'categories': categories_list,
            'order_status': list(order_status),
            'top_products': top_products_data,
            'summary': {
                'total_revenue': total_revenue,
                'avg_order_value': avg_order_value,
                'total_orders': total_orders,
                'total_products': Product.objects.count(),
                'total_categories': Category.objects.count(),
                'low_stock_count': Product.objects.filter(stock_quantity__lt=10).count()
            }
        }
        
        return JsonResponse(data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
