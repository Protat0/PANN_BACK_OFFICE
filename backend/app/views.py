from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services.user_service import UserService
from .services.customer_service import CustomerService
from .services.product_service import ProductService  # Add this import
from .services.auth_services import AuthService
from .services.session_services import SessionLogService
from .services.session_management_service import SessionManagementService
# Remove the global service initialization

from .serializers import (
    UserCreateSerializer, 
    UserUpdateSerializer, 
    CustomerCreateSerializer, 
    LoginSerializer
)

class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            "message": "User Management API is running!",
            "status": "active",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)

class UserListView(APIView):
    def get(self, request):
        """Get all users"""
        try:
            user_service = UserService()  # Initialize here instead
            users = user_service.get_all_users()
            return Response(users, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new user with validation"""
        try:
            # Validate input data
            serializer = UserCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {"error": "Validation failed", "details": serializer.errors}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use validated data
            user_service = UserService()
            validated_data = serializer.validated_data
            new_user = user_service.create_user(validated_data)
            return Response(new_user, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class UserDetailView(APIView):
    def get(self, request, user_id):
        """Get user by ID"""
        try:
            user_service = UserService()  # Initialize here instead
            user = user_service.get_user_by_id(user_id)
            if user:
                return Response(user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, user_id):
        """Update user"""
        try:
            user_service = UserService()  # Initialize here instead
            user_data = request.data
            updated_user = user_service.update_user(user_id, user_data)
            if updated_user:
                return Response(updated_user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, user_id):
        """Delete user"""
        try:
            user_service = UserService()  # Initialize here instead
            deleted = user_service.delete_user(user_id)
            if deleted:
                return Response(
                    {"message": "User deleted successfully"}, 
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserByEmailView(APIView):
    def get(self, request, email):
        """Get user by email"""
        try:
            user_service = UserService()  # Initialize here instead
            user = user_service.get_user_by_email(email)
            if user:
                return Response(user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UserByUsernameView(APIView):
    def get(self, request, username):
        """Get user by username"""
        try:
            user_service = UserService()  # Initialize here instead
            user = user_service.get_user_by_username(username)
            if user:
                return Response(user, status=status.HTTP_200_OK)
            return Response(
                {"error": "User not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class CustomerListView(APIView):
    def get(self, request):
        """Get all customers"""
        try:
            customer_service = CustomerService()
            customers = customer_service.get_all_customers()
            return Response(customers, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new customer"""
        try:
            customer_service = CustomerService()
            customer_data = request.data
            new_customer = customer_service.create_customer(customer_data)
            return Response(new_customer, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomerDetailView(APIView):
    def get(self, request, customer_id):
        """Get customer by ID"""
        try:
            customer_service = CustomerService()
            customer = customer_service.get_customer_by_id(customer_id)
            if customer:
                return Response(customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, customer_id):
        """Update customer"""
        try:
            customer_service = CustomerService()
            customer_data = request.data
            updated_customer = customer_service.update_customer(customer_id, customer_data)
            if updated_customer:
                return Response(updated_customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, customer_id):
        """Delete customer"""
        try:
            customer_service = CustomerService()
            deleted = customer_service.delete_customer(customer_id)
            if deleted:
                return Response(
                    {"message": "Customer deleted successfully"}, 
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================ PRODUCT VIEWS ================

class ProductListView(APIView):
    def get(self, request):
        """Get all products with optional filters"""
        try:
            product_service = ProductService()
            
            # Get query parameters for filtering
            filters = {}
            if request.GET.get('category_id'):
                filters['category_id'] = request.GET.get('category_id')
            if request.GET.get('status'):
                filters['status'] = request.GET.get('status')
            if request.GET.get('stock_level'):
                filters['stock_level'] = request.GET.get('stock_level')
            if request.GET.get('search'):
                filters['search'] = request.GET.get('search')
            
            products = product_service.get_all_products(filters if filters else None)
            return Response(products, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new product"""
        try:
            product_service = ProductService()
            product_data = request.data
            new_product = product_service.create_product(product_data)
            return Response({
                'message': 'Product created successfully', 
                'data': new_product
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class ProductDetailView(APIView):
    def get(self, request, product_id):
        """Get product by ID"""
        try:
            product_service = ProductService()
            product = product_service.get_product_by_id(product_id)
            if not product:
                return Response(
                    {"error": "Product not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(product, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, product_id):
        """Update product"""
        try:
            product_service = ProductService()
            product_data = request.data
            updated_product = product_service.update_product(product_id, product_data)
            if not updated_product:
                return Response(
                    {"error": "Product not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response({
                'message': 'Product updated successfully', 
                'data': updated_product
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, product_id):
        """Delete product"""
        try:
            product_service = ProductService()
            deleted = product_service.delete_product(product_id)
            if not deleted:
                return Response(
                    {"error": "Product not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(
                {"message": "Product deleted successfully"}, 
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductBySkuView(APIView):
    def get(self, request, sku):
        """Get product by SKU"""
        try:
            product_service = ProductService()
            product = product_service.get_product_by_sku(sku)
            if not product:
                return Response(
                    {"error": "Product not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            return Response(product, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductStockUpdateView(APIView):
    def put(self, request, product_id):
        """Update product stock with operation types"""
        try:
            product_service = ProductService()
            
            # Get stock data from request body
            stock_data = {
                'operation_type': request.data.get('operation_type', 'set'),
                'quantity': request.data.get('quantity'),
                'reason': request.data.get('reason', 'Manual adjustment')
            }
            
            # Validate required fields
            if stock_data['quantity'] is None:
                return Response(
                    {"error": "Quantity is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate operation type
            valid_operations = ['add', 'remove', 'set']
            if stock_data['operation_type'] not in valid_operations:
                return Response(
                    {"error": f"Invalid operation_type. Must be one of: {valid_operations}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update stock using the enhanced method
            updated_product = product_service.update_stock(product_id, stock_data)
            
            if not updated_product:
                return Response(
                    {"error": "Product not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response({
                'message': 'Stock updated successfully', 
                'data': updated_product
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def post(self, request, product_id):
        """Alternative POST method for stock updates"""
        return self.put(request, product_id)
    


class LowStockProductsView(APIView):
    def get(self, request):
        """Get products with low stock"""
        try:
            product_service = ProductService()
            branch_id = request.GET.get('branch_id')
            products = product_service.get_low_stock_products(branch_id)
            return Response(products, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ExpiringProductsView(APIView):
    def get(self, request):
        """Get products expiring within specified days"""
        try:
            product_service = ProductService()
            days_ahead = int(request.GET.get('days_ahead', 30))
            products = product_service.get_expiring_products(days_ahead)
            return Response(products, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
class BulkStockUpdateView(APIView):
    def post(self, request):
        """Handle bulk stock updates for multiple products"""
        try:
            stock_updates = request.data.get('updates', [])
            
            if not stock_updates:
                return Response(
                    {'error': 'No updates provided'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            product_service = ProductService()
            results = product_service.bulk_update_stock(stock_updates)
            
            return Response({
                'message': 'Bulk stock update completed',
                'results': results
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StockHistoryView(APIView):
    def get(self, request, product_id):
        """Get stock change history for a specific product"""
        try:
            product_service = ProductService()
            
            # Get product with sync logs
            product = product_service.get_product_by_id(product_id)
            
            if not product:
                return Response(
                    {'error': 'Product not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Extract stock-related sync logs
            sync_logs = product.get('sync_logs', [])
            stock_history = [
                log for log in sync_logs 
                if log.get('status', '').startswith('stock_')
            ]
            
            # Sort by most recent first
            stock_history.sort(
                key=lambda x: x.get('last_updated', ''), 
                reverse=True
            )
            
            return Response({
                'product_id': product_id,
                'product_name': product.get('product_name'),
                'current_stock': product.get('stock'),
                'stock_history': stock_history
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    

# ================ EXISTING VIEWS CONTINUE ================

class LoginView(APIView):
    def post(self, request):
        """User login"""
        try:
            auth_service = AuthService()
            email = request.data.get('email')
            password = request.data.get('password')
            
            if not email or not password:
                return Response(
                    {"error": "Email and password are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = auth_service.login(email, password)
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class LogoutView(APIView):
    def post(self, request):
        """User logout"""
        try:
            auth_service = AuthService()
            
            # Get token from Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return Response(
                    {"error": "Missing or invalid authorization header"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            token = authorization.split(" ")[1]
            result = auth_service.logout(token)
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class RefreshTokenView(APIView):
    def post(self, request):
        """Refresh access token"""
        try:
            auth_service = AuthService()
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = auth_service.refresh_access_token(refresh_token)
            return Response(result, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_401_UNAUTHORIZED
            )

class CurrentUserView(APIView):
    def get(self, request):
        """Get current authenticated user"""
        try:
            auth_service = AuthService()
            
            # Get token from Authorization header
            authorization = request.headers.get("Authorization")
            if not authorization or not authorization.startswith("Bearer "):
                return Response(
                    {"error": "Missing or invalid authorization header"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            token = authorization.split(" ")[1]
            user = auth_service.get_current_user(token)
            
            if user:
                return Response(user, status=status.HTTP_200_OK)
            
            return Response(
                {"error": "Invalid token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class VerifyTokenView(APIView):
    def post(self, request):
        """Verify if token is valid"""
        try:
            auth_service = AuthService()
            
            # Get token from Authorization header or request body
            authorization = request.headers.get("Authorization")
            if authorization and authorization.startswith("Bearer "):
                token = authorization.split(" ")[1]
            else:
                token = request.data.get('token')
            
            if not token:
                return Response(
                    {"error": "Token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            payload = auth_service.verify_token(token)
            
            if payload:
                return Response({
                    "valid": True,
                    "user_id": payload.get("sub"),
                    "email": payload.get("email"),
                    "role": payload.get("role")
                }, status=status.HTTP_200_OK)
            
            return Response(
                {"valid": False, "error": "Invalid token"}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class SessionLogsView(APIView):
    def get(self, request):
        """Get all session logs"""
        try:
            session_service = SessionLogService()
            # Get all sessions and convert ObjectIds to strings
            sessions = list(session_service.collection.find())
            for session in sessions:
                if '_id' in session:
                    session['_id'] = str(session['_id'])
                if 'user_id' in session:
                    session['user_id'] = str(session['user_id'])
            
            return Response(sessions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SystemStatusView(APIView):
    def get(self, request):
        """Get system status and counts"""
        try:
            user_service = UserService()
            customer_service = CustomerService()
            product_service = ProductService()  # Add this
            session_service = SessionLogService()
            
            # Get counts
            users = user_service.get_all_users()
            customers = customer_service.get_all_customers()
            products = product_service.get_all_products()  # Add this
            sessions = list(session_service.collection.find())
            
            # Get active sessions
            active_sessions = list(session_service.collection.find({"status": "active"}))
            
            return Response({
                "system": "PANN User Management System",
                "status": "operational",
                "version": "1.0.0",
                "statistics": {
                    "total_users": len(users),
                    "total_customers": len(customers),
                    "total_products": len(products),  # Add this
                    "total_sessions": len(sessions),
                    "active_sessions": len(active_sessions)
                },
                "endpoints": {
                    "health": "/api/v1/health/",
                    "users": "/api/v1/users/",
                    "customers": "/api/v1/customers/",
                    "products": "/api/v1/products/",  # Add this
                    "auth_login": "/api/v1/auth/login/",
                    "auth_logout": "/api/v1/auth/logout/",
                    "session_logs": "/api/v1/session-logs/"
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SessionManagementView(APIView):
    def get(self, request):
        """Get session management options"""
        return Response({
            "endpoints": {
                "active_sessions": "/api/v1/sessions/active/",
                "user_sessions": "/api/v1/sessions/user/{user_id}/",
                "force_logout": "/api/v1/sessions/force-logout/{user_id}/",
                "cleanup": "/api/v1/sessions/cleanup/",
                "statistics": "/api/v1/sessions/statistics/"
            }
        })

class ActiveSessionsView(APIView):
    def get(self, request):
        """Get all active sessions"""
        try:
            session_mgmt = SessionManagementService()
            sessions = session_mgmt.get_active_sessions()
            return Response(sessions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserSessionsView(APIView):
    def get(self, request, user_id):
        """Get sessions for specific user"""
        try:
            session_mgmt = SessionManagementService()
            sessions = session_mgmt.get_user_sessions(user_id)
            return Response(sessions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class SessionStatisticsView(APIView):
    def get(self, request):
        """Get session statistics"""
        try:
            session_mgmt = SessionManagementService()
            stats = session_mgmt.get_session_statistics()
            return Response(stats, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class APIDocumentationView(APIView):
    def get(self, request):
        """Complete API Documentation"""
        return Response({
            "title": "PANN User Management System API",
            "version": "1.0.0",
            "description": "Complete user management system with authentication, session logging, customer management, and product management",
            "base_url": "http://localhost:8000/api/v1/",
            
            "authentication": {
                "type": "JWT Bearer Token",
                "header": "Authorization: Bearer <token>",
                "login_endpoint": "/auth/login/",
                "refresh_endpoint": "/auth/refresh/"
            },
            
            "endpoints": {
                "system": {
                    "GET /": "System status and statistics",
                    "GET /health/": "Health check",
                    "GET /docs/": "This documentation"
                },
                
                "authentication": {
                    "POST /auth/login/": "User login",
                    "POST /auth/logout/": "User logout (requires auth)",
                    "POST /auth/refresh/": "Refresh access token",
                    "GET /auth/me/": "Get current user (requires auth)",
                    "POST /auth/verify-token/": "Verify token validity"
                },
                
                "users": {
                    "GET /users/": "List all users (requires auth)",
                    "POST /users/": "Create new user",
                    "GET /users/{id}/": "Get specific user (requires auth)",
                    "PUT /users/{id}/": "Update user (requires auth)",
                    "DELETE /users/{id}/": "Delete user (requires auth)",
                    "GET /users/email/{email}/": "Get user by email",
                    "GET /users/username/{username}/": "Get user by username"
                },
                
                "customers": {
                    "GET /customers/": "List all customers",
                    "POST /customers/": "Create new customer",
                    "GET /customers/{id}/": "Get specific customer",
                    "PUT /customers/{id}/": "Update customer",
                    "DELETE /customers/{id}/": "Delete customer"
                },
                
                "products": {
                    "GET /products/": "List all products with filters",
                    "POST /products/": "Create new product",
                    "GET /products/{id}/": "Get specific product",
                    "PUT /products/{id}/": "Update product",
                    "DELETE /products/{id}/": "Delete product",
                    "GET /products/sku/{sku}/": "Get product by SKU",
                    "PUT /products/{id}/stock/": "Update product stock",
                    "GET /products/reports/low-stock/": "Get low stock products",
                    "GET /products/reports/expiring/": "Get expiring products"
                },
                
                "sessions": {
                    "GET /sessions/": "Session management info",
                    "GET /sessions/active/": "Get active sessions",
                    "GET /sessions/user/{user_id}/": "Get user sessions",
                    "GET /sessions/statistics/": "Session statistics",
                    "GET /session-logs/": "All session logs"
                }
            },
            
            "example_requests": {
                "login": {
                    "method": "POST",
                    "url": "/auth/login/",
                    "body": {
                        "email": "admin@pannpos.com",
                        "password": "admin123"
                    }
                },
                "create_user": {
                    "method": "POST", 
                    "url": "/users/",
                    "body": {
                        "username": "newuser",
                        "email": "user@example.com",
                        "password": "password123",
                        "full_name": "New User",
                        "role": "customer"
                    }
                },
                "create_customer": {
                    "method": "POST",
                    "url": "/customers/",
                    "body": {
                        "full_name": "Customer Name",
                        "email": "customer@example.com", 
                        "password": "password123",
                        "phone": "09123456789",
                        "delivery_address": {
                            "street": "123 Main St",
                            "city": "Cebu",
                            "postal_code": "6000"
                        }
                    }
                },
                "create_product": {
                    "method": "POST",
                    "url": "/products/",
                    "body": {
                        "product_name": "Samyang Buldak Cheese Hot Chicken Flavor Ramen",
                        "category_id": "noodles",
                        "unit": "pack",
                        "stock": 50,
                        "expiry_date": "2025-12-31T00:00:00.000Z",
                        "low_stock_threshold": 10,
                        "cost_price": 45.50,
                        "selling_price": 65.00,
                        "status": "active",
                        "is_taxable": true,
                        "SKU": "SAM-BDK-CHZ-001"
                    }
                }
            },
            
            "features": [
                "JWT Authentication with refresh tokens",
                "Role-based access control (admin/employee/customer)",
                "Dual collection customer management",
                "Complete product management with inventory tracking",
                "Session logging and tracking",
                "Password hashing with bcrypt",
                "Input validation with serializers",
                "MongoDB integration",
                "Real-time session statistics",
                "Token blacklisting on logout",
                "Comprehensive error handling"
            ]
        })