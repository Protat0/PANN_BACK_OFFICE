# reports/management/commands/generate_sample_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reports.models import Branch, Category, Product, Sale, SaleItem
from decimal import Decimal
import random
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Generate sample data for testing reports'
    
    def handle(self, *args, **options):
        # Create sample branch
        branch, created = Branch.objects.get_or_create(
            name="Ramyeon Food Corner - Main",
            defaults={'address': 'Bislig City, Surigao del Sur'}
        )
        if created:
            self.stdout.write(f"Created branch: {branch.name}")
        
        # Create sample categories
        categories_data = [
            ('Noodles', 'Korean instant noodles and ramen'),
            ('Drinks', 'Beverages and soft drinks'),
            ('Toppings', 'Ramen toppings and add-ons'),
            ('Snacks', 'Korean snacks and side dishes')
        ]
        
        category_objects = []
        for cat_name, cat_desc in categories_data:
            cat, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={'description': cat_desc}
            )
            category_objects.append(cat)
            if created:
                self.stdout.write(f"Created category: {cat.name}")
        
        # Create sample products
        products_data = [
            ('Samyang Spicy Ramen', 'SAM001', Decimal('15.00'), Decimal('25.00'), category_objects[0]),
            ('Shin Ramyun', 'SHIN001', Decimal('12.00'), Decimal('20.00'), category_objects[0]),
            ('Jin Ramen Mild', 'JIN001', Decimal('10.00'), Decimal('18.00'), category_objects[0]),
            ('Coca Cola', 'COLA001', Decimal('8.00'), Decimal('15.00'), category_objects[1]),
            ('Korean Banana Milk', 'MILK001', Decimal('12.00'), Decimal('20.00'), category_objects[1]),
            ('Cheese Topping', 'CHEESE001', Decimal('5.00'), Decimal('10.00'), category_objects[2]),
            ('Egg Topping', 'EGG001', Decimal('8.00'), Decimal('15.00'), category_objects[2]),
            ('Korean Chips', 'CHIP001', Decimal('6.00'), Decimal('12.00'), category_objects[3]),
        ]
        
        product_objects = []
        for name, sku, cost, price, category in products_data:
            product, created = Product.objects.get_or_create(
                sku=sku,
                defaults={
                    'name': name,
                    'cost_price': cost,
                    'selling_price': price,
                    'category': category,
                    'branch': branch,
                    'stock_quantity': random.randint(20, 100),
                    'low_stock_threshold': 10
                }
            )
            product_objects.append(product)
            if created:
                self.stdout.write(f"Created product: {product.name}")
        
        # Create sample user (cashier)
        user, created = User.objects.get_or_create(
            username='cashier1',
            defaults={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'cashier1@example.com',
                'is_staff': True
            }
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(f"Created user: {user.username} (password: password123)")
        
        # Generate sample sales for the last 7 days
        sales_created = 0
        for i in range(7):
            sale_date = datetime.now() - timedelta(days=i)
            
            # Create 3-8 sales per day
            for j in range(random.randint(3, 8)):
                # Create sale
                sale = Sale.objects.create(
                    sale_number=f'SALE{sale_date.strftime("%Y%m%d")}{j+1:03d}',
                    cashier=user,
                    branch=branch,
                    payment_method=random.choice(['cash', 'card', 'gcash']),
                    order_type=random.choice(['dine_in', 'takeout', 'delivery']),
                    subtotal=Decimal('0.00'),
                    total_amount=Decimal('0.00'),
                    amount_paid=Decimal('0.00'),
                    created_at=sale_date.replace(
                        hour=random.randint(10, 21),
                        minute=random.randint(0, 59)
                    )
                )
                
                # Add 1-4 items per sale
                subtotal = Decimal('0.00')
                for k in range(random.randint(1, 4)):
                    product = random.choice(product_objects)
                    quantity = random.randint(1, 3)
                    unit_price = product.selling_price
                    total_price = unit_price * quantity
                    
                    SaleItem.objects.create(
                        sale=sale,
                        product=product,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        cost_price=product.cost_price
                    )
                    
                    subtotal += total_price
                
                # Update sale totals
                sale.subtotal = subtotal
                sale.total_amount = subtotal
                sale.amount_paid = subtotal
                sale.save()
                
                sales_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully generated sample data:\n'
                f'- 1 Branch\n'
                f'- {len(category_objects)} Categories\n'
                f'- {len(product_objects)} Products\n'
                f'- 1 User\n'
                f'- {sales_created} Sales'
            )
        )