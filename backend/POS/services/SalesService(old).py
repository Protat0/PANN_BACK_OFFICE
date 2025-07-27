
from datetime import datetime
from bson import ObjectId
from ..database import db_manager
from notifications.services import notification_service

class SalesServiceOld:
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

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document

    # ================================================================
    # UNIFIED SALES CREATION
    # ================================================================

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

    # ================================================================
    # UNIFIED REPORTING
    # ================================================================

    def get_all_sales_unified(self, date_range=None, include_source=None):
        """
        Get sales from both collections for unified reporting
        
        Args:
            date_range: {'start': datetime, 'end': datetime}
            include_source: List of sources to include ['pos', 'csv', 'manual'] or None for all
        """
        try:
            match_conditions = []
            
            # Date range filter
            if date_range:
                date_filter = {
                    "transaction_date": {
                        "$gte": date_range['start'],
                        "$lte": date_range['end']
                    }
                }
                match_conditions.append(date_filter)

            # Source filter
            if include_source:
                source_filter = {"source": {"$in": include_source}}
                match_conditions.append(source_filter)

            # Build match stage
            match_stage = {"$and": match_conditions} if match_conditions else {}

            # Get POS sales
            pos_sales = list(self.sales_collection.find(match_stage))
            
            # Get sales log entries
            sales_log_entries = list(self.sales_log_collection.find(match_stage))

            # Normalize both formats
            unified_sales = []
            
            # Process POS sales
            for sale in pos_sales:
                unified_sale = self._normalize_pos_sale(sale)
                unified_sales.append(unified_sale)

            # Process sales log entries
            for sale in sales_log_entries:
                unified_sale = self._normalize_sales_log(sale)
                unified_sales.append(unified_sale)

            # Sort by transaction date
            unified_sales.sort(key=lambda x: x['transaction_date'], reverse=True)

            return unified_sales

        except Exception as e:
            raise Exception(f"Error getting unified sales: {str(e)}")

    def _normalize_pos_sale(self, pos_sale):
        """Convert POS sale to unified format"""
        return {
            '_id': str(pos_sale['_id']),
            'transaction_date': pos_sale['transaction_date'],
            'total_amount': pos_sale['final_amount'],
            'gross_amount': pos_sale.get('total_amount', pos_sale['final_amount']),
            'discount_amount': pos_sale.get('total_discount', 0),
            'payment_method': pos_sale.get('payment_method', 'cash'),
            'customer_id': pos_sale.get('customer_id'),
            'cashier_id': pos_sale.get('cashier_id'),
            'promotion_applied': pos_sale.get('promotion_applied'),
            'items': pos_sale.get('items', []),
            'source': 'pos',
            'status': pos_sale.get('status', 'completed'),
            'collection': 'sales'
        }

    def _normalize_sales_log(self, sales_log):
        """Convert sales log to unified format"""
        return {
            '_id': str(sales_log['_id']),
            'transaction_date': sales_log['transaction_date'],
            'total_amount': sales_log['total_amount'],
            'gross_amount': sales_log['total_amount'],
            'discount_amount': 0,  # Sales logs don't typically have discounts
            'payment_method': sales_log.get('payment_method', 'cash'),
            'customer_id': str(sales_log['customer_id']) if sales_log.get('customer_id') else None,
            'cashier_id': str(sales_log['user_id']) if sales_log.get('user_id') else None,
            'promotion_applied': None,
            'items': self._convert_item_list_to_items(sales_log.get('item_list', [])),
            'source': sales_log.get('source', 'manual'),
            'status': sales_log.get('status', 'completed'),
            'collection': 'sales_log'
        }

    def _convert_item_list_to_items(self, item_list):
        """Convert sales log item_list to POS items format"""
        items = []
        for item in item_list:
            items.append({
                'product_id': item.get('item_code', ''),
                'product_name': item.get('item_name', ''),
                'quantity': item.get('quantity', 0),
                'price': item.get('unit_price', 0),
                'total': item.get('total_price', 0)
            })
        return items

    # ================================================================
    # ENHANCED REPORTING WITH BOTH COLLECTIONS
    # ================================================================

    def get_comprehensive_sales_report(self, date_range=None):
        """Get comprehensive sales report from both POS and sales log"""
        try:
            unified_sales = self.get_all_sales_unified(date_range)
            
            # Calculate totals
            total_revenue = sum(sale['total_amount'] for sale in unified_sales)
            total_discount = sum(sale['discount_amount'] for sale in unified_sales)
            gross_revenue = sum(sale['gross_amount'] for sale in unified_sales)
            transaction_count = len(unified_sales)
            
            # Break down by source
            source_breakdown = {}
            for sale in unified_sales:
                source = sale['source']
                if source not in source_breakdown:
                    source_breakdown[source] = {
                        'count': 0,
                        'revenue': 0,
                        'discount': 0
                    }
                source_breakdown[source]['count'] += 1
                source_breakdown[source]['revenue'] += sale['total_amount']
                source_breakdown[source]['discount'] += sale['discount_amount']

            # Payment method breakdown
            payment_breakdown = {}
            for sale in unified_sales:
                payment_method = sale['payment_method']
                if payment_method not in payment_breakdown:
                    payment_breakdown[payment_method] = {
                        'count': 0,
                        'revenue': 0
                    }
                payment_breakdown[payment_method]['count'] += 1
                payment_breakdown[payment_method]['revenue'] += sale['total_amount']

            return {
                'summary': {
                    'total_revenue': round(total_revenue, 2),
                    'total_discount': round(total_discount, 2),
                    'gross_revenue': round(gross_revenue, 2),
                    'transaction_count': transaction_count,
                    'avg_transaction_value': round(total_revenue / transaction_count, 2) if transaction_count > 0 else 0
                },
                'source_breakdown': source_breakdown,
                'payment_breakdown': payment_breakdown,
                'transactions': unified_sales[:50]  # Return first 50 for display
            }

        except Exception as e:
            raise Exception(f"Error generating comprehensive sales report: {str(e)}")