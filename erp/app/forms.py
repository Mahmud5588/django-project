from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from .models import Product, Order, Category

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'stock_quantity', 'sku', 'image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'stock_quantity': forms.NumberInput(attrs={'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('sku', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('category', css_class='form-group col-md-6 mb-0'),
                Column('price', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('stock_quantity', css_class='form-group col-md-6 mb-0'),
                Column('image', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Submit('submit', 'Save Product', css_class='btn btn-primary')
        )

    def clean_sku(self):
        sku = self.cleaned_data.get('sku')
        if sku:
            # Check if SKU already exists (excluding current instance if updating)
            existing = Product.objects.filter(sku=sku)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A product with this SKU already exists.')
        return sku

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'status', 'shipping_address', 'notes', 'total_amount']
        widgets = {
            'shipping_address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'total_amount': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('customer', css_class='form-group col-md-6 mb-0'),
                Column('status', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('total_amount', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'shipping_address',
            'notes',
            Submit('submit', 'Save Order', css_class='btn btn-primary')
        )

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'name',
            'description',
            Submit('submit', 'Save Category', css_class='btn btn-primary')
        )

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check if category name already exists (excluding current instance if updating)
            existing = Category.objects.filter(name__iexact=name)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise forms.ValidationError('A category with this name already exists.')
        return name
