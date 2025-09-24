from datetime import datetime
from ..database import db_manager
import logging
import csv
from io import StringIO
import json

logger = logging.getLogger(__name__)

class CategoryDisplayService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.category_collection = self.db.category
        self.sales_collection = self.db.sales_log
        self._ensure_sales_indexes()

    def _ensure_sales_indexes(self):
        """Create essential indexes for sales performance"""
        try:
            # Critical for sales performance with string-based operations
            indexes = [
                [("item_list.item_name", 1), ("transaction_date", 1)],
                [("transaction_date", 1)],
                [("item_list.product_id", 1)]  # For PROD-##### lookups
            ]
            
            for index_fields in indexes:
                self.sales_collection.create_index(index_fields, background=True)
            
            logger.info("Sales indexes created")
        except Exception as e:
            logger.warning(f"Could not create sales indexes: {e}")

    def get_categories_display(self, include_deleted=False, limit=50):
        """Optimized aggregation pipeline - string ID format only"""
        try:
            category_match = {}
            if not include_deleted:
                category_match['isDeleted'] = {'$ne': True}
            
            pipeline = [
                {"$match": category_match},
                {"$limit": limit},
                
                # Extract all product names from subcategories (combined format only)
                {"$addFields": {
                    "safe_products": {
                        "$reduce": {
                            "input": {"$ifNull": ["$sub_categories", []]},
                            "initialValue": [],
                            "in": {
                                "$concatArrays": [
                                    "$$value", 
                                    {
                                        "$map": {
                                            "input": {"$ifNull": ["$$this.products", []]},
                                            "as": "product",
                                            "in": "$$product.product_name"  # Only handle combined format
                                        }
                                    }
                                ]
                            }
                        }
                    }
                }},
                
                # Lookup sales data by product names
                {"$lookup": {
                    "from": "sales_log",
                    "let": {"safe_products": "$safe_products"},
                    "pipeline": [
                        {"$unwind": "$item_list"},
                        {"$match": {
                            "$expr": {
                                "$in": ["$item_list.item_name", "$$safe_products"]
                            }
                        }},
                        {"$group": {
                            "_id": "$item_list.item_name",
                            "total_quantity": {"$sum": "$item_list.quantity"},
                            "total_sales": {"$sum": {"$multiply": ["$item_list.quantity", "$item_list.unit_price"]}}
                        }}
                    ],
                    "as": "sales_data"
                }},
                
                # Calculate totals and clean up
                {"$addFields": {
                    "total_sales": {"$sum": "$sales_data.total_sales"},
                    "total_quantity": {"$sum": "$sales_data.total_quantity"}
                }},
                
                {"$unset": "safe_products"}
            ]
            
            results = list(self.category_collection.aggregate(pipeline))
            
            # Process subcategories with sales data
            for category in results:
                subcategories_data = []
                sales_lookup = {item["_id"]: item for item in category.get("sales_data", [])}
                
                for subcategory in category.get('sub_categories', []):
                    subcategory_sales = 0
                    subcategory_quantity = 0
                    
                    products = subcategory.get('products', [])
                    
                    # Only handle combined format (product_id + product_name)
                    for product in products:
                        if isinstance(product, dict):
                            product_name = product.get('product_name')
                            if product_name and product_name in sales_lookup:
                                product_data = sales_lookup[product_name]
                                subcategory_quantity += product_data['total_quantity']
                                subcategory_sales += product_data['total_sales']
                    
                    subcategories_data.append({
                        'name': subcategory.get('name', 'Unknown'),
                        'quantity_sold': subcategory_quantity,
                        'total_sales': round(subcategory_sales, 2),
                        'product_count': len(products)
                    })
                
                category['subcategories'] = subcategories_data
                category['subcategory_count'] = len(subcategories_data)
                
                # Clean up sales_data from final output
                if 'sales_data' in category:
                    del category['sales_data']
            
            logger.info(f"Processed {len(results)} categories for display")
            return results
            
        except Exception as e:
            logger.error(f"Error in optimized categories display: {e}")
            raise Exception(f"Error getting categories display: {str(e)}")

    def get_categories_display(self, include_deleted=False):
        """Main display method - optimized for string IDs"""
        return self.get_categories_display_optimized(include_deleted, limit=100)

    def get_categories_display_with_date_filter(self, start_date=None, end_date=None, frequency='monthly', include_deleted=False):
        """Get categories with date-filtered sales data"""
        try:
            # Build date filter
            date_filter = {}
            if start_date or end_date:
                date_filter["transaction_date"] = {}
                if start_date:
                    from datetime import time
                    if isinstance(start_date, str):
                        from django.utils.dateparse import parse_date
                        start_date = parse_date(start_date)
                    if start_date:
                        start_datetime = datetime.combine(start_date, time.min)
                        date_filter["transaction_date"]["$gte"] = start_datetime
                if end_date:
                    if isinstance(end_date, str):
                        from django.utils.dateparse import parse_date
                        end_date = parse_date(end_date)
                    if end_date:
                        end_datetime = datetime.combine(end_date, time.max)
                        date_filter["transaction_date"]["$lte"] = end_datetime
            
            # Get filtered invoices
            invoices = list(self.sales_collection.find(date_filter, {
                "item_list.item_name": 1,
                "item_list.quantity": 1,
                "item_list.unit_price": 1
            }))

            # Build sales lookup
            item_sales_lookup = {}
            for invoice in invoices:
                for item in invoice.get('item_list', []):
                    item_name = item['item_name']
                    if item_name not in item_sales_lookup:
                        item_sales_lookup[item_name] = {'quantity': 0, 'total_sales': 0}
                    
                    item_total = item['quantity'] * item['unit_price']
                    item_sales_lookup[item_name]['quantity'] += item['quantity']
                    item_sales_lookup[item_name]['total_sales'] += item_total

            # Process categories with string ID operations
            category_filter = {}
            if not include_deleted:
                category_filter['isDeleted'] = {'$ne': True}
                
            categories = list(self.category_collection.find(category_filter))
            categories_with_sales = []

            for category in categories:
                category_total_sales = 0
                category_total_quantity = 0
                subcategories_data = []
                
                for subcategory in category.get('sub_categories', []):
                    subcategory_total_quantity = 0
                    subcategory_total_sales = 0
                    
                    products = subcategory.get('products', [])
                    
                    # Only handle combined format (product_id + product_name)
                    for product in products:
                        if isinstance(product, dict):
                            product_name = product.get('product_name')
                            if product_name and product_name in item_sales_lookup:
                                product_data = item_sales_lookup[product_name]
                                subcategory_total_quantity += product_data['quantity']
                                subcategory_total_sales += product_data['total_sales']
                    
                    category_total_sales += subcategory_total_sales
                    category_total_quantity += subcategory_total_quantity
                    
                    subcategories_data.append({
                        'name': subcategory['name'],
                        'quantity_sold': subcategory_total_quantity,
                        'total_sales': subcategory_total_sales,
                        'product_count': len(products)
                    })
                
                categories_with_sales.append({
                    'category_id': category['category_id'],  # String ID
                    'category_name': category['category_name'],
                    'description': category.get('description', ''),
                    'status': category.get('status', ''),
                    'isDeleted': category.get('isDeleted', False),
                    'deleted_at': category.get('deleted_at'),
                    'date_created': category.get('date_created'),
                    'last_updated': category.get('last_updated'),
                    'total_quantity_sold': category_total_quantity,
                    'total_sales': category_total_sales,
                    'subcategories': subcategories_data,
                    'subcategory_count': len(subcategories_data)
                })

            return {
                'categories': categories_with_sales,
                'total_categories': len(categories_with_sales),
                'date_filter_applied': bool(start_date or end_date),
                'total_invoices': len(invoices),
                'include_deleted': include_deleted
            }
            
        except Exception as e:
            logger.error(f"Error in date filter display: {e}")
            raise Exception(f"Error getting categories with date filter: {str(e)}")

    def export_categories_csv(self, include_sales_data=True, date_filter=None, include_deleted=False):
        """Export categories to CSV format with optional sales data"""
        try:
            # Get categories data
            if include_sales_data:
                if date_filter:
                    result = self.get_categories_display_with_date_filter(
                        start_date=date_filter.get('start_date'),
                        end_date=date_filter.get('end_date'),
                        frequency=date_filter.get('frequency', 'monthly'),
                        include_deleted=include_deleted
                    )
                    categories = result.get('categories', [])
                else:
                    categories = self.get_categories_display(include_deleted=include_deleted)
            else:
                # Basic category data only
                from .category_service import CategoryService
                category_service = CategoryService()
                categories = category_service.get_all_categories(include_deleted=include_deleted)
            
            # Create CSV content
            output = StringIO()
            writer = csv.writer(output)
            
            # Define headers
            if include_sales_data:
                headers = [
                    'Category ID',
                    'Category Name', 
                    'Description', 
                    'Status',
                    'Is Deleted',
                    'Deleted At',
                    'Sub-Categories Count', 
                    'Sub-Categories', 
                    'Total Products',
                    'Total Quantity Sold',
                    'Total Sales (₱)',
                    'Date Created', 
                    'Last Updated'
                ]
            else:
                headers = [
                    'Category ID',
                    'Category Name', 
                    'Description', 
                    'Status',
                    'Is Deleted',
                    'Deleted At',
                    'Sub-Categories Count', 
                    'Sub-Categories', 
                    'Total Products',
                    'Date Created', 
                    'Last Updated'
                ]
            
            writer.writerow(headers)
            
            # Write category data
            for category in categories:
                # Calculate sub-categories info
                sub_categories = category.get('sub_categories', []) or category.get('subcategories', [])
                sub_categories_count = len(sub_categories)
                
                # Format sub-categories names
                if sub_categories_count > 0:
                    sub_category_names = '; '.join([sub.get('name', 'Unknown') for sub in sub_categories])
                else:
                    sub_category_names = 'None'
                
                # Calculate total products
                total_products = 0
                if include_sales_data and 'subcategories' in category:
                    # From display service data
                    total_products = sum(sub.get('product_count', 0) for sub in category.get('subcategories', []))
                elif 'sub_categories' in category:
                    # From basic category data
                    total_products = sum(len(sub.get('products', [])) for sub in category.get('sub_categories', []))
                
                # Format dates
                date_created = self._format_export_date(category.get('date_created'))
                last_updated = self._format_export_date(category.get('last_updated'))
                deleted_at = self._format_export_date(category.get('deleted_at')) if category.get('deleted_at') else 'N/A'
                
                # Build row data
                if include_sales_data:
                    row = [
                        category.get('category_id', 'N/A'),  # String ID
                        category.get('category_name', ''),
                        category.get('description', ''),
                        category.get('status', 'active'),
                        'Yes' if category.get('isDeleted', False) else 'No',
                        deleted_at,
                        sub_categories_count,
                        sub_category_names,
                        total_products,
                        category.get('total_quantity_sold', 0),
                        f"{category.get('total_sales', 0):.2f}",
                        date_created,
                        last_updated
                    ]
                else:
                    row = [
                        category.get('category_id', 'N/A'),  # String ID
                        category.get('category_name', ''),
                        category.get('description', ''),
                        category.get('status', 'active'),
                        'Yes' if category.get('isDeleted', False) else 'No',
                        deleted_at,
                        sub_categories_count,
                        sub_category_names,
                        total_products,
                        date_created,
                        last_updated
                    ]
                
                writer.writerow(row)
            
            # Get CSV content
            csv_content = output.getvalue()
            output.close()
            
            return {
                'content': csv_content,
                'filename': f"categories_export_{datetime.utcnow().strftime('%Y-%m-%d')}.csv",
                'content_type': 'text/csv',
                'total_records': len(categories),
                'include_deleted': include_deleted
            }
            
        except Exception as e:
            raise Exception(f"Error exporting categories to CSV: {str(e)}")

    def export_categories_json(self, include_sales_data=True, date_filter=None, include_deleted=False):
        """Export categories to JSON format with optional sales data"""
        try:
            # Get categories data (same logic as CSV export)
            if include_sales_data:
                if date_filter:
                    result = self.get_categories_display_with_date_filter(
                        start_date=date_filter.get('start_date'),
                        end_date=date_filter.get('end_date'),
                        frequency=date_filter.get('frequency', 'monthly'),
                        include_deleted=include_deleted
                    )
                    categories = result.get('categories', [])
                    export_metadata = {
                        'total_categories': result.get('total_categories', 0),
                        'date_filter_applied': result.get('date_filter_applied', False),
                        'frequency': result.get('frequency', 'monthly'),
                        'total_invoices': result.get('total_invoices', 0),
                        'include_deleted': result.get('include_deleted', False)
                    }
                else:
                    categories = self.get_categories_display(include_deleted=include_deleted)
                    export_metadata = {
                        'total_categories': len(categories),
                        'date_filter_applied': False,
                        'include_deleted': include_deleted
                    }
            else:
                from .category_service import CategoryService
                category_service = CategoryService()
                categories = category_service.get_all_categories(include_deleted=include_deleted)
                export_metadata = {
                    'total_categories': len(categories),
                    'date_filter_applied': False,
                    'include_deleted': include_deleted
                }
            
            # Prepare export data
            export_data = {
                'export_info': {
                    'exported_at': datetime.utcnow().isoformat(),
                    'format': 'json',
                    'include_sales_data': include_sales_data,
                    **export_metadata
                },
                'categories': categories
            }
            
            # Convert to JSON
            json_content = json.dumps(export_data, indent=2, default=str)
            
            return {
                'content': json_content,
                'filename': f"categories_export_{datetime.utcnow().strftime('%Y-%m-%d')}.json",
                'content_type': 'application/json',
                'total_records': len(categories),
                'include_deleted': include_deleted
            }
            
        except Exception as e:
            raise Exception(f"Error exporting categories to JSON: {str(e)}")

    def validate_export_params(self, format_type, include_sales_data, date_filter, include_deleted=False):
        """Validate export parameters"""
        try:
            # Validate format
            valid_formats = ['csv', 'json']
            if format_type not in valid_formats:
                raise ValueError(f"Invalid format. Must be one of: {', '.join(valid_formats)}")
            
            # Validate include_sales_data
            if not isinstance(include_sales_data, bool):
                raise ValueError("include_sales_data must be a boolean")
            
            # Validate include_deleted
            if not isinstance(include_deleted, bool):
                raise ValueError("include_deleted must be a boolean")
            
            # Validate date_filter if provided
            if date_filter:
                if not isinstance(date_filter, dict):
                    raise ValueError("date_filter must be a dictionary")
                
                # Check date format if dates are provided
                for date_key in ['start_date', 'end_date']:
                    if date_key in date_filter and date_filter[date_key]:
                        try:
                            if isinstance(date_filter[date_key], str):
                                datetime.fromisoformat(date_filter[date_key])
                        except ValueError:
                            raise ValueError(f"Invalid {date_key} format. Use ISO format (YYYY-MM-DD)")
            
            return True
            
        except Exception as e:
            raise Exception(f"Export parameter validation failed: {str(e)}")

    def _format_export_date(self, date_value):
        """Helper method to format dates for export"""
        if not date_value:
            return 'N/A'
        
        try:
            if isinstance(date_value, str):
                try:
                    date_obj = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except:
                    return date_value
            elif isinstance(date_value, datetime):
                date_obj = date_value
            else:
                return 'Invalid Date'
            
            return date_obj.strftime('%d-%b-%Y %I:%M %p')
            
        except Exception:
            return 'Invalid Date'