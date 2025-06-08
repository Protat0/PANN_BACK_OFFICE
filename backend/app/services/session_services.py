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