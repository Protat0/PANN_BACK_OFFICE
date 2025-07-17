from datetime import datetime
from bson import ObjectId
from ..database import db_manager

class SessionLogService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.session_logs
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def log_login(self, user_data):
        """Log user login session - FIXED VERSION"""
        try:
            print(f"🔍 SessionLogService.log_login() called with user_data: {user_data}")
            print(f"🔍 user_data type: {type(user_data)}")
            print(f"🔍 user_data keys: {list(user_data.keys()) if isinstance(user_data, dict) else 'Not a dict'}")
            
            # ✅ FIXED: More robust user_id handling
            user_id = user_data.get("user_id")
            
            # Handle different user_id formats
            if user_id is not None:
                if isinstance(user_id, str) and user_id.strip():
                    try:
                        # Try to convert string to ObjectId if it's a valid ObjectId string
                        if len(user_id) == 24:  # Standard ObjectId length
                            user_id = ObjectId(user_id)
                        else:
                            # Keep as string if it's not ObjectId format
                            pass
                    except Exception as e:
                        print(f"⚠️ Could not convert user_id to ObjectId: {e}")
                        # Keep as original value
                elif isinstance(user_id, ObjectId):
                    # Already an ObjectId, keep as is
                    pass
                else:
                    print(f"⚠️ Unexpected user_id type: {type(user_id)}, value: {user_id}")
            else:
                print(f"❌ user_id is None or missing from user_data")
            
            # ✅ FIXED: Get username with fallback chain
            username = (
                user_data.get("username") or 
                user_data.get("email") or 
                user_data.get("name") or 
                "unknown"
            )
            
            print(f"🔍 Extracted values:")
            print(f"  - user_id: {user_id} (type: {type(user_id)})")
            print(f"  - username: {username}")
            print(f"  - branch_id: {user_data.get('branch_id', 1)}")
            
            log_data = {
                "user_id": user_id,  # Keep original format/type
                "branch_id": user_data.get("branch_id", 1),
                "username": username,
                "login_time": datetime.utcnow(),
                "logout_time": None,
                "session_duration": None,
                "status": "active",
                "source": "auth_service",
                "last_updated": datetime.utcnow()
            }
            
            print(f"🔍 Final log_data: {log_data}")
            
            result = self.collection.insert_one(log_data)
            print(f"✅ Session log inserted with ID: {result.inserted_id}")
            
            return self.convert_object_id(log_data)
        
        except Exception as e:
            print(f"❌ Error logging session: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Error logging session: {str(e)}")
    
    def log_logout(self, user_id):
        """Log user logout and calculate session duration - ENHANCED DEBUG VERSION"""
        try:
            print(f"\n🔍 ===== LOGOUT DEBUG START =====")
            print(f"🔍 log_logout() called with user_id: {user_id}")
            print(f"🔍 user_id type: {type(user_id)}")
            print(f"🔍 user_id length: {len(str(user_id))}")
            
            # Convert user_id to ObjectId format to match what's stored
            search_user_id = None
            
            if isinstance(user_id, str):
                if len(user_id) == 24:  # Standard ObjectId string length
                    try:
                        search_user_id = ObjectId(user_id)
                        print(f"🔍 Converted string to ObjectId: {search_user_id}")
                    except Exception as e:
                        print(f"❌ Failed to convert string to ObjectId: {e}")
                        search_user_id = user_id
                else:
                    search_user_id = user_id
                    print(f"🔍 Using string user_id (not ObjectId format): {search_user_id}")
            elif isinstance(user_id, ObjectId):
                search_user_id = user_id
                print(f"🔍 user_id is already ObjectId: {search_user_id}")
            else:
                search_user_id = user_id
                print(f"🔍 Unknown user_id type, using as-is: {search_user_id}")
            
            # Debug: Show what we're searching for
            print(f"🔍 Searching for session with user_id: {search_user_id} (type: {type(search_user_id)})")
            
            # Check all active sessions first (for debugging)
            all_active_sessions = list(self.collection.find({"logout_time": None}))
            print(f"🔍 Total active sessions in database: {len(all_active_sessions)}")
            
            for i, session in enumerate(all_active_sessions[:3]):  # Show first 3 for debugging
                print(f"🔍 Active session {i+1}:")
                print(f"    user_id: {session.get('user_id')} (type: {type(session.get('user_id'))})")
                print(f"    username: {session.get('username')}")
                print(f"    login_time: {session.get('login_time')}")
            
            # Find the latest active session for this user
            latest_session = self.collection.find_one(
                {"user_id": search_user_id, "logout_time": None},
                sort=[("login_time", -1)]
            )
            
            print(f"🔍 Found matching session: {latest_session is not None}")
            
            if latest_session:
                print(f"✅ Found session to update:")
                print(f"    _id: {latest_session['_id']}")
                print(f"    user_id: {latest_session['user_id']}")
                print(f"    username: {latest_session['username']}")
                print(f"    login_time: {latest_session['login_time']}")
                
                logout_time = datetime.utcnow()
                duration = (logout_time - latest_session["login_time"]).total_seconds()
                
                print(f"🔍 Calculating session duration:")
                print(f"    logout_time: {logout_time}")
                print(f"    login_time: {latest_session['login_time']}")
                print(f"    duration: {duration} seconds")
                
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
                
                print(f"✅ Update result:")
                print(f"    matched_count: {update_result.matched_count}")
                print(f"    modified_count: {update_result.modified_count}")
                
                if update_result.modified_count > 0:
                    print(f"✅ Session logout logged successfully!")
                    
                    # Verify the update worked
                    updated_session = self.collection.find_one({"_id": latest_session["_id"]})
                    print(f"🔍 Verification - Updated session:")
                    print(f"    logout_time: {updated_session.get('logout_time')}")
                    print(f"    session_duration: {updated_session.get('session_duration')}")
                    print(f"    status: {updated_session.get('status')}")
                    
                    print(f"🔍 ===== LOGOUT DEBUG END =====\n")
                    return {"message": "Session logged out successfully"}
                else:
                    print(f"❌ Update failed - no documents modified")
                    print(f"🔍 ===== LOGOUT DEBUG END =====\n")
                    return {"message": "Update failed"}
            else:
                print(f"❌ No active session found for user_id: {search_user_id}")
                
                # Additional debugging - try different search methods
                print(f"🔍 Trying alternative search methods...")
                
                # Try searching by username if we have it
                if hasattr(self, 'last_known_username'):
                    username_session = self.collection.find_one(
                        {"username": self.last_known_username, "logout_time": None},
                        sort=[("login_time", -1)]
                    )
                    print(f"🔍 Search by username '{self.last_known_username}': {username_session is not None}")
                
                # Try searching with string version of ObjectId
                if isinstance(search_user_id, ObjectId):
                    string_session = self.collection.find_one(
                        {"user_id": str(search_user_id), "logout_time": None},
                        sort=[("login_time", -1)]
                    )
                    print(f"🔍 Search with string version: {string_session is not None}")
                
                # Try searching with ObjectId version if we have string
                elif isinstance(search_user_id, str) and len(search_user_id) == 24:
                    try:
                        objectid_session = self.collection.find_one(
                            {"user_id": ObjectId(search_user_id), "logout_time": None},
                            sort=[("login_time", -1)]
                        )
                        print(f"🔍 Search with ObjectId version: {objectid_session is not None}")
                    except:
                        print(f"🔍 Could not convert to ObjectId for alternative search")
                
                print(f"🔍 ===== LOGOUT DEBUG END =====\n")
                return {"message": "No active session found"}
        
        except Exception as e:
            print(f"❌ Error logging logout: {str(e)}")
            import traceback
            traceback.print_exc()
            print(f"🔍 ===== LOGOUT DEBUG END =====\n")
            raise Exception(f"Error logging logout: {str(e)}")

