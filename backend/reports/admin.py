# reports/admin.py
from django.contrib import admin
from .models import Branch, Category, Product, Sale, SaleItem

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    list_display = ['name', 'address', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'address']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent_category', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent_category', 'created_at']
    search_fields = ['name', 'description']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'sku', 'category', 'selling_price', 
        'stock_quantity', 'is_low_stock', 'branch', 'is_active'
    ]
    list_filter = [
        'category', 'branch', 'is_active', 
        'created_at', 'expiry_date'
    ]
    search_fields = ['name', 'sku', 'barcode']
    readonly_fields = ['profit_margin', 'is_low_stock']

class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ['profit']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = [
        'sale_number', 'cashier', 'branch', 'payment_method',
        'total_amount', 'is_refunded', 'created_at'
    ]
    list_filter = [
        'payment_method', 'order_type', 'branch', 
        'is_refunded', 'created_at'
    ]
    search_fields = ['sale_number', 'customer_name', 'customer_phone']
    readonly_fields = ['profit']
    inlines = [SaleItemInline]

@admin.register(SaleItem)
class SaleItemAdmin(admin.ModelAdmin):
    list_display = ['sale', 'product', 'quantity', 'unit_price', 'total_price', 'profit']
    list_filter = ['sale__created_at', 'product__category']
    search_fields = ['sale__sale_number', 'product__name']
    readonly_fields = ['profit']