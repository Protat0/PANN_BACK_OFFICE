from datetime import datetime, timedelta
from bson import ObjectId
from ..database import db_manager
import logging

logger = logging.getLogger(__name__)

class SessionLogService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.session_logs

    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
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
    
    def _normalize_user_id(self, user_id):
        """Normalize user_id to ObjectId format if possible"""
        if not user_id:
            return None
        if isinstance(user_id, ObjectId):
            return user_id
        if isinstance(user_id, str) and len(user_id) == 24:
            try:
                return ObjectId(user_id)
            except Exception:
                return user_id
        return user_id

    def _close_existing_sessions(self, user_id):
        """Close any existing active sessions for a user"""
        try:
            cutoff_time = datetime.utcnow()
            
            # Close sessions older than 24 hours
            self.collection.update_many(
                {
                    "user_id": user_id,
                    "status": "active",
                    "login_time": {"$lt": cutoff_time - timedelta(hours=24)}
                },
                {
                    "$set": {
                        "logout_time": cutoff_time,
                        "status": "expired",
                        "logout_reason": "session_expired"
                    }
                }
            )
            
            # Close recent active sessions (new login replaces old)
            recent_sessions = self.collection.update_many(
                {
                    "user_id": user_id,
                    "status": "active"
                },
                {
                    "$set": {
                        "logout_time": cutoff_time,
                        "status": "replaced",
                        "logout_reason": "new_login"
                    }
                }
            )
            
            if recent_sessions.modified_count > 0:
                logger.info(f"Closed {recent_sessions.modified_count} existing sessions for user")
                
        except Exception as e:
            logger.error(f"Error closing existing sessions: {e}")

    def log_login(self, user_data):
        """Log user login session"""
        try:  
            user_id = self._normalize_user_id(user_data.get("user_id"))
            if not user_id:
                raise ValueError("user_id is required")
            
            username = (
                user_data.get("username") or 
                user_data.get("email") or 
                "unknown"
            )

            # Close any existing active sessions
            self._close_existing_sessions(user_id)

            log_data = {
                "user_id": user_id,
                "branch_id": user_data.get("branch_id", 1),
                "username": username,
                "login_time": datetime.utcnow(),
                "logout_time": None,
                "session_duration": None,
                "status": "active",
                "ip_address": user_data.get("ip_address"),
                "user_agent": user_data.get("user_agent"),
                "source": "auth_service"
            }

            result = self.collection.insert_one(log_data)
            log_data['_id'] = result.inserted_id

            logger.info(f"Login session logged for user {username}")
            return self.convert_object_id(log_data)
        
        except Exception as e:
            logger.error(f"Error logging session: {e}")
            raise Exception(f"Error logging session: {str(e)}")
    
    def log_logout(self, user_id, reason="user_logout"):
        """Log user logout and calculate session duration"""
        try:
            normalized_user_id = self._normalize_user_id(user_id)
            if not normalized_user_id:
                raise ValueError("user_id is required")
            
            # Find most recent active session
            session = self.collection.find_one(
                {"user_id": normalized_user_id, "status": "active"},
                sort=[("login_time", -1)]
            )

            if not session:
                logger.warning(f"No active session found for user_id: {user_id}")
                return {"success": False, "message": "No active session found"}

            logout_time = datetime.utcnow()
            duration = int((logout_time - session["login_time"]).total_seconds())

            # Update session with logout info
            update_result = self.collection.update_one(
                {"_id": session["_id"]},
                {
                    "$set": {
                        "logout_time": logout_time,
                        "session_duration": duration,
                        "status": "completed",
                        "logout_reason": reason
                    }
                }
            )

            if update_result.modified_count > 0:
                logger.info(f"Logout logged for user {session.get('username')} (duration: {duration}s)")
                return {"success": True, "message": "Session logged out successfully", "duration": duration}
            else:
                logger.error("Failed to update session with logout info")
                return {"success": False, "message": "Failed to update session"}
        
        except Exception as e:
            logger.error(f"Error logging logout: {e}")
            raise Exception(f"Error logging logout: {str(e)}")
    
    def get_active_sessions(self):
        """Get all currently active sessions"""
        try:
            sessions = list(self.collection.find(
                {"status": "active"},  # Fixed typo: was "statius"
                sort=[("login_time", -1)]
            ))
            return [self.convert_object_id(session) for session in sessions]
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []

    def get_user_sessions(self, user_id, limit=50):
        """Get session history for a specific user"""
        try:
            normalized_user_id = self._normalize_user_id(user_id)
            sessions = list(self.collection.find(
                {"user_id": normalized_user_id},
                sort=[("login_time", -1)],
                limit=limit
            ))
            return [self.convert_object_id(session) for session in sessions]
        except Exception as e:
            logger.error(f"Error getting user sessions: {e}")
            return []

    def get_session_statistics(self):
        """Get session statistics"""
        try:
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get counts
            active_count = self.collection.count_documents({"status": "active"})
            today_sessions = self.collection.count_documents({
                "login_time": {"$gte": today_start}
            })

            # Calculate average session duration
            recent_sessions = list(self.collection.find(
                {"session_duration": {"$exists": True, "$ne": None}},
                {"session_duration": 1}
            ).sort("login_time", -1).limit(100))
            
            avg_duration = 0
            if recent_sessions:
                total_duration = sum(s.get("session_duration", 0) for s in recent_sessions)
                avg_duration = total_duration // len(recent_sessions)
            
            return {
                "active_sessions": active_count,
                "today_sessions": today_sessions,
                "avg_session_duration": avg_duration
            }

        except Exception as e:
            logger.error(f"Error getting session statistics: {e}")
            return {
                "active_sessions": 0,
                "today_sessions": 0,
                "avg_session_duration": 0
            } 

    def cleanup_old_sessions(self, days_old=30):
        """Clean up sessions older than specified days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            result = self.collection.delete_many({
                "login_time": {"$lt": cutoff_date},
                "status": {"$in": ["completed", "expired", "replaced"]}
            })
            logger.info(f"Cleaned up {result.deleted_count} old sessions")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Error cleaning up old sessions: {e}")
            return 0


class SessionDisplayService:  # Fixed class name
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.session_logs
        self.audit_collection = self.db.audit_logs
   
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
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
        
        return document

    def get_session_logs(self, limit=100, status_filter=None):
        """Get formatted session logs"""
        try:
            query = {}
            if status_filter:
                query["status"] = status_filter
            
            session_logs = list(self.collection.find(query)
                              .sort("login_time", -1)
                              .limit(limit))
            
            formatted_logs = []
            for i, log in enumerate(session_logs):
                log = self.convert_object_id(log)
                
                # Format duration
                duration = log.get('session_duration', 0)
                if duration:
                    if duration < 60:
                        duration_str = f"{duration}s"
                    elif duration < 3600:
                        duration_str = f"{duration // 60}m {duration % 60}s"
                    else:
                        hours = duration // 3600
                        minutes = (duration % 3600) // 60
                        duration_str = f"{hours}h {minutes}m"
                else:
                    duration_str = "Active" if log.get('status') == 'active' else "0s"
            
                formatted_log = {
                    "log_id": f"SES-{i+1:04d}",
                    "username": log.get('username', 'Unknown'),
                    "ref_id": log.get('_id', '')[:12] if log.get('_id') else '',
                    "event_type": "Session",
                    "duration": duration_str,
                    "status": log.get('status', 'Unknown').title(),
                    "login_time": log.get('login_time'),
                    "logout_time": log.get('logout_time'),
                    "branch_id": log.get('branch_id', 'N/A'),
                    "ip_address": log.get('ip_address'),
                    "logout_reason": log.get('logout_reason')
                }
                formatted_logs.append(formatted_log)
            
            return {
                'success': True,
                'data': formatted_logs,
                'count': len(formatted_logs)
            }
            
        except Exception as e:
            logger.error(f"Error getting session logs: {e}")  # Fixed: use logger instead of print
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def get_combined_logs(self, limit=100, log_type=None):
        """Get combined session and audit logs"""
        try:
            all_logs = []
            
            # Get session logs if requested
            if log_type in [None, 'all', 'session']:
                session_limit = limit//2 if log_type == 'all' else limit
                session_result = self.get_session_logs(session_limit)
                if session_result['success']:
                    for log in session_result['data']:
                        log['log_source'] = 'session'
                        log['timestamp'] = log['login_time']
                        all_logs.append(log)
            
            # Get audit logs if requested
            if log_type in [None, 'all', 'audit']:
                try:
                    audit_limit = limit//2 if log_type == 'all' else limit
                    audit_logs = list(self.audit_collection.find()
                                    .sort("timestamp", -1)
                                    .limit(audit_limit))
                    
                    for i, audit in enumerate(audit_logs):
                        audit = self.convert_object_id(audit)
                        formatted_audit = {
                            "log_id": f"AUD-{i+1:04d}",
                            "username": audit.get('username', 'Unknown'),
                            "ref_id": audit.get('_id', '')[:12] if audit.get('_id') else '',
                            "event_type": audit.get('event_type', 'Unknown').replace('_', ' ').title(),
                            "duration": self._format_audit_changes(audit),
                            "status": audit.get('status', 'Unknown').title(),
                            "timestamp": audit.get('timestamp'),
                            "branch_id": audit.get('branch_id', 'N/A'),
                            "target_type": audit.get('target_type'),
                            "log_source": "audit"
                        }
                        all_logs.append(formatted_audit)
                        
                except Exception as e:
                    logger.warning(f"Could not fetch audit logs: {e}")
            
            # Sort all logs by timestamp (newest first)
            all_logs.sort(key=lambda x: x.get('timestamp') or datetime.min, reverse=True)
            
            return {
                'success': True,
                'data': all_logs[:limit],
                'total_count': len(all_logs)
            }
            
        except Exception as e:
            logger.error(f"Error getting combined logs: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def _format_audit_changes(self, audit_log):
        """Format audit log changes for display"""
        event_type = audit_log.get('event_type', '')
        
        if 'create' in event_type:
            return "Created"
        elif 'delete' in event_type:
            return "Deleted"
        elif 'update' in event_type:
            changes = audit_log.get('changes', {})
            if isinstance(changes, dict):
                changed_fields = changes.get('changed_fields', [])
                return f"{len(changed_fields)} fields" if changed_fields else "Updated"
        
        return "N/A"