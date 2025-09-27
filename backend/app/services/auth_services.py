from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from ..database import db_manager

# JWT settings
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 696969
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.user_collection = self.db.users
        self.blacklist_collection = self.db.token_blacklist
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        print(f"🔐 Password verification debug:")
        print(f"🔐 Input password length: {len(password) if password else 0}")
        print(f"🔐 Stored hash length: {len(hashed) if hashed else 0}")
        print(f"🔐 Hash starts with: {hashed[:10] if hashed else 'None'}...")
        
        try:
            result = bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
            print(f"🔐 bcrypt.checkpw result: {result}")
            return result
        except Exception as e:
            print(f"❌ Password verification exception: {e}")
            return False
    
    def create_access_token(self, data: dict, expires_delta: timedelta = None):
        """Create JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict):
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str):
        """Verify JWT token"""
        try:
            # Check if token is blacklisted
            if self.blacklist_collection.find_one({"token": token}):
                return None
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return payload
        except JWTError:
            return None
    
    def login(self, email: str, password: str):
        print(f"🚀 AUTH SERVICE LOGIN START")
        print(f"📧 Email: {email}")
        print(f"🔍 Password length: {len(password) if password else 0}")
        
        try:
            # Find user by email
            print(f"🔍 Looking up user by email: {email}")
            user = self.user_collection.find_one({"email": email})
            
            if not user:
                print(f"❌ User not found with email: {email}")
                raise Exception("Invalid email or password")
            else:
                print(f"✅ User found: {user.get('email', 'N/A')}")
                print(f"🆔 User ID: {user.get('_id', 'N/A')}")
                print(f"👤 Username: {user.get('username', 'N/A')}")
                print(f"🎭 Role: {user.get('role', 'N/A')}")
                print(f"📊 Status: {user.get('status', 'N/A')}")
            
            # Password verification
            print(f"🔐 Starting password verification...")
            password_valid = self.verify_password(password, user["password"])
            print(f"🔐 Password verification result: {password_valid}")
            
            if not password_valid:
                print(f"❌ Password verification failed for: {email}")
                raise Exception("Invalid email or password")
            
            # Status check
            user_status = user.get("status", "active")
            print(f"📊 Checking user status: {user_status}")
            if user_status != "active":
                print(f"❌ User status not active: {user_status}")
                raise Exception("Account is not active")
            
            # Role check
            user_role = user.get("role", "").lower()
            print(f"🎭 Checking user role: '{user_role}'")
            if user_role != "admin":
                print(f"❌ Non-admin login attempt blocked: {email} (role: {user_role})")
                raise Exception("Access denied. This system is restricted to administrators only.")
            
            # Convert ObjectId to string
            user_id = str(user["_id"])
            print(f"🆔 Converting ObjectId to string: {user_id}")
            
            # Update last login
            print(f"⏰ Updating last login timestamp...")
            update_result = self.user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            print(f"⏰ Last login update result - matched: {update_result.matched_count}, modified: {update_result.modified_count}")
            
            # Create tokens
            print(f"🎫 Creating JWT tokens...")
            token_data = {"sub": user_id, "email": user["email"], "role": user["role"]}
            print(f"🎫 Token data: {token_data}")
            
            access_token = self.create_access_token(token_data)
            refresh_token = self.create_refresh_token(token_data)
            print(f"🎫 Access token created: {access_token[:50]}...")
            print(f"🎫 Refresh token created: {refresh_token[:50]}...")
            
            # Prepare user data for response
            user_response_data = {
                "id": user_id,
                "email": user["email"],
                "role": user["role"],
                "name": user.get("full_name", ""),
                "username": user.get("username", ""),
                "status": user.get("status", "active")
            }
            print(f"👤 User response data prepared: {user_response_data}")
            
            # Session logging
            print(f"📝 Starting session logging...")
            try:
                from .session_services import SessionLogService
                session_service = SessionLogService()
                session_user = {
                    "user_id": user_id,
                    "username": user.get("username", user["email"]),
                    "email": user["email"],
                    "branch_id": 1,
                    "role": "admin"
                }
                print(f"📝 Session user data: {session_user}")
                session_result = session_service.log_login(session_user)
                print(f"✅ Session logged successfully: {session_result}")
                print(f"✅ Admin login successful: {user['email']}")
            except Exception as session_error:
                print(f"❌ Session logging error: {session_error}")
            
            # Final response
            final_response = {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": user_response_data
            }
            print(f"🎉 LOGIN SUCCESSFUL - Response prepared")
            print(f"🎉 Final response keys: {list(final_response.keys())}")
            return final_response
            
        except Exception as e:
            print(f"💥 LOGIN FAILED for {email}")
            print(f"💥 Error type: {type(e).__name__}")
            print(f"💥 Error message: {str(e)}")
            import traceback
            print(f"💥 Full traceback:")
            traceback.print_exc()
            raise e
    
    def logout(self, token: str):
        print(f"🚀🚀🚀 AUTH SERVICE LOGOUT CALLED! 🚀🚀🚀")
        print(f"Logout attempt with token: {token[:20]}...")
        
        try:
            clean_token = token.replace("Bearer ", "").strip()
            
            # ✅ NEW: Get user info from token BEFORE blacklisting
            try:
                current_user = self.get_current_user(clean_token)
                print(f"🔍 LOGOUT: Got current user: {current_user}")
                
                if current_user and current_user.get('user_id'):
                    user_id = current_user.get('user_id')
                    print(f"🔍 LOGOUT: Extracted user_id: {user_id}")
                    
                    # ✅ NEW: Log session logout
                    try:
                        from .session_services import SessionLogService
                        session_service = SessionLogService()
                        print(f"🔍 LOGOUT: About to call session_service.log_logout({user_id})")
                        session_result = session_service.log_logout(user_id)
                        print(f"✅ LOGOUT: Session logout result: {session_result}")
                    except Exception as session_error:
                        print(f"❌ LOGOUT: Session logout failed: {session_error}")
                        # Continue with token blacklisting even if session logout fails
                else:
                    print(f"⚠️ LOGOUT: Could not extract user_id from token")
                    
            except Exception as user_error:
                print(f"❌ LOGOUT: Could not get current user: {user_error}")
                # Continue with token blacklisting even if we can't get user info
            
            # Check if already blacklisted
            existing = self.blacklist_collection.find_one({"token": clean_token})
            print(f"Token already blacklisted: {existing is not None}")
            
            # Add to blacklist
            result = self.blacklist_collection.insert_one({
                "token": clean_token,
                "blacklisted_at": datetime.utcnow()
            })
            print(f"Blacklist insert result: {result.inserted_id}")
            
            return {"message": "Successfully logged out"}
        except Exception as e:
            print(f"Logout error: {str(e)}")
            raise e
    
    def get_current_user(self, token: str):
        """Get current user from token"""
        try:
            payload = self.verify_token(token)
            if not payload or payload.get("type") != "access":
                return None
            
            user_id = payload["sub"]  # This is the ObjectId string
            
            # Convert back to ObjectId for lookup
            from bson import ObjectId
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            
            if user:
                return {
                    "user_id": str(user["_id"]),
                    "email": user["email"],
                    "role": user["role"],
                    "user_data": user
                }
            return None
        
        except Exception as e:
            raise Exception(f"Error getting current user: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str):
        """Refresh access token using refresh token"""
        try:
            payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
            if payload.get("type") != "refresh":
                raise Exception("Invalid token type")
            
            user_id = payload["sub"]
            user = self.user_collection.find_one({"user_id": user_id})
            
            if not user:
                raise Exception("User not found")
            
            # Create new access token
            token_data = {"sub": user_id, "email": user["email"], "role": user["role"]}
            new_access_token = self.create_access_token(token_data)
            
            return {
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
            }
        except JWTError:
            raise Exception("Invalid refresh token")