from datetime import datetime
from bson import ObjectId
from ..database import db_manager  # ✅ Updated import

class SessionLogService:
    def __init__(self):
        self.db = db_manager.get_database()  # ✅ Get database connection
        self.collection = self.db.session_logs  # ✅ Use cloud database
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def log_login(self, user_data):
        """Log user login session"""
        try:
           
            
            log_data = {
                "user_id": ObjectId(user_data["user_id"]) if isinstance(user_data["user_id"], str) else user_data["user_id"],
                "branch_id": user_data.get("branch_id", 1),
                "username": user_data.get("username", user_data.get("email", "unknown")),
                "login_time": datetime.utcnow(),
                "logout_time": None,
                "session_duration": None,
                "status": "active",
                "source": "auth_service",
                "last_updated": datetime.utcnow()
            }
            
           
            
            result = self.collection.insert_one(log_data)
           
            
            return self.convert_object_id(log_data)
        
        except Exception as e:
           
            raise Exception(f"Error logging session: {str(e)}")
    
    def log_logout(self, user_id):
        """Log user logout and calculate session duration"""
        try:
            
            
            if isinstance(user_id, str):
                user_id = ObjectId(user_id)
            
            # Find the latest active session for this user
            latest_session = self.collection.find_one(
                {"user_id": user_id, "logout_time": None},
                sort=[("login_time", -1)]
            )
            
         
            
            if latest_session:
                logout_time = datetime.utcnow()
                duration = (logout_time - latest_session["login_time"]).total_seconds()
                
                # Update the session with logout info
                update_result = self.collection.update_one(
                    {"_id": latest_session["_id"]},
                    {
                        "$set": {
                            "logout_time": logout_time,
                            "session_duration": int(duration),
                            "status": "completed",
                            "last_updated": logout_time
                        }
                    }
                )
                
              
                
                return {"message": "Session logged out successfully"}
            
           
            return {"message": "No active session found"}
        
        except Exception as e:
           
            raise Exception(f"Error logging logout: {str(e)}")
        
class SessionDisplay:
    def __init__(self):
        self.db = db_manager.get_database()  # ✅ Get database connection
        self.collection = self.db.session_logs  # ✅ Use cloud database
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def get_session_logs(self):
        """Simplified version with minimal processing"""
        try:
            session_logs = list(self.collection.find().sort("login_time", -1))
            
            formatted_logs = []
            for i, log in enumerate(session_logs):
                log = self.convert_object_id(log)
                
                formatted_log = {
                    "log_id": f"SES-{i+1:04d}",
                    "user_id": log.get('username', 'Unknown'),
                    "ref_id": log.get('_id', '')[:12],
                    "event_type": "Session",
                    "amount_qty": f"{log.get('session_duration', 0)}s",
                    "status": log.get('status', 'Unknown').title(),
                    "timestamp": str(log.get('login_time', '')),
                    "remarks": f"Branch {log.get('branch_id', 'N/A')}"
                }
                
                formatted_logs.append(formatted_log)
            
            return {
                'success': True,
                'data': formatted_logs
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
