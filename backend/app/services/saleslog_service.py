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
                    message=f"A new invoice for ${invoice.total_amount} has been created",
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