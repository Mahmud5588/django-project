from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Category, Product, Order, OrderItem
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create superuser if it doesn't exist
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
            self.stdout.write(self.style.SUCCESS('Created admin user: admin/admin123'))
        
        # Create sample users
        users = []
        for i in range(5):
            username = f'user{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='password123',
                    first_name=f'User{i+1}',
                    last_name='Test'
                )
                users.append(user)
        
        # Create categories
        categories_data = [
            {'name': 'Electronics', 'description': 'Electronic devices, gadgets, computers, and tech accessories'},
            {'name': 'Clothing & Fashion', 'description': 'Apparel, shoes, accessories, and fashion items for all ages'},
            {'name': 'Books & Media', 'description': 'Books, magazines, educational materials, and digital media'},
            {'name': 'Home & Garden', 'description': 'Home improvement, furniture, garden supplies, and decor'},
            {'name': 'Sports & Outdoors', 'description': 'Sports equipment, outdoor gear, fitness accessories'},
            {'name': 'Health & Beauty', 'description': 'Personal care, cosmetics, health supplements, and wellness products'},
            {'name': 'Automotive', 'description': 'Car parts, accessories, tools, and automotive supplies'},
            {'name': 'Toys & Games', 'description': 'Toys, board games, video games, and entertainment products'},
        ]
        
        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            categories.append(category)
        
        # Create products
        products_data = [
            {'name': 'MacBook Pro', 'category': 'Electronics', 'price': 1299.99, 'stock': 25},
            {'name': 'iPhone 15', 'category': 'Electronics', 'price': 999.99, 'stock': 50},
            {'name': 'Samsung Galaxy S24', 'category': 'Electronics', 'price': 899.99, 'stock': 40},
            {'name': 'Dell Monitor 27"', 'category': 'Electronics', 'price': 299.99, 'stock': 30},
            {'name': 'Wireless Headphones', 'category': 'Electronics', 'price': 199.99, 'stock': 75},
            {'name': 'Cotton T-Shirt', 'category': 'Clothing & Fashion', 'price': 24.99, 'stock': 200},
            {'name': 'Denim Jeans', 'category': 'Clothing & Fashion', 'price': 59.99, 'stock': 150},
            {'name': 'Winter Jacket', 'category': 'Clothing & Fashion', 'price': 89.99, 'stock': 80},
            {'name': 'Running Shoes', 'category': 'Clothing & Fashion', 'price': 129.99, 'stock': 60},
            {'name': 'Python Crash Course', 'category': 'Books & Media', 'price': 39.99, 'stock': 100},
            {'name': 'Clean Code', 'category': 'Books & Media', 'price': 44.99, 'stock': 85},
            {'name': 'Design Patterns', 'category': 'Books & Media', 'price': 49.99, 'stock': 70},
            {'name': 'Garden Hose 50ft', 'category': 'Home & Garden', 'price': 34.99, 'stock': 45},
            {'name': 'Lawn Mower', 'category': 'Home & Garden', 'price': 299.99, 'stock': 15},
            {'name': 'Plant Fertilizer', 'category': 'Home & Garden', 'price': 19.99, 'stock': 120},
            {'name': 'Tennis Racket', 'category': 'Sports & Outdoors', 'price': 89.99, 'stock': 35},
            {'name': 'Basketball', 'category': 'Sports & Outdoors', 'price': 29.99, 'stock': 60},
            {'name': 'Yoga Mat', 'category': 'Sports & Outdoors', 'price': 24.99, 'stock': 90},
        ]
        
        products = []
        for prod_data in products_data:
            category = Category.objects.get(name=prod_data['category'])
            product, created = Product.objects.get_or_create(
                name=prod_data['name'],
                defaults={
                    'description': f'High quality {prod_data["name"].lower()} with excellent features and durability.',
                    'category': category,
                    'price': Decimal(str(prod_data['price'])),
                    'stock_quantity': prod_data['stock'],
                    'sku': f'SKU{random.randint(10000, 99999)}'
                }
            )
            products.append(product)
        
        # Create sample orders
        all_users = User.objects.all()
        statuses = ['pending', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for i in range(50):
            customer = random.choice(all_users)
            order = Order.objects.create(
                customer=customer,
                status=random.choice(statuses),
                shipping_address=f'{random.randint(100, 9999)} {random.choice(["Main St", "Oak Ave", "Pine Rd", "Elm Dr", "Cedar Ln"])}, {random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"])}, {random.choice(["NY", "CA", "IL", "TX", "AZ"])} {random.randint(10000, 99999)}',
                total_amount=Decimal('0.00')
            )
            
            # Add random products to order
            num_items = random.randint(1, 5)
            total_amount = Decimal('0.00')
            
            selected_products = random.sample(products, min(num_items, len(products)))
            
            for product in selected_products:
                quantity = random.randint(1, 3)
                price = product.price
                
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=quantity,
                    price=price
                )
                
                total_amount += price * quantity
            
            order.total_amount = total_amount
            order.save()
        
        self.stdout.write(self.style.SUCCESS('Sample data created successfully!'))
        self.stdout.write('You can now login with:')
        self.stdout.write('Username: admin')
        self.stdout.write('Password: admin123')
