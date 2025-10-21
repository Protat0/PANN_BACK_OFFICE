from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from ..services.customer_service import CustomerService
from ..services.auth_services import AuthService
from datetime import datetime, timedelta
from jose import jwt
import logging

logger = logging.getLogger(__name__)

# Use the same settings as the existing auth service
SECRET_KEY = "your-secret-key-here-change-in-production"  # Same as AuthService
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class CustomerAuthService:
    """Customer authentication service for frontend customer access"""
    
    def __init__(self):
        self.customer_service = CustomerService()
        self.db = self.customer_service.db
        self.customer_collection = self.customer_service.customer_collection
    
    def authenticate_customer(self, email, password):
        """Authenticate customer with email and password"""
        try:
            if not email or not password:
                return None
            
            customer = self.customer_collection.find_one({
                'email': email.strip().lower(),
                'isDeleted': {'$ne': True},
                'status': 'active'
            })
            
            if not customer:
                return None
            
            # Use the existing customer service password verification
            if self.customer_service.verify_password(password, customer['password']):
                # Update last login timestamp
                self.customer_collection.update_one(
                    {'_id': customer['_id']},
                    {'$set': {'last_updated': datetime.utcnow()}}
                )
                return customer
            
            return None
            
        except Exception as e:
            logger.error(f"Error authenticating customer: {str(e)}")
            raise Exception(f"Error authenticating customer: {str(e)}")
    
    def create_customer(self, customer_data):
        """Create new customer account"""
        try:
            # Use the existing customer service to create customer
            return self.customer_service.create_customer(customer_data)
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise e
    
    def get_customer_by_id(self, customer_id):
        """Get customer by ID"""
        try:
            return self.customer_service.get_customer_by_id(customer_id)
        except Exception as e:
            logger.error(f"Error getting customer: {str(e)}")
            return None
    
    def change_customer_password(self, customer_id, old_password, new_password):
        """Change customer password"""
        try:
            customer = self.get_customer_by_id(customer_id)
            if not customer:
                return False
            
            if not self.customer_service.verify_password(old_password, customer['password']):
                return False
            
            # Hash new password
            hashed_password = self.customer_service.hash_password(new_password)
            
            # Update password
            result = self.customer_collection.update_one(
                {'_id': customer['_id']},
                {'$set': {'password': hashed_password, 'last_updated': datetime.utcnow()}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error changing password: {str(e)}")
            return False
    
    def update_customer_profile(self, customer_id, profile_data):
        """Update customer profile"""
        try:
            return self.customer_service.update_customer_profile(customer_id, profile_data)
        except Exception as e:
            logger.error(f"Error updating profile: {str(e)}")
            return None

def generate_jwt_token(customer):
    """Generate JWT token for customer using same settings as AuthService"""
    payload = {
        'customer_id': str(customer['_id']),
        'username': customer.get('username', ''),
        'email': customer.get('email', ''),
        'sub': str(customer['_id']),  # Subject - same as AuthService uses
        'exp': datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        'iat': datetime.utcnow(),
        'type': 'customer'  # Distinguish from admin tokens
    }
    
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_jwt_token(token):
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception:
        return None

def jwt_required(f):
    """Decorator to protect routes that require customer authentication"""
    def decorated_function(request, *args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        auth_header = request.headers.get('Authorization')
        logger.info(f"JWT Auth - Authorization header: {auth_header}")
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            logger.info(f"JWT Auth - Token extracted (length: {len(token)})")
        else:
            logger.warning(f"JWT Auth - No valid Bearer token found in header: {auth_header}")
        
        if not token:
            logger.error("JWT Auth - No token provided")
            return Response(
                {'error': 'Authentication token is missing'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Decode token
        payload = decode_jwt_token(token)
        logger.info(f"JWT Auth - Token payload: {payload}")
        
        if not payload or payload.get('type') != 'customer':
            logger.error(f"JWT Auth - Invalid token or wrong type. Payload: {payload}")
            return Response(
                {'error': 'Invalid or expired token'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Add customer info to request
        request.customer = payload
        logger.info(f"JWT Auth - Successfully authenticated customer: {payload.get('customer_id', 'unknown')}")
        
        return f(request, *args, **kwargs)
    
    return decorated_function

def sanitize_customer_data(customer):
    """Remove sensitive data from customer object before sending to frontend"""
    if not customer:
        return None
    
    # Create a copy to avoid modifying original
    if isinstance(customer, dict):
        customer_data = customer.copy()
    else:
        # Handle MongoDB cursor objects or other types
        customer_data = dict(customer) if hasattr(customer, '__iter__') and not isinstance(customer, str) else {}
    
    # Remove password field
    customer_data.pop('password', None)
    
    # Convert ObjectId to string and add customer_id field for frontend compatibility
    if '_id' in customer_data:
        customer_data['customer_id'] = str(customer_data['_id'])
        customer_data['_id'] = str(customer_data['_id'])
    
    # Ensure required fields exist with defaults
    customer_data.setdefault('loyalty_points', 0)
    customer_data.setdefault('email', '')
    customer_data.setdefault('full_name', customer_data.get('name', ''))
    
    return customer_data

# Initialize customer auth service
customer_auth_service = CustomerAuthService()

@csrf_exempt
@api_view(['POST'])
def customer_login(request):
    """Customer login endpoint - matches ramyeonsite backend API"""
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        
        if not email or not password:
            return Response(
                {'error': 'Email and password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer = customer_auth_service.authenticate_customer(email, password)
        
        if not customer:
            return Response(
                {'error': 'Invalid email or password'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        token = generate_jwt_token(customer)
        customer_data = sanitize_customer_data(customer)
        
        return Response({
            'token': token,
            'customer': customer_data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'An error occurred during login'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
def customer_register(request):
    """Customer registration endpoint - matches ramyeonsite backend API"""
    try:
        customer_data = {
            'email': request.data.get('email'),
            'password': request.data.get('password'),
            'username': request.data.get('username'),
            'full_name': request.data.get('full_name'),
            'phone': request.data.get('phone', ''),
            'delivery_address': request.data.get('delivery_address', {})
        }
        
        customer = customer_auth_service.create_customer(customer_data)
        token = generate_jwt_token(customer)
        customer_data_response = sanitize_customer_data(customer)
        
        return Response({
            'token': token,
            'customer': customer_data_response,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'error': 'An error occurred during registration'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@jwt_required
def customer_me(request):
    """Get current customer info from JWT token - matches ramyeonsite backend API"""
    try:
        # Check if customer data exists in request
        if not hasattr(request, 'customer') or not request.customer:
            logger.error("No customer data in request object")
            return Response(
                {'error': 'Authentication token is invalid'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        customer_id = request.customer.get('customer_id')
        if not customer_id:
            logger.error("No customer_id in JWT token payload")
            return Response(
                {'error': 'Invalid token: missing customer_id'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        logger.info(f"Looking up customer with ID: {customer_id}")
        
        # Get customer from database using ObjectId
        from bson import ObjectId
        
        try:
            # Try to convert to ObjectId first
            object_id = ObjectId(customer_id)
        except Exception as e:
            logger.error(f"Invalid ObjectId format for customer_id {customer_id}: {str(e)}")
            return Response(
                {'error': 'Invalid customer ID format'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        customer = customer_auth_service.customer_collection.find_one({
            '_id': object_id,
            'isDeleted': {'$ne': True}
        })
        
        if not customer:
            logger.error(f"Customer not found in database for ID: {customer_id}")
            return Response(
                {'error': 'Customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        logger.info(f"Found customer: {customer.get('email', 'no email')}")
        
        customer_data = sanitize_customer_data(customer)
        
        if not customer_data:
            logger.error("Failed to sanitize customer data")
            return Response(
                {'error': 'Failed to process customer data'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        return Response({
            'customer': customer_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Get customer error: {str(e)}", exc_info=True)
        return Response(
            {'error': 'An error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['POST'])
@jwt_required
def customer_change_password(request):
    """Change customer password - matches ramyeonsite backend API"""
    try:
        customer_id = request.customer['customer_id']
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'error': 'Old password and new password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        success = customer_auth_service.change_customer_password(
            customer_id, old_password, new_password
        )
        
        if success:
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to change password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Change password error: {str(e)}")
        return Response(
            {'error': 'An error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@csrf_exempt
@api_view(['PUT', 'PATCH'])
@jwt_required
def customer_update_profile(request):
    """Update customer profile information - matches ramyeonsite backend API"""
    try:
        customer_id = request.customer['customer_id']
        profile_data = {}
        
        # Extract allowed fields from request
        allowed_fields = [
            'full_name', 'email', 'username', 'phone', 
            'delivery_address', 'profile_picture', 'birthdate', 'preferences'
        ]
        
        for field in allowed_fields:
            if field in request.data:
                profile_data[field] = request.data[field]
        
        updated_customer = customer_auth_service.update_customer_profile(
            customer_id, profile_data
        )
        
        if updated_customer:
            customer_data = sanitize_customer_data(updated_customer)
            return Response({
                'customer': customer_data,
                'message': 'Profile updated successfully'
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Failed to update profile'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
    except ValueError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return Response(
            {'error': 'An error occurred while updating profile'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
