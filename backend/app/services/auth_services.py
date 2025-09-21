from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from ..database import db_manager

# JWT settings
SECRET_KEY = "your-secret-key-here-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class AuthService:
    def __init__(self):
        self.db = db_manager.get_database()
        self.user_collection = self.db.users
        self.blacklist_collection = self.db.token_blacklist
    
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
        try:
            # Find user by email
            user = self.user_collection.find_one({"email": email})
            if not user:
                raise Exception("Invalid email or password")
            
            # Password verification
            if not self.verify_password(password, user["password"]):
                raise Exception("Invalid email or password")
            
            # Status and role checks
            user_status = user.get("status", "active")
            if user_status != "active":
                raise Exception("Account is not active")
            
            user_role = user.get("role", "").lower()
            if user_role != "admin":
                raise Exception("Access denied. This system is restricted to administrators only.")
            
            # ✅ Use _id instead of user_id
            user_id = user["_id"]  # This is your USER-0001 format
            
            # Update last login using _id
            self.user_collection.update_one(
                {"_id": user_id},  # Use _id for lookup
                {"$set": {"last_login": datetime.utcnow()}}
            )
            
            # Create tokens with USER-#### format
            token_data = {"sub": user_id, "email": user["email"], "role": user["role"]}
            access_token = self.create_access_token(token_data)
            refresh_token = self.create_refresh_token(token_data)
            
            # Session logging with USER-#### format
            try:
                from .session_services import SessionLogService
                session_service = SessionLogService()
                session_user = {
                    "user_id": user_id,  # Pass the USER-#### ID
                    "username": user.get("username", user["email"]),
                    "email": user["email"],
                    "branch_id": 1,
                    "role": "admin"
                }
                session_service.log_login(session_user)
            except Exception as session_error:
                print(f"Session logging error: {session_error}")
            
            # Response with USER-#### format
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                "user": {
                    "id": user_id,  # USER-#### format
                    "email": user["email"],
                    "role": user["role"],
                    "name": user.get("full_name", ""),
                    "username": user.get("username", ""),
                    "status": user.get("status", "active")
                }
            }
            
        except Exception as e:
            print(f"Login failed for {email}: {str(e)}")
            raise e
    
    def logout(self, token: str):
        try:
            clean_token = token.replace("Bearer ", "").strip()
            
            # Get user info and log session logout
            try:
                current_user = self.get_current_user(clean_token)
                if current_user and current_user.get('user_id'):
                    user_id = current_user.get('user_id')
                    
                    # Log session logout
                    try:
                        from .session_services import SessionLogService
                        session_service = SessionLogService()
                        session_service.log_logout(user_id)
                    except Exception as session_error:
                        print(f"Session logout failed: {session_error}")
                        
            except Exception as user_error:
                print(f"Could not get current user: {user_error}")
            
            # Blacklist token
            self.blacklist_collection.insert_one({
                "token": clean_token,
                "blacklisted_at": datetime.utcnow()
            })
            
            return {"message": "Successfully logged out"}
        except Exception as e:
            raise e
    
    def get_current_user(self, token: str):
        """Get current user from token"""
        try:
            payload = self.verify_token(token)
            if not payload or payload.get("type") != "access":
                return None
            
            user_id = payload["sub"]  # USER-#### format
            
            # Look up by _id field instead of user_id
            user = self.user_collection.find_one({"_id": user_id})
            
            if user:
                return {
                    "user_id": user["_id"],  # USER-#### format
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
            user = self.user_collection.find_one({"_id": user_id})  # Use _id
            
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