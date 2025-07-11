from bson import ObjectId
from datetime import datetime
from ..database import db_manager 
from ..models import SalesLog
import bcrypt
from notifications.services import notification_service

class SalesLogService():
    def __init__(self):
        self.db = db_manager.get_database()  
        self.sales_log_collection = self.db.sales_log  
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document:
            if '_id' in document and isinstance(document['_id'], ObjectId):
                document['_id'] = str(document['_id'])
            if 'customer_id' in document and isinstance(document['customer_id'], ObjectId):
                document['customer_id'] = str(document['customer_id'])
            if 'user_id' in document and isinstance(document['user_id'], ObjectId):
                document['user_id'] = str(document['user_id'])
            # Convert datetime to ISO format string
            if 'transaction_date' in document and isinstance(document['transaction_date'], datetime):
                document['transaction_date'] = document['transaction_date'].isoformat()
        return document
    
    def create_invoice(self, invoice_data):
        try:
            # Create SalesLog instance with all invoice data
            invoice = SalesLog(**invoice_data)
            
            # Convert to dictionary for MongoDB insertion (preserves ObjectIds)
            invoice_dict = invoice.to_mongodb_dict()
            
            # Insert into MongoDB
            result = self.sales_log_collection.insert_one(invoice_dict)
            
            # Update the invoice object with the inserted ID
            invoice._id = result.inserted_id
            
            # Create notification
            try:
                notification_service.create_notification(
                    title="New Invoice Created",
                    message=f"A new invoice for ₱{invoice.total_amount} has been created",
                    priority="medium",
                    notification_type="system",
                    metadata={
                        "invoice_id": str(invoice._id),
                        "total_amount": invoice.total_amount,
                        "sales_type": invoice.sales_type,
                        "customer_id": str(invoice.customer_id),
                        "user_id": str(invoice.user_id),
                        "registration_source": "invoice_creation",
                        "action_type": "invoice_created"
                    }
                )
            except Exception as notification_error:
                print(f"Failed to create notification for new invoice: {notification_error}")
            
            # Return JSON-serializable dictionary
            return invoice.to_dict()
            
        except Exception as e:
            raise Exception(f"Error creating invoice: {str(e)}")
    
    def get_invoice_by_id(self, invoice_id):
        """Get invoice by ID"""
        try:
            if isinstance(invoice_id, str):
                invoice_id = ObjectId(invoice_id)
            
            invoice_doc = self.sales_log_collection.find_one({"_id": invoice_id})
            
            if invoice_doc:
                return self.convert_object_id(invoice_doc)
            return None
            
        except Exception as e:
            raise Exception(f"Error retrieving invoice: {str(e)}")
    
    def get_all_invoices(self, limit=100, skip=0):
        """Get all invoices with pagination"""
        try:
            invoices = list(self.sales_log_collection.find().skip(skip).limit(limit))
            
            # Convert ObjectIds to strings
            for invoice in invoices:
                self.convert_object_id(invoice)
            
            return invoices
            
        except Exception as e:
            raise Exception(f"Error retrieving invoices: {str(e)}")
    
    def update_invoice(self, invoice_id, update_data):
        """Update an existing invoice"""
        try:
            if isinstance(invoice_id, str):
                invoice_id = ObjectId(invoice_id)
            
            # Remove _id from update_data if present
            update_data.pop('_id', None)
            
            result = self.sales_log_collection.update_one(
                {"_id": invoice_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                return self.get_invoice_by_id(invoice_id)
            else:
                return None
                
        except Exception as e:
            raise Exception(f"Error updating invoice: {str(e)}")
    
    def delete_invoice(self, invoice_id):
        """Delete an invoice"""
        try:
            if isinstance(invoice_id, str):
                invoice_id = ObjectId(invoice_id)
            
            result = self.sales_log_collection.delete_one({"_id": invoice_id})
            
            return result.deleted_count > 0
            
        except Exception as e:
            raise Exception(f"Error deleting invoice: {str(e)}")

    def get_transactions_for_export(self, filters=None):
        """Get transactions for CSV export with optional filtering"""
        try:
            query = {}
            
            # Apply filters if provided
            if filters:
                # Date range filtering
                if filters.get('start_date') and filters.get('end_date'):
                    try:
                        from django.utils.dateparse import parse_date
                        from datetime import time
                        
                        # Parse start date
                        if isinstance(filters['start_date'], str):
                            start_date = parse_date(filters['start_date'])
                        else:
                            start_date = filters['start_date']
                        
                        # Parse end date
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
                        # Continue without date filter if parsing fails
                
                # Sales type filtering
                if filters.get('sales_type'):
                    query['sales_type'] = filters['sales_type']
                
                # Payment method filtering
                if filters.get('payment_method'):
                    query['payment_method'] = filters['payment_method']
                
                # Status filtering
                if filters.get('status'):
                    query['status'] = filters['status']
                
                # Customer ID filtering
                if filters.get('customer_id'):
                    try:
                        customer_id = ObjectId(filters['customer_id'])
                        query['customer_id'] = customer_id
                    except Exception:
                        # Skip invalid customer_id
                        pass
            
            print(f"Export query: {query}")  # Debug log
            
            # Get transactions from MongoDB with a reasonable limit
            transactions = list(self.sales_log_collection.find(query).limit(10000))
            
            print(f"Found {len(transactions)} transactions for export")  # Debug log
            
            # Convert ObjectIds to strings for processing
            for transaction in transactions:
                self.convert_object_id(transaction)
            
            return transactions
            
        except Exception as e:
            print(f"Error in get_transactions_for_export: {str(e)}")
            raise Exception(f"Error retrieving transactions for export: {str(e)}")
        
        
class SalesLogItemReport():
    
    def __init__(self):
        self.db = db_manager.get_database()  
        self.sales_log_collection = self.db.sales_log  

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document:
            if '_id' in document and isinstance(document['_id'], ObjectId):
                document['_id'] = str(document['_id'])
            if 'customer_id' in document and isinstance(document['customer_id'], ObjectId):
                document['customer_id'] = str(document['customer_id'])
            if 'user_id' in document and isinstance(document['user_id'], ObjectId):
                document['user_id'] = str(document['user_id'])
            # Convert datetime to ISO format string
            if 'transaction_date' in document and isinstance(document['transaction_date'], datetime):
                document['transaction_date'] = document['transaction_date'].isoformat()
        return document
    
class SalesItemHistory():
    def __init__(self):
        self.db = db_manager.get_database()  
        self.sales_log_collection = self.db.sales_log

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document:
            if '_id' in document and isinstance(document['_id'], ObjectId):
                document['_id'] = str(document['_id'])
            if 'customer_id' in document and isinstance(document['customer_id'], ObjectId):
                document['customer_id'] = str(document['customer_id'])
            if 'user_id' in document and isinstance(document['user_id'], ObjectId):
                document['user_id'] = str(document['user_id'])
            # Convert datetime to ISO format string
            if 'transaction_date' in document and isinstance(document['transaction_date'], datetime):
                document['transaction_date'] = document['transaction_date'].isoformat()
        return document

    def fetch_item_history(self, page=1, page_size=50):
        try:
            # Calculate skip value for pagination
            skip = (page - 1) * page_size
            
            # Use projection to fetch only specific fields
            projection = {
                "_id": 1,
                "item_list.item_name": 1,
                "customer_id": 1,
                "transaction_date": 1,
                "payment_method": 1,
                "sales_type": 1,
                "total_amount": 1,
                "item_list.quantity":1,
                "item_list.unit_price":1, 
            }
            
            # Fetch documents with pagination
            invoices = list(self.sales_log_collection.find({}, projection).skip(skip).limit(page_size))
            
            # Get total count for pagination info
            total_count = self.sales_log_collection.count_documents({})
            total_pages = (total_count + page_size - 1) // page_size  # Ceiling division
            
            # Convert ObjectIds to strings
            for invoice in invoices:
                self.convert_object_id(invoice)
            
            # Return data with pagination info
            return {
                "data": invoices,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_records": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_prev": page > 1
                }
            }
            
        except Exception as e:
            raise Exception(f"Error retrieving invoices: {str(e)}")
        
class SalesTopItem():
    def __init__(self):
        self.db = db_manager.get_database()  
        self.sales_log_collection = self.db.sales_log

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document:
            if '_id' in document and isinstance(document['_id'], ObjectId):
                document['_id'] = str(document['_id'])
            if 'customer_id' in document and isinstance(document['customer_id'], ObjectId):
                document['customer_id'] = str(document['customer_id'])
            if 'user_id' in document and isinstance(document['user_id'], ObjectId):
                document['user_id'] = str(document['user_id'])
            # Convert datetime to ISO format string
            if 'transaction_date' in document and isinstance(document['transaction_date'], datetime):
                document['transaction_date'] = document['transaction_date'].isoformat()
        return document

    def fetch_top_item(self, limit=5):
        try:
            projection = {
                "item_list.item_name": 1,
                "total_amount": 1
            }
            
            invoices = list(self.sales_log_collection.find({}, projection))
            total_count = self.sales_log_collection.count_documents({})
            
            item_totals = {}
            
            for invoice in invoices:
                # Check if invoice has item_list and total_amount
                if 'item_list' in invoice and 'total_amount' in invoice:
                    total_amount = invoice['total_amount']
                    
                    # Handle case where item_list might be a list of items
                    if isinstance(invoice['item_list'], list):
                        for item in invoice['item_list']:
                            if 'item_name' in item:
                                item_name = item['item_name']
                                if item_name in item_totals:
                                    item_totals[item_name] += total_amount
                                else:
                                    item_totals[item_name] = total_amount
                    
                    # Handle case where item_list has direct item_name
                    elif 'item_name' in invoice['item_list']:
                        item_name = invoice['item_list']['item_name']
                        if item_name in item_totals:
                            item_totals[item_name] += total_amount
                        else:
                            item_totals[item_name] = total_amount
            
            # Convert to list of dictionaries and sort by total amount (descending)
            result = [
                {"item_name": name, "total_amount": amount} 
                for name, amount in item_totals.items()
            ]
            result.sort(key=lambda x: x['total_amount'], reverse=True)
            
            # Limit the results to the specified number
            top_items = result[:limit]
            
            return {
                "items": top_items,
                "total_invoices": total_count,
                "showing_top": len(top_items)
            }
            
        except Exception as e:
            raise Exception(f"Error retrieving invoices: {str(e)}")
        

    def fetch_all_top_item(self, start_date=None, end_date=None, frequency='monthly'):
        try:
            projection = {
                "item_list.item_name": 1,
                "item_list.quantity": 1,
                "item_list.unit_price": 1,
                "total_amount": 1,
                "transaction_date": 1,
            }
            
            # Build date filter query
            date_filter = {}
            if start_date or end_date:
                date_filter["transaction_date"] = {}
                if start_date:
                    # Convert date to datetime for proper MongoDB querying
                    from datetime import datetime, time
                    if isinstance(start_date, str):
                        from django.utils.dateparse import parse_date
                        start_date = parse_date(start_date)
                    if start_date:  # Check if parsing was successful
                        start_datetime = datetime.combine(start_date, time.min)
                        date_filter["transaction_date"]["$gte"] = start_datetime
                if end_date:
                    # Convert date to datetime for proper MongoDB querying
                    if isinstance(end_date, str):
                        from django.utils.dateparse import parse_date
                        end_date = parse_date(end_date)
                    if end_date:  # Check if parsing was successful
                        end_datetime = datetime.combine(end_date, time.max)
                        date_filter["transaction_date"]["$lte"] = end_datetime
            
            # Apply the filter to the query
            query_filter = date_filter if date_filter else {}
            
            print(f"MongoDB Query Filter: {query_filter}")  # Debug log
            print(f"Date range: {start_date} to {end_date}, Frequency: {frequency}")  # Debug log
            
            invoices = list(self.sales_log_collection.find(query_filter, projection))
            total_count = self.sales_log_collection.count_documents(query_filter)
            
            print(f"Found {len(invoices)} invoices matching date filter")  # Debug log
            
            item_totals = {}
            
            for invoice in invoices:
                # Check if invoice has item_list and total_amount
                if 'item_list' in invoice and 'total_amount' in invoice:
                    total_amount = invoice['total_amount']
                    transaction_date = invoice.get('transaction_date')
                    
                    # Handle case where item_list might be a list of items
                    if isinstance(invoice['item_list'], list):
                        for item in invoice['item_list']:
                            if 'item_name' in item:
                                item_name = item['item_name']
                                quantity = item.get('quantity', 0)
                                unit_price = item.get('unit_price', 0)
                                
                                if item_name in item_totals:
                                    item_totals[item_name]['total_amount'] += total_amount
                                    item_totals[item_name]['total_quantity'] += quantity
                                    # For unit_price, we might want to track average or just keep the latest
                                    # Here I'm keeping the most recent unit_price
                                    item_totals[item_name]['unit_price'] = unit_price
                                    # Keep the most recent transaction date
                                    if transaction_date and (not item_totals[item_name]['latest_transaction_date'] or 
                                                        transaction_date > item_totals[item_name]['latest_transaction_date']):
                                        item_totals[item_name]['latest_transaction_date'] = transaction_date
                                else:
                                    item_totals[item_name] = {
                                        'total_amount': total_amount,
                                        'total_quantity': quantity,
                                        'unit_price': unit_price,
                                        'latest_transaction_date': transaction_date
                                    }
                    
                    # Handle case where item_list has direct item_name
                    elif 'item_name' in invoice['item_list']:
                        item_name = invoice['item_list']['item_name']
                        quantity = invoice['item_list'].get('quantity', 0)
                        unit_price = invoice['item_list'].get('unit_price', 0)
                        
                        if item_name in item_totals:
                            item_totals[item_name]['total_amount'] += total_amount
                            item_totals[item_name]['total_quantity'] += quantity
                            item_totals[item_name]['unit_price'] = unit_price
                            # Keep the most recent transaction date
                            if transaction_date and (not item_totals[item_name]['latest_transaction_date'] or 
                                                transaction_date > item_totals[item_name]['latest_transaction_date']):
                                item_totals[item_name]['latest_transaction_date'] = transaction_date
                        else:
                            item_totals[item_name] = {
                                'total_amount': total_amount,
                                'total_quantity': quantity,
                                'unit_price': unit_price,
                                'latest_transaction_date': transaction_date
                            }
            
            # Convert to list of dictionaries and sort by total amount (descending)
            # Handle None values in latest_transaction_date
            result = []
            for name, data in item_totals.items():
                # Handle None transaction date by converting to string
                latest_date = data['latest_transaction_date']
                if latest_date:
                    if hasattr(latest_date, 'isoformat'):
                        latest_date_str = latest_date.isoformat()
                    else:
                        latest_date_str = str(latest_date)
                else:
                    latest_date_str = None
                
                result.append({
                    "item_name": name, 
                    "total_amount": data['total_amount'],
                    "total_quantity": data['total_quantity'],
                    "unit_price": data['unit_price'],
                    "latest_transaction_date": latest_date_str
                })
            
            result.sort(key=lambda x: x['total_amount'], reverse=True)
            
            # Prepare safe date strings for response
            start_date_str = None
            end_date_str = None
            
            if start_date:
                if hasattr(start_date, 'isoformat'):
                    start_date_str = start_date.isoformat()
                else:
                    start_date_str = str(start_date)
                    
            if end_date:
                if hasattr(end_date, 'isoformat'):
                    end_date_str = end_date.isoformat()
                else:
                    end_date_str = str(end_date)
            
            return {
                "items": result,
                "total_invoices": total_count,
                "showing_top": len(result),
                "date_filter_applied": bool(start_date or end_date),
                "frequency": frequency,
                "date_range": {
                    "start_date": start_date_str,
                    "end_date": end_date_str
                }
            }
            
        except Exception as e:
            print(f"Error in fetch_all_top_item: {str(e)}")  # Debug log
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")  # Full error details
            raise Exception(f"Error retrieving invoices with date filter: {str(e)}")