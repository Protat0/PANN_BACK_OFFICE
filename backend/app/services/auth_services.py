from datetime import datetime, timedelta
from jose import JWTError, jwt
from bson import ObjectId
import bcrypt
from ..database import db_manager

# JWT settings
SECRET_KEY = "your-secret-key-here-change-in-production"  #Default is your-secret-key-here-change-in-production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.user_collection = self.db.users
        self.blacklist_collection = self.db.token_blacklist
    
    def convert_object_id(self, document):
        """Convert ObjectId to string for JSON serialization"""
        if document and '_id' in document:
            document['_id'] = str(document['_id'])
        return document
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except:
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
        """Authenticate user and return tokens - ADMIN ONLY"""
        try:
            # Find user by email
            user = self.user_collection.find_one({"email": email})
            if not user:
                raise Exception("Invalid email or password")
            
            # Verify password
            if not self.verify_password(password, user["password"]):
                raise Exception("Invalid email or password")
            
            # Check if user is active (default to active if status is missing)
            user_status = user.get("status", "active")
            if user_status != "active":
                raise Exception("Account is not active")
            
            # ADMIN-ONLY CHECK: Verify user has admin role
            user_role = user.get("role", "").lower()
            if user_role != "admin":
                # Log unauthorized access attempt
                print(f"Non-admin login attempt blocked: {email} (role: {user_role})")
                raise Exception("Access denied. This system is restricted to administrators only.")
            
            # Update last login 
            self.user_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Create tokens
            token_data = {"sub": str(user["_id"]), "email": user["email"], "role": user["role"]}
            access_token = self.create_access_token(token_data)
            refresh_token = self.create_refresh_token(token_data)
            
            # Log the admin login session
            try:
                from .session_services import SessionLogService
                session_service = SessionLogService()
                session_user = {
                    "user_id": str(user["_id"]),
                    "username": user.get("username", user["email"]),
                    "email": user["email"],
                    "branch_id": 1,  # Default branch
                    "role": "admin"  # Explicitly mark as admin session
                }
                session_service.log_login(session_user)
                print(f"Admin login successful: {user['email']}")
            except Exception as session_error:
                print(f"Session logging error: {session_error}")
                # Don't fail login if session logging fails
            
            # Prepare user info for response
            user_info = self.convert_object_id(user.copy())
            user_info.pop("password", None)  # Remove password from response
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": str(user["_id"]),
                    "email": user["email"],
                    "role": user["role"],
                    "name": user.get("full_name", ""),
                    "username": user.get("username", ""),
                    "status": user.get("status", "active")
                }
            }
            
        except Exception as e:
            # Log failed login attempts for security monitoring
            print(f"Login failed for {email}: {str(e)}")
            raise e
    
    def logout(self, token: str):
        print(f"Logout attempt with token: {token[:20]}...")
        
        try:
            clean_token = token.replace("Bearer ", "").strip()
            
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
            
            user_id = payload["sub"]
            user = self.user_collection.find_one({"_id": ObjectId(user_id)})
            if user:
                user_info = self.convert_object_id(user.copy())
                user_info.pop("password", None)  # Remove password
                return {
                    "user_id": str(user["_id"]),
                    "email": user["email"],
                    "role": user["role"],
                    "user_data": user_info
                }
            return None
        
        except Exception as e:
            raise Exception(f"Error getting current user: {str(e)}")