class SessionDisplay:
    def __init__(self):
        self.db = db_manager.get_database()
        self.collection = self.db.session_logs
    
    def convert_object_id(self, document):
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def get_session_logs(self):
        """Get session logs - WORKING VERSION"""
        try:
            session_logs = list(self.collection.find().sort("login_time", -1))
            
            formatted_logs = []
            for i, log in enumerate(session_logs):
                log = self.convert_object_id(log)
                
                formatted_log = {
                    "log_id": f"SES-{i+1:04d}",
                    "user_id": log.get('username', 'Unknown'),  # Use username for display
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
            print(f"❌ Error getting session logs: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
    
    def get_combined_logs_display(self, limit=100, log_type=None):
        """Get both session and audit logs combined"""
        try:
            session_logs = []
            audit_logs = []
            
            # Get session logs
            session_cursor = self.collection.find().sort("login_time", -1)
            session_logs = list(session_cursor)
            
            # Get audit logs
            try:
                audit_collection = self.db.audit_logs
                audit_cursor = audit_collection.find().sort("timestamp", -1)
                audit_logs = list(audit_cursor)
                print(f"✅ Fetched {len(audit_logs)} audit logs")
            except Exception as e:
                print(f"⚠️ No audit logs available: {e}")
                audit_logs = []
            
            # Format all logs
            formatted_logs = []
            
            # Format session logs
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
                    "remarks": f"Branch {log.get('branch_id', 'N/A')}",
                    "log_source": "session"
                }
                formatted_logs.append(formatted_log)
            
            # Format audit logs
            for i, log in enumerate(audit_logs):
                log = self.convert_object_id(log)
                formatted_log = {
                    "log_id": f"AUD-{i+1:04d}",
                    "user_id": log.get('username', 'Unknown'),
                    "ref_id": log.get('_id', '')[:12],
                    "event_type": log.get('event_type', 'Unknown').replace('_', ' ').title(),
                    "amount_qty": self._format_audit_amount(log),
                    "status": log.get('status', 'Unknown').title(),
                    "timestamp": str(log.get('timestamp', '')),
                    "remarks": self._format_audit_remarks(log),
                    "log_source": "audit"
                }
                formatted_logs.append(formatted_log)
            
            # Sort by timestamp (newest first)
            formatted_logs.sort(key=lambda x: self._parse_timestamp(x['timestamp']), reverse=True)
            
            # Apply filter if specified
            if log_type and log_type != 'all':
                if log_type == 'session':
                    formatted_logs = [log for log in formatted_logs if log['log_source'] == 'session']
                elif log_type == 'audit':
                    formatted_logs = [log for log in formatted_logs if log['log_source'] == 'audit']
            
            return {
                'success': True,
                'data': formatted_logs[:limit],
                'total_count': len(formatted_logs),
                'session_count': len(session_logs),
                'audit_count': len(audit_logs)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': []
            }
        
    def _format_audit_amount(self, log):
        """Helper method for audit log amounts"""
        event_type = log.get('event_type', '')
        if 'delete' in event_type:
            return "1 record"
        elif 'create' in event_type:
            return "1 record"
        elif 'update' in event_type:
            changes = log.get('changes', {}).get('changed_fields', [])
            return f"{len(changes)} fields" if changes else "0 fields"
        return "N/A"

    def _format_audit_remarks(self, log):
        """Helper method for audit log remarks"""
        target_type = log.get('target_type', 'System')
        target_name = log.get('target_name', 'N/A')
        if target_type and target_name and target_name != 'N/A':
            return f"{target_type.title()}: {target_name}"
        return f"Branch {log.get('branch_id', 'N/A')}"

    def _parse_timestamp(self, timestamp_str):
        """Helper to parse timestamp for sorting"""
        try:
            if not timestamp_str or timestamp_str == '':
                return datetime.min
            return datetime.fromisoformat(str(timestamp_str).replace('Z', '+00:00'))
        except:
            try:
                return datetime.strptime(str(timestamp_str), '%Y-%m-%d %H:%M:%S.%f')
            except:
                return datetime.min

