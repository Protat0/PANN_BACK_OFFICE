# notifications/services.py
from datetime import datetime
from bson import ObjectId
from django.contrib.auth.models import User
from app.database import db_manager
import uuid

class NotificationService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.notifications
    
    def create_notification(self, title, message, recipient_id=None, recipient_username=None, 
                          priority='medium', notification_type='system', metadata=None):
        """Create a new notification"""
        try:
            notification_doc = {
                "_id": ObjectId(),
                "title": title,
                "message": message,
                "priority": priority,
                "is_read": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "notification_type": notification_type,
                "metadata": metadata or {}
            }
            
            # Only add recipient info if provided
            if recipient_id or recipient_username:
                recipient = self._get_recipient(recipient_id, recipient_username)
                if not recipient:
                    raise ValueError("Recipient not found")
                
                notification_doc.update({
                    "recipient_id": str(recipient.id),
                    "recipient_username": recipient.username
                })
            
            result = self.collection.insert_one(notification_doc)
            notification_doc['_id'] = str(result.inserted_id)
            
            return notification_doc
            
        except Exception as e:
            raise Exception(f"Error creating notification: {str(e)}")
    
    def create_inventory_alert(self, recipient_id, product_id, current_stock, product_name=None):
        """Create an inventory alert notification"""
        title = "Low Stock Alert"
        message = f"{product_name or 'Product'} is running low"
        
        metadata = {
            "product_id": product_id,
            "current_stock": current_stock
        }
        
        return self.create_notification(
            title=title,
            message=message,
            recipient_id=recipient_id,
            priority='high',
            notification_type='inventory',
            metadata=metadata
        )
    
    def get_notifications(self, recipient_id=None, notification_type=None, is_read=None, limit=50):
        """Get notifications with filters"""
        query = {}
        
        if recipient_id:
            query['recipient_id'] = str(recipient_id)
        if notification_type:
            query['notification_type'] = notification_type
        if is_read is not None:
            query['is_read'] = is_read
        
        notifications = list(self.collection.find(query)
                           .sort('created_at', -1)
                           .limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for notification in notifications:
            notification['_id'] = str(notification['_id'])
            notification['id'] = notification['_id']  # Add id field for consistency
        
        return notifications
    
    def get_notification_by_id(self, notification_id):
        """Get a specific notification by ID"""
        try:
            notification = self.collection.find_one({'_id': ObjectId(notification_id)})
            if notification:
                notification['_id'] = str(notification['_id'])
                notification['id'] = notification['_id']
            return notification
        except Exception:
            return None
    
    def mark_as_read(self, notification_id):
        """Mark notification as read"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(notification_id)},
                {
                    '$set': {
                        'is_read': True,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def mark_as_unread(self, notification_id):
        """Mark notification as unread"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(notification_id)},
                {
                    '$set': {
                        'is_read': False,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def get_recent_notifications(self, limit=10, hours=None):
        """Get recent notifications (last X hours or last X notifications)"""
        try:
            query = {}
            
            # If hours specified, filter by time
            if hours:
                from datetime import timedelta
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query['created_at'] = {'$gte': time_threshold}
            
            notifications = list(self.collection.find(query)
                               .sort('created_at', -1)
                               .limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for notification in notifications:
                notification['_id'] = str(notification['_id'])
                notification['id'] = notification['_id']
            
            return notifications
            
        except Exception as e:
            raise Exception(f"Error getting recent notifications: {str(e)}")
    
    def get_all_notifications(self, skip=0, limit=50):
        """Get all notifications with pagination"""
        try:
            # Get total count for pagination
            total_count = self.collection.count_documents({})
            
            # Get notifications with pagination
            notifications = list(self.collection.find({})
                                .sort('created_at', -1)
                                .skip(skip)
                                .limit(limit))
            
            # Convert ObjectId to string for JSON serialization
            for notification in notifications:
                notification['_id'] = str(notification['_id'])
                notification['id'] = notification['_id']
            
            return notifications, total_count
            
        except Exception as e:
            raise Exception(f"Error getting all notifications: {str(e)}")

    def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(notification_id)})
            return result.deleted_count > 0
        except Exception:
            return False
    
    def get_unread_count(self, recipient_id):
        """Get count of unread notifications for a user"""
        return self.collection.count_documents({
            'recipient_id': str(recipient_id),
            'is_read': False
        })
    
    def _get_recipient(self, recipient_id=None, recipient_username=None):
        """Helper method to get recipient User object"""
        if recipient_id:
            try:
                return User.objects.get(id=recipient_id)
            except User.DoesNotExist:
                return None
        elif recipient_username:
            try:
                return User.objects.get(username=recipient_username)
            except User.DoesNotExist:
                return None
        return None

# Singleton instance
notification_service = NotificationService()