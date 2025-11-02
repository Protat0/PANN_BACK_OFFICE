# notifications/services.py
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.http import JsonResponse
from app.database import db_manager

class NotificationService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.notifications
    
    # ================================================================
    # ID GENERATION METHOD
    # ================================================================
    
    def generate_notification_id(self):
        """
        Generate sequential notification ID in format NOTIF-XXXXXX
        Uses MongoDB aggregation to find the highest existing ID
        """
        try:
            pipeline = [
                {'$match': {'_id': {'$regex': '^NOTIF-'}}},
                {'$project': {
                    'numericPart': {
                        '$toInt': {'$substr': ['$_id', 6, -1]}  # Extract number after "NOTIF-"
                    }
                }},
                {'$sort': {'numericPart': -1}},
                {'$limit': 1}
            ]
            
            result = list(self.collection.aggregate(pipeline))
            
            if result:
                next_number = result[0]['numericPart'] + 1
            else:
                next_number = 1  # First notification
            
            return f"NOTIF-{next_number:06d}"  # Format as NOTIF-000001, NOTIF-000002, etc.
            
        except Exception as e:
            raise Exception(f"Error generating notification ID: {str(e)}")
    
    # ================================================================
    # NOTIFICATION CREATION METHODS
    # ================================================================
    
    def create_notification(self, title, message, recipient_id=None, recipient_username=None, 
                          priority='medium', notification_type='system', metadata=None):
        """Create a new notification"""
        try:
            notification_id = self.generate_notification_id()
            
            notification_doc = {
                "_id": notification_id,
                "title": title,
                "message": message,
                "priority": priority,
                "is_read": False,
                "archived": False,
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
            
            self.collection.insert_one(notification_doc)
            
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
    
    # ================================================================
    # NOTIFICATION RETRIEVAL METHODS
    # ================================================================
    
    def get_notifications(self, recipient_id=None, notification_type=None, is_read=None, limit=50, include_archived=False):
        """Get notifications with filters"""
        query = {}
        
        # Exclude archived notifications by default
        if not include_archived:
            query['archived'] = {'$ne': True}
        
        if recipient_id:
            query['recipient_id'] = str(recipient_id)
        if notification_type:
            query['notification_type'] = notification_type
        if is_read is not None:
            query['is_read'] = is_read
        
        notifications = list(self.collection.find(query)
                        .sort('created_at', -1)
                        .limit(limit))
        
        return self._format_notifications(notifications)
    
    def get_notification_by_id(self, notification_id):
        """Get a specific notification by ID"""
        try:
            notification = self.collection.find_one({'_id': notification_id})
            if notification:
                notification = self._format_notification(notification)
            return notification
        except Exception:
            return None
    
    def get_recent_notifications(self, limit=10, hours=None, include_archived=False):
        """Get recent notifications (last X hours or last X notifications)"""
        try:
            query = {}
            
            # Exclude archived notifications by default
            if not include_archived:
                query['archived'] = {'$ne': True}
            
            # If hours specified, filter by time
            if hours:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query['created_at'] = {'$gte': time_threshold}
            
            notifications = list(self.collection.find(query)
                            .sort('created_at', -1)
                            .limit(limit))
            
            return self._format_notifications(notifications)
            
        except Exception as e:
            raise Exception(f"Error getting recent notifications: {str(e)}")
    
    def get_all_notifications(self, skip=0, limit=50, include_archived=False):
        """Get all notifications with pagination"""
        try:
            query = {}
            
            # Exclude archived notifications by default
            if not include_archived:
                query['archived'] = {'$ne': True}
            
            # Get total count for pagination
            total_count = self.collection.count_documents(query)
            
            # Get notifications with pagination
            notifications = list(self.collection.find(query)
                                .sort('created_at', -1)
                                .skip(skip)
                                .limit(limit))
            
            formatted_notifications = self._format_notifications(notifications)
            
            return formatted_notifications, total_count
            
        except Exception as e:
            raise Exception(f"Error getting all notifications: {str(e)}")

    def get_all_notifications_api(self, request):
        """API endpoint method for getting all notifications"""
        try:
            # Get query parameters
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 50))
            include_archived = request.GET.get('include_archived', 'false').lower() == 'true'
            
            # Calculate skip for pagination
            skip = (page - 1) * limit
            
            # Get notifications from service
            notifications, total_count = self.get_all_notifications(
                skip=skip,
                limit=limit,
                include_archived=include_archived
            )
            
            # Calculate pagination info
            total_pages = (total_count + limit - 1) // limit
            has_next = page < total_pages
            has_previous = page > 1
            
            return JsonResponse({
                'success': True,
                'data': notifications,
                'pagination': {
                    'current_page': page,
                    'total_pages': total_pages,
                    'total_count': total_count,
                    'per_page': limit,
                    'has_next': has_next,
                    'has_previous': has_previous
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'data': [],
                'pagination': {}
            }, status=500)

    def get_recent_notifications_api(self, request):
        """API endpoint method for getting recent notifications"""
        try:
            limit = int(request.GET.get('limit', 10))
            hours = request.GET.get('hours')
            include_archived = request.GET.get('include_archived', 'false').lower() == 'true'
            
            if hours:
                hours = int(hours)
            
            notifications = self.get_recent_notifications(
                limit=limit,
                hours=hours,
                include_archived=include_archived
            )
            
            return JsonResponse({
                'success': True,
                'data': notifications
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'data': []
            }, status=500)
    
    def get_unread_count(self, recipient_id=None, include_archived=False):
        """Get count of unread notifications for a user or all notifications"""
        query = {'is_read': False}
        
        # Exclude archived notifications by default
        if not include_archived:
            query['archived'] = {'$ne': True}
        
        if recipient_id:
            query['recipient_id'] = str(recipient_id)
        
        return self.collection.count_documents(query)
    
    # ================================================================
    # NOTIFICATION STATUS UPDATE METHODS
    # ================================================================
    
    def mark_as_read(self, notification_id):
        """Mark notification as read"""
        try:
            result = self.collection.update_one(
                {'_id': notification_id},  # String ID now
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

    def mark_as_read_api(self, notification_id):
        """API endpoint method for marking notification as read"""
        try:
            success = self.mark_as_read(notification_id)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Notification marked as read successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to mark notification as read'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def mark_as_unread(self, notification_id):
        """Mark notification as unread"""
        try:
            result = self.collection.update_one(
                {'_id': notification_id},  # String ID now
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
    
    def mark_all_as_read(self, recipient_id=None):
        """
        Mark all notifications as read
        
        Args:
            recipient_id (str, optional): If provided, only mark notifications for this user as read.
                                        If None, mark ALL notifications in the system as read.
        
        Returns:
            int: Number of notifications marked as read
        """
        try:
            query = {'is_read': False, 'archived': {'$ne': True}}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            
            result = self.collection.update_many(
                query,
                {
                    '$set': {
                        'is_read': True,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count
            
        except Exception as e:
            raise Exception(f"Error marking notifications as read: {str(e)}")

    def mark_all_as_read_api(self, request):
        """API endpoint method for marking all notifications as read"""
        try:
            recipient_id = request.GET.get('recipient_id')
            count = self.mark_all_as_read(recipient_id)
            
            return JsonResponse({
                'success': True,
                'message': f'{count} notifications marked as read',
                'count': count
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def mark_all_as_unread(self, recipient_id=None):
        """
        Mark all notifications as unread
        
        Args:
            recipient_id (str, optional): If provided, only mark notifications for this user as unread.
                                        If None, mark ALL notifications in the system as unread.
        
        Returns:
            int: Number of notifications marked as unread
        """
        try:
            query = {'is_read': True, 'archived': {'$ne': True}}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            
            result = self.collection.update_many(
                query,
                {
                    '$set': {
                        'is_read': False,
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count
            
        except Exception as e:
            raise Exception(f"Error marking notifications as unread: {str(e)}")
    
    # ================================================================
    # NOTIFICATION ARCHIVING METHODS
    # ================================================================
    
    def archive_notification(self, notification_id):
        """
        Archive a notification (mark as archived, don't delete)
        
        Args:
            notification_id (str): ID of the notification to archive
        
        Returns:
            bool: True if notification was archived successfully
        """
        try:
            result = self.collection.update_one(
                {'_id': notification_id},  # String ID now
                {
                    '$set': {
                        'archived': True,
                        'archived_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error archiving notification: {str(e)}")

    def archive_notification_api(self, notification_id):
        """API endpoint method for archiving notification"""
        try:
            success = self.archive_notification(notification_id)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Notification archived successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to archive notification'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def unarchive_notification(self, notification_id):
        """
        Unarchive a notification
        
        Args:
            notification_id (str): ID of the notification to unarchive
        
        Returns:
            bool: True if notification was unarchived successfully
        """
        try:
            result = self.collection.update_one(
                {'_id': notification_id},  # String ID now
                {
                    '$set': {
                        'archived': False,
                        'updated_at': datetime.utcnow()
                    },
                    '$unset': {
                        'archived_at': ""
                    }
                }
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error unarchiving notification: {str(e)}")

    def unarchive_notification_api(self, notification_id):
        """API endpoint method for unarchiving notification"""
        try:
            success = self.unarchive_notification(notification_id)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Notification unarchived successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to unarchive notification'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def archive_all_read_notifications(self, recipient_id=None):
        """
        Archive all read notifications
        
        Args:
            recipient_id (str, optional): Only archive read notifications for this user
        
        Returns:
            int: Number of notifications archived
        """
        try:
            query = {'is_read': True, 'archived': {'$ne': True}}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            
            result = self.collection.update_many(
                query,
                {
                    '$set': {
                        'archived': True,
                        'archived_at': datetime.utcnow(),
                        'updated_at': datetime.utcnow()
                    }
                }
            )
            
            return result.modified_count
            
        except Exception as e:
            raise Exception(f"Error archiving read notifications: {str(e)}")
    
    def get_archived_notifications(self, recipient_id=None, skip=0, limit=50):
        """
        Get archived notifications with pagination
        
        Args:
            recipient_id (str, optional): Only get archived notifications for this user
            skip (int): Number of notifications to skip for pagination
            limit (int): Maximum number of notifications to return
        
        Returns:
            tuple: (notifications_list, total_count)
        """
        try:
            query = {'archived': True}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            
            # Get total count for pagination
            total_count = self.collection.count_documents(query)
            
            # Get notifications with pagination
            notifications = list(self.collection.find(query)
                                .sort('archived_at', -1)
                                .skip(skip)
                                .limit(limit))
            
            formatted_notifications = self._format_notifications(notifications)
            
            return formatted_notifications, total_count
            
        except Exception as e:
            raise Exception(f"Error getting archived notifications: {str(e)}")
    
    # ================================================================
    # NOTIFICATION DELETION METHODS
    # ================================================================
    
    def delete_notification(self, notification_id):
        """Delete a notification"""
        try:
            result = self.collection.delete_one({'_id': notification_id})  # String ID now
            return result.deleted_count > 0
        except Exception:
            return False

    def delete_notification_api(self, notification_id):
        """API endpoint method for deleting notification"""
        try:
            success = self.delete_notification(notification_id)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'message': 'Notification deleted successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to delete notification'
                }, status=400)
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    def delete_all_notifications(self, recipient_id=None, notification_type=None):
        """
        Delete all notifications with optional filters
        
        Args:
            recipient_id (str, optional): Only delete notifications for this user
            notification_type (str, optional): Only delete notifications of this type
        
        Returns:
            int: Number of notifications deleted
        """
        try:
            query = {}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            if notification_type:
                query['notification_type'] = notification_type
            
            result = self.collection.delete_many(query)
            return result.deleted_count
            
        except Exception as e:
            raise Exception(f"Error deleting notifications: {str(e)}")
    
    def delete_read_notifications(self, recipient_id=None):
        """
        Delete all read notifications
        
        Args:
            recipient_id (str, optional): Only delete read notifications for this user
        
        Returns:
            int: Number of notifications deleted
        """
        try:
            query = {'is_read': True}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            
            result = self.collection.delete_many(query)
            return result.deleted_count
            
        except Exception as e:
            raise Exception(f"Error deleting read notifications: {str(e)}")
    
    def delete_archived_notifications(self, recipient_id=None):
        """
        Delete all archived notifications permanently
        
        Args:
            recipient_id (str, optional): Only delete archived notifications for this user
        
        Returns:
            int: Number of notifications deleted
        """
        try:
            query = {'archived': True}
            
            if recipient_id:
                query['recipient_id'] = str(recipient_id)
            
            result = self.collection.delete_many(query)
            return result.deleted_count
            
        except Exception as e:
            raise Exception(f"Error deleting archived notifications: {str(e)}")
    
    # ================================================================
    # UTILITY METHODS
    # ================================================================
    
    def _format_notification(self, notification):
        """Format a single notification for JSON serialization"""
        if notification:
            # _id is already a string, no conversion needed
            notification['id'] = notification['_id']  # Add id field for consistency
        return notification
    
    def _format_notifications(self, notifications):
        """Format multiple notifications for JSON serialization"""
        for notification in notifications:
            self._format_notification(notification)
        return notifications

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
    
    # ================================================================
    # ANALYTICS METHODS
    # ================================================================
    
    def get_notification_stats(self, recipient_id=None, include_archived=False):
        """Get notification statistics"""
        try:
            base_query = {}
            if recipient_id:
                base_query['recipient_id'] = str(recipient_id)
            
            # Include archived in stats if requested
            if not include_archived:
                base_query['archived'] = {'$ne': True}
            
            total = self.collection.count_documents(base_query)
            unread = self.collection.count_documents({**base_query, 'is_read': False})
            read = self.collection.count_documents({**base_query, 'is_read': True})
            
            # Get archived count separately
            archived_query = dict(base_query)
            archived_query['archived'] = True
            archived = self.collection.count_documents(archived_query)
            
            # Get counts by type
            type_pipeline = [
                {'$match': base_query},
                {'$group': {'_id': '$notification_type', 'count': {'$sum': 1}}}
            ]
            type_counts = list(self.collection.aggregate(type_pipeline))
            
            # Get counts by priority
            priority_pipeline = [
                {'$match': base_query},
                {'$group': {'_id': '$priority', 'count': {'$sum': 1}}}
            ]
            priority_counts = list(self.collection.aggregate(priority_pipeline))
            
            return {
                'total': total,
                'read': read,
                'unread': unread,
                'archived': archived,
                'by_type': {item['_id']: item['count'] for item in type_counts},
                'by_priority': {item['_id']: item['count'] for item in priority_counts}
            }
            
        except Exception as e:
            raise Exception(f"Error getting notification stats: {str(e)}")

# Singleton instance
notification_service = NotificationService()