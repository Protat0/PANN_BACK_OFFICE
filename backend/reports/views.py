# reports/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Sum, Count, Avg, F, Q  # ← Q is already imported correctly
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal

from .models import Sale, SaleItem, Product, Category, Branch
from .serializers import (
    SaleSerializer, ProductSerializer, DashboardStatsSerializer
)

class ReportsViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get basic dashboard statistics"""
        now = timezone.now()
        today = now.date()
        week_start = today - timedelta(days=today.weekday())
        month_start = today.replace(day=1)
        
        # Today's stats
        today_sales = Sale.objects.filter(
            created_at__date=today,
            is_refunded=False
        ).aggregate(
            total_sales=Sum('total_amount') or Decimal('0.00'),
            total_orders=Count('id'),
            average_order_value=Avg('total_amount') or Decimal('0.00')
        )
        
        # Week's stats
        week_sales = Sale.objects.filter(
            created_at__date__gte=week_start,
            created_at__date__lte=today,
            is_refunded=False
        ).aggregate(
            total_sales=Sum('total_amount') or Decimal('0.00'),
            total_orders=Count('id')
        )
        
        # Month's stats
        month_sales = Sale.objects.filter(
            created_at__date__gte=month_start,
            created_at__date__lte=today,
            is_refunded=False
        ).aggregate(
            total_sales=Sum('total_amount') or Decimal('0.00'),
            total_orders=Count('id')
        )
        
        # Inventory stats - Fix this line (line 61)
        inventory_stats = Product.objects.filter(is_active=True).aggregate(
            total_products=Count('id'),
            low_stock_count=Count('id', filter=Q(stock_quantity__lte=F('low_stock_threshold')))
        )
        
        dashboard_data = {
            'total_sales_today': today_sales['total_sales'],
            'total_orders_today': today_sales['total_orders'],
            'total_profit_today': Decimal('0.00'),
            'average_order_value_today': today_sales['average_order_value'],
            
            'total_sales_week': week_sales['total_sales'],
            'total_orders_week': week_sales['total_orders'],
            'total_profit_week': Decimal('0.00'),
            
            'total_sales_month': month_sales['total_sales'],
            'total_orders_month': month_sales['total_orders'],
            'total_profit_month': Decimal('0.00'),
            
            'low_stock_count': inventory_stats['low_stock_count'],
            'total_products': inventory_stats['total_products'],
        }
        
        serializer = DashboardStatsSerializer(dashboard_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def products_list(self, request):
        """Get list of all products"""
        products = Product.objects.filter(is_active=True)
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sales_summary(self, request):
        """Get sales summary for a period"""
        period = request.query_params.get('period', 'today')
        
        # Get date range based on period
        now = timezone.now()
        if period == 'today':
            start_date = now.date()
            end_date = now.date()
        elif period == 'week':
            start_date = now.date() - timedelta(days=now.weekday())
            end_date = now.date()
        elif period == 'month':
            start_date = now.date().replace(day=1)
            end_date = now.date()
        else:
            start_date = now.date()
            end_date = now.date()
        
        # Get sales data
        sales_data = Sale.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            is_refunded=False
        ).aggregate(
            total_sales=Sum('total_amount') or Decimal('0.00'),
            total_orders=Count('id'),
            average_order_value=Avg('total_amount') or Decimal('0.00'),
            total_items_sold=Sum('sale_items__quantity') or 0
        )
        
        sales_data['period'] = f"{start_date} to {end_date}"
        
        return Response(sales_data)
    
    @action(detail=False, methods=['get'])
    def top_products(self, request):
        """Get top selling products"""
        limit = int(request.query_params.get('limit', 10))
        
        # Get top products by quantity sold
        top_products = SaleItem.objects.values(
            'product__name',
            'product__sku',
            'product__category__name'
        ).annotate(
            quantity_sold=Sum('quantity'),
            total_revenue=Sum('total_price')
        ).order_by('-quantity_sold')[:limit]
        
        return Response(list(top_products))
    
    @action(detail=False, methods=['get'])
    def low_stock_products(self, request):
        """Get products with low stock"""
        low_stock = Product.objects.filter(
            is_active=True,
            stock_quantity__lte=10  # or use F('low_stock_threshold')
        ).values(
            'name', 'sku', 'stock_quantity', 'low_stock_threshold'
        )
        
        return Response(list(low_stock))
    
    @action(detail=False, methods=['get'])
    def recent_sales(self, request):
        """Get recent sales"""
        limit = int(request.query_params.get('limit', 20))
        
        recent_sales = Sale.objects.filter(
            is_refunded=False
        ).order_by('-created_at')[:limit]
        
        serializer = SaleSerializer(recent_sales, many=True)
        return Response(serializer.data)