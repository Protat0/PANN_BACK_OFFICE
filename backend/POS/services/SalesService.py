from datetime import datetime
from bson import ObjectId
from ..database import db_manager
from notifications.services import notification_service
from promotionCon import PromoConnection

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
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
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
        """Get recent sales from both POS and sales_log"""
        try:
            all_sales = []
            
            # Get POS sales
            pos_sales = list(self.sales_collection.find({}).sort('transaction_date', -1).limit(limit))
            for sale in pos_sales:
                sale['collection_source'] = 'sales'
                all_sales.append(self.convert_object_id(sale))
            
            # Get sales_log sales  
            log_sales = list(self.sales_log_collection.find({}).sort('transaction_date', -1).limit(limit))
            for sale in log_sales:
                sale['collection_source'] = 'sales_log'
                all_sales.append(self.convert_object_id(sale))
            
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