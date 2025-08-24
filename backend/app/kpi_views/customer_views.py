from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.customer_service import CustomerService
import logging

def get_authenticated_user_from_jwt(request):
    """Helper function to get authenticated user with proper username from JWT token"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        
        from ..services.auth_services import AuthService
        from bson import ObjectId
        
        auth_service = AuthService()
        user_data = auth_service.get_current_user(token)
        
        if not user_data:
            return None
        
        user_id = user_data.get('user_id')
        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            return None
        
        actual_username = user_doc.get('username')
        if actual_username and actual_username.strip():
            display_username = actual_username
        else:
            display_username = user_doc.get('email', 'unknown')
        
        return {
            "user_id": user_id,
            "username": display_username,
            "email": user_doc.get('email'),
            "branch_id": 1,
            "role": user_doc.get('role', 'admin'),
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT')
        }
        
    except Exception as e:
        print(f"JWT Auth helper error: {e}")
        return None

class CustomerListView(APIView):
    def get(self, request):
        """Get all customers - No changes needed"""
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
        """Create new customer - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            customer_service = CustomerService()
            customer_data = request.data
            
            # ✅ UPDATED: Pass current_user to service
            new_customer = customer_service.create_customer(customer_data, current_user)
            
            return Response(new_customer, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomerDetailView(APIView):
    def get(self, request, customer_id):
        """Get customer by ID - No changes needed"""
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
        """Update customer - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            customer_service = CustomerService()
            customer_data = request.data
            
            # ✅ UPDATED: Pass current_user to service
            updated_customer = customer_service.update_customer(customer_id, customer_data, current_user)
            
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
        """Delete customer - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            customer_service = CustomerService()
            
            # ✅ UPDATED: Pass current_user to service
            deleted = customer_service.delete_customer(customer_id, current_user)
            
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


# ================ Customer KPI Views ================
class ActiveCustomerKPIView(APIView):
    def get(self, request):
        try:
            customer_service = CustomerService()
            activeCount = customer_service.get_active_customers()
            return Response({"active_customers": activeCount}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Active CustomerKPI error: {str(e)}")
            print(f"Active CustomerKPI error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class MonthlyCustomerKPIView(APIView):
    def get(self, request):
        try:
            customer_service = CustomerService()
            monthlyCount = customer_service.get_monthly_users()
            return Response({"monthly_customers": monthlyCount}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Monthly CustomerKPI error: {str(e)}")
            print(f"Monthly CustomerKPI error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DailyCustomerKPIView(APIView):
    def get(self, request):
        try:
            customer_service = CustomerService()
            dailyCount = customer_service.get_daily_logins()
            return Response({"daily_customers": dailyCount}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(f"Daily CustomerKPI error: {str(e)}")
            print(f"Daily CustomerKPI error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)