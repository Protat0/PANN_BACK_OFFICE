# reports/serializers.py
from rest_framework import serializers
from .models import Sale, SaleItem, Product, Category, Branch
from django.contrib.auth.models import User
from decimal import Decimal

class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Branch
        fields = ['id', 'name', 'address']

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'parent_category']

class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    profit_margin = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'sku', 'barcode', 'category', 'category_name',
            'cost_price', 'selling_price', 'stock_quantity', 'low_stock_threshold',
            'profit_margin', 'is_low_stock', 'expiry_date'
        ]

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_sku = serializers.CharField(source='product.sku', read_only=True)
    profit = serializers.ReadOnlyField()
    
    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'product_sku', 'quantity',
            'unit_price', 'total_price', 'cost_price', 'profit'
        ]

class SaleSerializer(serializers.ModelSerializer):
    sale_items = SaleItemSerializer(many=True, read_only=True)
    cashier_name = serializers.CharField(source='cashier.get_full_name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    profit = serializers.ReadOnlyField()
    
    class Meta:
        model = Sale
        fields = [
            'id', 'sale_number', 'cashier', 'cashier_name', 'branch', 'branch_name',
            'customer_name', 'customer_phone', 'payment_method', 'order_type',
            'subtotal', 'discount_amount', 'tax_amount', 'total_amount',
            'amount_paid', 'change_amount', 'profit', 'is_refunded',
            'created_at', 'sale_items'
        ]

# Dashboard Stats Serializer
class DashboardStatsSerializer(serializers.Serializer):
    total_sales_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders_today = serializers.IntegerField()
    total_profit_today = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_order_value_today = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    total_sales_week = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders_week = serializers.IntegerField()
    total_profit_week = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    total_sales_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_orders_month = serializers.IntegerField()
    total_profit_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    low_stock_count = serializers.IntegerField()
    total_products = serializers.IntegerField()