from datetime import datetime, timedelta
from collections import defaultdict
from ..database import db_manager


class SalesByCategoryService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.sales_collection = self.db.sales
        self.online_transactions_collection = self.db.online_transactions
        self.products_collection = self.db.products
        self.categories_collection = self.db.category

    def get_sales_by_category_with_date_filter(self, start_date=None, end_date=None, include_voided=False):
        """
        Fetch total sales and quantities grouped by category
        Includes both POS and online transactions with proper date filtering
        """
        try:
            query_filter = {}

            # ✅ Filter by date range
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    if isinstance(start_date, str):
                        start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                    date_filter["$gte"] = start_date
                if end_date:
                    if isinstance(end_date, str):
                        end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
                    date_filter["$lte"] = end_date
                query_filter["transaction_date"] = date_filter

            # ✅ Exclude voided sales unless requested
            if not include_voided:
                query_filter["status"] = {"$ne": "voided"}

            # 🔍 Fetch all sales data (POS + Online)
            pos_sales = list(self.sales_collection.find(query_filter))
            online_sales = list(self.online_transactions_collection.find(query_filter))
            all_sales = pos_sales + online_sales
            
            print(f"📊 Found {len(pos_sales)} POS sales and {len(online_sales)} online sales in range")

            # Fetch all products and categories once
            products = list(self.products_collection.find({}))
            categories = list(self.categories_collection.find({}))

            # 🔗 Build lookup maps with proper ID handling
            product_id_to_category = {}
            for product in products:
                product_id = product.get('_id') or product.get('product_id')
                category_id = product.get('category_id')
                if product_id and category_id:
                    product_id_to_category[str(product_id)] = str(category_id)

            category_id_to_name = {}
            for category in categories:
                category_id = str(category.get('_id'))
                category_name = category.get('category_name', 'Unknown Category')
                category_id_to_name[category_id] = category_name

            # 🧮 Initialize aggregation containers
            category_aggregate = defaultdict(lambda: {
                "total_sales": 0.0, 
                "total_items_sold": 0, 
                "product_count": set(),
                "transaction_count": 0
            })

            # 🧩 Accumulate sales per category from all transactions
            for sale in all_sales:
                # Skip voided entries unless explicitly allowed
                if not include_voided and sale.get("status") == "voided":
                    continue

                for item in sale.get("items", []):
                    product_id = str(item.get("product_id"))
                    quantity = item.get("quantity", 0)
                    subtotal = item.get("subtotal", 0.0)

                    category_id = product_id_to_category.get(product_id)
                    if not category_id:
                        continue

                    category_aggregate[category_id]["total_sales"] += subtotal
                    category_aggregate[category_id]["total_items_sold"] += quantity
                    category_aggregate[category_id]["product_count"].add(product_id)

            # Count transactions per category
            for sale in all_sales:
                if not include_voided and sale.get("status") == "voided":
                    continue
                    
                for item in sale.get("items", []):
                    product_id = str(item.get("product_id"))
                    category_id = product_id_to_category.get(product_id)
                    if category_id:
                        category_aggregate[category_id]["transaction_count"] += 1
                        break  # Count transaction only once per category

            # 🧾 Build final results with enhanced metrics
            results = []
            for category_id, data in category_aggregate.items():
                category_name = category_id_to_name.get(category_id, "Unknown Category")
                total_sales = round(data["total_sales"], 2)
                total_items = data["total_items_sold"]
                product_count = len(data["product_count"])
                transaction_count = data["transaction_count"]
                
                # Calculate averages
                avg_sale_per_transaction = round(total_sales / transaction_count, 2) if transaction_count > 0 else 0
                avg_items_per_transaction = round(total_items / transaction_count, 2) if transaction_count > 0 else 0

                results.append({
                    "category_id": category_id,
                    "category_name": category_name,
                    "total_sales": total_sales,
                    "total_items_sold": total_items,
                    "product_count": product_count,
                    "transaction_count": transaction_count,
                    "avg_sale_per_transaction": avg_sale_per_transaction,
                    "avg_items_per_transaction": avg_items_per_transaction
                })

            # Sort by total_sales desc
            results.sort(key=lambda x: x["total_sales"], reverse=True)

            print(f"✅ Aggregated {len(results)} categories with enhanced metrics")
            return results

        except Exception as e:
            print(f"❌ Error in get_sales_by_category_with_date_filter: {str(e)}")
            raise e

    def get_top_categories(self, start_date=None, end_date=None, limit=5):
        """
        Return only the top N categories sorted by total sales
        """
        try:
            all_categories = self.get_sales_by_category_with_date_filter(start_date, end_date)
            return all_categories[:limit]
        except Exception as e:
            print(f"❌ Error in get_top_categories: {str(e)}")
            return []

    def get_category_performance_trends(self, start_date=None, end_date=None):
        """
        Get category performance with trend analysis
        """
        try:
            # Get current period data
            current_data = self.get_sales_by_category_with_date_filter(start_date, end_date)
            
            # Calculate previous period for comparison (30 days before)
            if start_date and end_date:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date.replace("Z", "+00:00"))
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                
                period_days = (end_date - start_date).days
                prev_start_date = start_date - timedelta(days=period_days)
                prev_end_date = start_date - timedelta(seconds=1)
                
                previous_data = self.get_sales_by_category_with_date_filter(prev_start_date, prev_end_date)
                
                # Create lookup for previous data
                prev_lookup = {item['category_id']: item for item in previous_data}
                
                # Calculate trends
                for category in current_data:
                    category_id = category['category_id']
                    prev_category = prev_lookup.get(category_id)
                    
                    if prev_category:
                        current_sales = category['total_sales']
                        prev_sales = prev_category['total_sales']
                        
                        if prev_sales > 0:
                            sales_growth = ((current_sales - prev_sales) / prev_sales) * 100
                        else:
                            sales_growth = 100 if current_sales > 0 else 0
                            
                        category['sales_growth_percent'] = round(sales_growth, 2)
                        category['trend'] = 'up' if sales_growth > 0 else 'down' if sales_growth < 0 else 'stable'
                    else:
                        category['sales_growth_percent'] = 100  # New category
                        category['trend'] = 'new'
            
            return current_data
            
        except Exception as e:
            print(f"❌ Error in get_category_performance_trends: {str(e)}")
            return self.get_sales_by_category_with_date_filter(start_date, end_date)  # Fallback to basic data