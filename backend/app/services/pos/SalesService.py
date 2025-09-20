from datetime import datetime
from bson import ObjectId
from ...database import db_manager
from notifications.services import notification_service
from .promotionCon import PromoConnection

class SalesService:
    """
    Unified service that combines POS transactions and sales logging
    Works with both PromoConnection and SalesLogService
    """
    def __init__(self):
        self.db = db_manager.get_database()
        self.sales_collection = self.db.sales  # POS transactions
        self.sales_log_collection = self.db.sales_log  # Imported/manual sales
        self.products_collection = self.db.products
        self.promotions_collection = self.db.promotions
        self.promo_connection = PromoConnection()

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization - Enhanced version"""
        if document is None:
            return document
        
        if isinstance(document, list):
            return [self.convert_object_id(item) for item in document]
        
        if isinstance(document, dict):
            converted = {}
            for key, value in document.items():
                if isinstance(value, ObjectId):
                    converted[key] = str(value)
                elif isinstance(value, (dict, list)):
                    converted[key] = self.convert_object_id(value)
                else:
                    converted[key] = value
            return converted
        
        if isinstance(document, ObjectId):
            return str(document)
        
        return document
    
    def create_unified_sale(self, sale_data, source='pos'):
        """
        Create a sale record that works for both POS and manual entry
        
        Args:
            sale_data: Sale information
            source: 'pos' for POS transactions, 'manual' for manual entry, 'csv' for imports
        """
        try:
            if source == 'pos':
                # Use POS format (your existing PromoConnection.create_sales)
                return self._create_pos_sale(sale_data)
            else:
                # Use sales log format (your existing SalesLogService.create_invoice)
                return self._create_sales_log(sale_data, source)
                
        except Exception as e:
            raise Exception(f"Error creating unified sale: {str(e)}")

    def _create_pos_sale(self, sale_data):
        """Create POS-style sale record"""
        try:
            sales_record = {
                'sale_id': str(ObjectId()),
                'items': sale_data['items'],
                'total_amount': sale_data['total_amount'],
                'total_discount': sale_data.get('total_discount', 0),
                'final_amount': sale_data.get('final_amount', sale_data['total_amount']),
                'promotion_applied': sale_data.get('promotion_applied', None),
                'payment_method': sale_data.get('payment_method', 'cash'),
                'cashier_id': sale_data.get('cashier_id', None),
                'customer_id': sale_data.get('customer_id', None),
                'transaction_date': datetime.utcnow(),
                'status': 'completed',
                'source': 'pos',
                'created_at': datetime.utcnow(),
                'last_updated': datetime.utcnow()
            }

            result = self.sales_collection.insert_one(sales_record)
            sales_record['_id'] = str(result.inserted_id)

            # Send notification
            self._send_sale_notification(sales_record, 'pos_sale_created')

            return {
                'success': True,
                'message': 'POS sale created successfully',
                'data': sales_record
            }

        except Exception as e:
            raise Exception(f"Error creating POS sale: {str(e)}")

    def _create_sales_log(self, sale_data, source):
        """Create sales log style record"""
        try:
            # Convert POS format to sales log format if needed
            if 'items' in sale_data and isinstance(sale_data['items'], list):
                # Convert POS items format to sales log item_list format
                item_list = []
                for item in sale_data['items']:
                    item_list.append({
                        'item_code': item.get('product_id', ''),
                        'item_name': item.get('product_name', ''),
                        'quantity': item.get('quantity', 0),
                        'unit_price': item.get('price', 0),
                        'total_price': item.get('price', 0) * item.get('quantity', 0),
                        'unit_of_measure': item.get('unit', 'pc'),
                        'tax_amount': 0,
                        'imported_from_csv': source == 'csv'
                    })
            else:
                item_list = sale_data.get('item_list', [])

            sales_log_record = {
                'customer_id': ObjectId(sale_data['customer_id']) if sale_data.get('customer_id') else None,
                'user_id': ObjectId(sale_data['user_id']) if sale_data.get('user_id') else None,
                'transaction_date': sale_data.get('transaction_date', datetime.utcnow()),
                'total_amount': sale_data['total_amount'],
                'status': sale_data.get('status', 'completed'),
                'payment_method': sale_data.get('payment_method', 'cash'),
                'sales_type': sale_data.get('sales_type', 'retail'),
                'tax_rate': sale_data.get('tax_rate', 0),
                'tax_amount': sale_data.get('tax_amount', 0),
                'is_taxable': sale_data.get('is_taxable', False),
                'notes': sale_data.get('notes', ''),
                'item_list': item_list,
                'source': source,
                'sync_logs': sale_data.get('sync_logs', [])
            }

            result = self.sales_log_collection.insert_one(sales_log_record)
            sales_log_record['_id'] = str(result.inserted_id)

            # Send notification
            self._send_sale_notification(sales_log_record, f'{source}_sale_created')

            return {
                'success': True,
                'message': f'{source.title()} sale logged successfully',
                'data': self.convert_object_id(sales_log_record)
            }

        except Exception as e:
            raise Exception(f"Error creating sales log: {str(e)}")

    def _send_sale_notification(self, sale_record, notification_type):
        """Send notification for sale creation"""
        try:
            total_amount = sale_record.get('total_amount', 0)
            source = sale_record.get('source', 'unknown')
            
            if notification_type == 'pos_sale_created':
                title = "POS Sale Completed"
                message = f"New POS transaction completed for ₱{total_amount}"
                priority = "low"
            elif notification_type == 'csv_sale_created':
                title = "CSV Sale Imported"
                message = f"Sale imported from CSV for ₱{total_amount}"
                priority = "low"
            elif notification_type == 'manual_sale_created':
                title = "Manual Sale Entered"
                message = f"Manual sale entry for ₱{total_amount}"
                priority = "low"
            else:
                title = "Sale Created"
                message = f"New sale recorded for ₱{total_amount}"
                priority = "low"

            notification_service.create_notification(
                title=title,
                message=message,
                priority=priority,
                notification_type="sales",
                metadata={
                    "sale_id": str(sale_record.get('_id', '')),
                    "total_amount": total_amount,
                    "source": source,
                    "payment_method": sale_record.get('payment_method', ''),
                    "action_type": notification_type
                }
            )

        except Exception as notification_error:
            print(f"Failed to create sale notification: {notification_error}")

    def get_pos_sale_by_id(self, sale_id):
        """Get a POS sale by ID from sales collection only"""
        try:
            # Convert string to ObjectId
            if isinstance(sale_id, str):
                object_id = ObjectId(sale_id)
            else:
                object_id = sale_id
            
            # Correct MongoDB query syntax
            sale = self.sales_collection.find_one({'_id': object_id})
            
            if sale:
                return self.convert_object_id(sale)
            return None
            
        except Exception as e:
            raise Exception(f"Error fetching POS sale by ID: {str(e)}")
    
    def get_recent_sales(self, limit=10):
        """Get recent sales from both POS and sales_log - Fixed version"""
        try:
            all_sales = []
            
            # Get POS sales
            pos_sales = list(self.sales_collection.find({}).sort('transaction_date', -1).limit(limit))
            for sale in pos_sales:
                sale['collection_source'] = 'sales'
                all_sales.append(self.convert_object_id(sale))  # ✅ Fix ObjectId
            
            # Get sales_log sales  
            log_sales = list(self.sales_log_collection.find({}).sort('transaction_date', -1).limit(limit))
            for sale in log_sales:
                sale['collection_source'] = 'sales_log'
                all_sales.append(self.convert_object_id(sale))  # ✅ Fix ObjectId
            
            # Sort by date and limit
            all_sales.sort(key=lambda x: x['transaction_date'], reverse=True)
            return all_sales[:limit]
            
        except Exception as e:
            raise Exception(f"Error fetching recent sales: {str(e)}")
        
    def get_sales_by_date_range(self, start_date, end_date, source=None):
        """Create sales log style record"""
        try:
           
            return

        except Exception as e:
            raise Exception(f"Error Fetching sale by ID: {str(e)}")
        
    def get_sales_log_by_id(self, log_id):
        """
        ✅ MISSING METHOD: Get sales log by ID from sales_log collection
        This is what SalesLogService.get_invoice_by_id() is trying to call
        """
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
            
            log_doc = self.sales_log_collection.find_one({"_id": log_id})
            
            if log_doc:
                return self.convert_object_id(log_doc)
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving sales log by ID: {str(e)}")

    def update_sales_log(self, log_id, update_data):
        """
        ✅ MISSING METHOD: Update an existing sales log
        """
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
            
            # Remove _id from update_data if present
            update_data.pop('_id', None)
            
            result = self.sales_log_collection.update_one(
                {"_id": log_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_sales_log_by_id(log_id)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Error updating sales log: {str(e)}")

    def delete_sales_log(self, log_id):
        """
        ✅ MISSING METHOD: Delete a sales log
        """
        try:
            if isinstance(log_id, str):
                log_id = ObjectId(log_id)
            
            result = self.sales_log_collection.delete_one({"_id": log_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Error deleting sales log: {str(e)}")

    def get_all_sales_logs(self, limit=100, skip=0):
        """
        ✅ MISSING METHOD: Get all sales logs with pagination
        """
        try:
            logs = list(self.sales_log_collection.find().skip(skip).limit(limit))
            
            # Convert ObjectIds to strings
            for log in logs:
                self.convert_object_id(log)
            
            return logs
            
        except Exception as e:
            raise Exception(f"Error retrieving sales logs: {str(e)}")

    def get_sales_logs_paginated(self, page=1, page_size=50, filters=None):
        """
        ✅ MISSING METHOD: Get sales logs with advanced pagination and filtering
        """
        try:
            skip = (page - 1) * page_size
            query = {}
            
            # Apply filters if provided
            if filters:
                if filters.get('start_date') and filters.get('end_date'):
                    query['transaction_date'] = {
                        '$gte': filters['start_date'],
                        '$lte': filters['end_date']
                    }
                if filters.get('sales_type'):
                    query['sales_type'] = filters['sales_type']
                if filters.get('source'):
                    query['source'] = filters['source']
                if filters.get('payment_method'):
                    query['payment_method'] = filters['payment_method']
                if filters.get('customer_id'):
                    try:
                        query['customer_id'] = ObjectId(filters['customer_id'])
                    except:
                        pass  # Skip invalid customer_id
            
            # Get logs with pagination
            logs = list(self.sales_log_collection.find(query).skip(skip).limit(page_size))
            total_count = self.sales_log_collection.count_documents(query)
            total_pages = (total_count + page_size - 1) // page_size
            
            # Convert ObjectIds
            for log in logs:
                self.convert_object_id(log)
            
            return {
                "data": logs,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_records": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                },
                "filters_applied": filters or {}
            }
            
        except Exception as e:
            raise Exception(f"Error retrieving paginated sales logs: {str(e)}")

    def get_sales_logs_for_export(self, filters=None):
        """
        ✅ MISSING METHOD: Get sales logs for export with filtering
        """
        try:
            query = {}
            
            # Apply filters if provided
            if filters:
                # Date range filtering
                if filters.get('start_date') and filters.get('end_date'):
                    try:
                        from django.utils.dateparse import parse_date
                        from datetime import time
                        
                        # Parse dates
                        if isinstance(filters['start_date'], str):
                            start_date = parse_date(filters['start_date'])
                        else:
                            start_date = filters['start_date']
                        
                        if isinstance(filters['end_date'], str):
                            end_date = parse_date(filters['end_date'])
                        else:
                            end_date = filters['end_date']
                        
                        if start_date and end_date:
                            start_datetime = datetime.combine(start_date, time.min)
                            end_datetime = datetime.combine(end_date, time.max)
                            query['transaction_date'] = {
                                '$gte': start_datetime, 
                                '$lte': end_datetime
                            }
                    except Exception as date_error:
                        print(f"Date parsing error: {date_error}")
                
                # Other filters
                if filters.get('sales_type'):
                    query['sales_type'] = filters['sales_type']
                if filters.get('payment_method'):
                    query['payment_method'] = filters['payment_method']
                if filters.get('status'):
                    query['status'] = filters['status']
                if filters.get('source'):
                    query['source'] = filters['source']
                if filters.get('customer_id'):
                    try:
                        query['customer_id'] = ObjectId(filters['customer_id'])
                    except:
                        pass
            
            print(f"Export query: {query}")
            
            # Get transactions with a reasonable limit for export
            transactions = list(self.sales_log_collection.find(query).limit(10000))
            
            print(f"Found {len(transactions)} transactions for export")
            
            # Convert ObjectIds to strings
            for transaction in transactions:
                self.convert_object_id(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error in get_sales_logs_for_export: {str(e)}")
            raise Exception(f"Error retrieving sales logs for export: {str(e)}")

    def get_sales_by_date_range(self, start_date, end_date, source=None):
        """
        ✅ COMPLETE THIS METHOD: Get sales by date range
        """
        try:
            query = {
                'transaction_date': {
                    '$gte': start_date,
                    '$lte': end_date
                }
            }
            
            if source:
                query['source'] = source
            
            # Get from both collections
            pos_sales = list(self.sales_collection.find(query))
            log_sales = list(self.sales_log_collection.find(query))
            
            # Combine and convert
            all_sales = []
            
            for sale in pos_sales:
                sale['collection_source'] = 'sales'
                all_sales.append(self.convert_object_id(sale))
            
            for sale in log_sales:
                sale['collection_source'] = 'sales_log'
                all_sales.append(self.convert_object_id(sale))
            
            # Sort by date
            all_sales.sort(key=lambda x: x['transaction_date'], reverse=True)
            
            return all_sales
            
        except Exception as e:
            raise Exception(f"Error fetching sales by date range: {str(e)}")