from ..database import db_manager 
from ..models import SalesLog
import bcrypt
from notifications.services import notification_service
from .pos.SalesService import SalesService
from collections import defaultdict
from datetime import datetime, timedelta

class SalesDisplayService():
    def __init__(self):
        self.db = db_manager.get_database()  
        self.sales_collection = self.db.sales  
        self.online_transactions_collection = self.db.online_transactions 

    def fetch_all_sales(self):
        """Fetch ALL sales (no filter, just demo; add pagination or filters if needed)."""
        sales = list(self.sales_collection.find({}))
        for sale in sales:
            # sanitize ObjectId, dates, etc., if needed
            sale['_id'] = str(sale['_id'])
            # other conversion as needed
        return sales

    def fetch_all_online_transactions(self):
        """Fetch ALL online transactions."""
        transactions = list(self.online_transactions_collection.find({}))
        for txn in transactions:
            txn['_id'] = str(txn['_id'])
            # convert/clean up other fields as needed
        return transactions

    def top_selling_items(self, start_date=None, end_date=None, limit=10):
        now = datetime.utcnow()
        if start_date is None:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = now

        sales = list(self.sales_collection.find({"transaction_date": {"$gte": start_date, "$lte": end_date}}))
        online_transactions = list(self.online_transactions_collection.find({"transaction_date": {"$gte": start_date, "$lte": end_date}}))
        item_totals = defaultdict(lambda: {"product_name": "", "total_quantity": 0, "total_sales": 0.0})
        for sale in sales + online_transactions:
            for item in sale.get("items", []):
                pid = item["product_id"]
                item_totals[pid]["product_name"] = item.get("product_name", "")
                item_totals[pid]["total_quantity"] += item.get("quantity", 0)
                item_totals[pid]["total_sales"] += item.get("subtotal", 0)
        result = sorted([
            {"product_id": pid, **data}
            for pid, data in item_totals.items()
        ], key=lambda x: x["total_sales"], reverse=True)
        return result[:limit]

    def top_selling_pos_items(self, start_date=None, end_date=None, limit=10):
        now = datetime.utcnow()
        if start_date is None:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = now
        sales = list(self.sales_collection.find({"transaction_date": {"$gte": start_date, "$lte": end_date}}))
        item_totals = defaultdict(lambda: {"product_name": "", "total_quantity": 0, "total_sales": 0.0})
        for sale in sales:
            for item in sale.get("items", []):
                pid = item["product_id"]
                item_totals[pid]["product_name"] = item.get("product_name", "")
                item_totals[pid]["total_quantity"] += item.get("quantity", 0)
                item_totals[pid]["total_sales"] += item.get("subtotal", 0)
        result = sorted([
            {"product_id": pid, **data}
            for pid, data in item_totals.items()
        ], key=lambda x: x["total_sales"], reverse=True)
        return result[:limit]

    def top_selling_online_items(self, start_date=None, end_date=None, limit=10):
        now = datetime.utcnow()
        if start_date is None:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = now
        online_transactions = list(self.online_transactions_collection.find({"transaction_date": {"$gte": start_date, "$lte": end_date}}))
        item_totals = defaultdict(lambda: {"product_name": "", "total_quantity": 0, "total_sales": 0.0})
        for txn in online_transactions:
            for item in txn.get("items", []):
                pid = item["product_id"]
                item_totals[pid]["product_name"] = item.get("product_name", "")
                item_totals[pid]["total_quantity"] += item.get("quantity", 0)
                item_totals[pid]["total_sales"] += item.get("subtotal", 0)
        result = sorted([
            {"product_id": pid, **data}
            for pid, data in item_totals.items()
        ], key=lambda x: x["total_sales"], reverse=True)
        return result[:limit] 

    def fetch_all_products(self):
        products = list(self.db.products.find({}))
        for p in products:
            p['_id'] = str(p['_id'])
        return products

    def fetch_all_categories(self):
        categories = list(self.db.category.find({}))
        for c in categories:
            c['_id'] = str(c['_id'])
        return categories

    def fetch_all_batches(self):
        batches = list(self.db.batches.find({}))
        for b in batches:
            b['_id'] = str(b['_id'])
        return batches

    def build_sales_by_item_display(self, start_date=None, end_date=None):
        now = datetime.utcnow()
        if start_date is None:
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if end_date is None:
            end_date = now

        products = self.fetch_all_products()
        categories = self.fetch_all_categories()
        batches = self.fetch_all_batches()

        # Map category_id -> category_name
        category_id_to_name = {}
        for cat in categories:
            category_id_to_name[cat.get('category_id') or cat.get('_id')] = cat.get('name') or cat.get('category_name')

        # Group batches by product_id and sum quantity_remaining
        product_id_to_stock_remaining = defaultdict(int)
        for batch in batches:
            product_id = batch.get('product_id')
            qty_remaining = batch.get('quantity_remaining', 0)
            if product_id:
                product_id_to_stock_remaining[product_id] += qty_remaining

        # Aggregate sales and online items for the period
        pos_sales = list(self.sales_collection.find({"transaction_date": {"$gte": start_date, "$lte": end_date}}))
        online_sales = list(self.online_transactions_collection.find({"transaction_date": {"$gte": start_date, "$lte": end_date}}))

        product_id_to_sold_qty = defaultdict(int)
        product_id_to_total_sales = defaultdict(float)

        def accumulate_items(container):
            for doc in container:
                for item in doc.get('items', []):
                    pid = item.get('product_id')
                    if not pid:
                        continue
                    product_id_to_sold_qty[pid] += item.get('quantity', 0)
                    product_id_to_total_sales[pid] += item.get('subtotal', 0.0)

        accumulate_items(pos_sales)
        accumulate_items(online_sales)

        # Build display list per product
        display_rows = []
        for p in products:
            product_id = p.get('product_id') or p.get('_id')
            category_name = category_id_to_name.get(p.get('category_id'))
            display_rows.append({
                'product_id': product_id,
                'product_name': p.get('product_name'),
                'category_name': category_name,
                'sku': p.get('sku') or p.get('SKU') or p.get('Sku'),
                'unit': p.get('unit'),
                'stock': product_id_to_stock_remaining.get(product_id, 0),
                'items_sold': product_id_to_sold_qty.get(product_id, 0),
                'total_sales': round(product_id_to_total_sales.get(product_id, 0.0), 2),
                # Optional passthrough fields if frontend needs them
                'selling_price': p.get('selling_price'),
                'is_taxable': p.get('is_taxable'),
            })

        # Sort by total_sales desc by default
        display_rows.sort(key=lambda r: r['total_sales'], reverse=True)
        return display_rows 

    
   