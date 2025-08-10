from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.customer_service import CustomerService
from ..decorators.authenticationDecorator import require_admin, require_authentication, get_authenticated_user_from_jwt
import logging

logger = logging.getLogger(__name__)

class CustomerListView(APIView):
    def __init__(self):
        self.customer_service = CustomerService()

    @require_admin  
    def get(self, request):
        """Get all customers - Admin only"""
        try:
            # Always include deleted customers, let frontend filter
            customers = self.customer_service.get_all_customers(include_deleted=True)
            return Response(customers, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error getting customers: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def post(self, request):
        """Create new customer - Authenticated users can create customers"""
        try:
            customer_data = request.data
            new_customer = self.customer_service.create_customer(
                customer_data, 
                request.current_user  # Set by decorator
            )
            
            return Response(new_customer, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomerDetailView(APIView):
    def __init__(self):
        self.customer_service = CustomerService()

    @require_authentication
    def get(self, request, customer_id):
        """Get customer by ID - Authentication required"""
        try:
            customer = self.customer_service.get_customer_by_id(customer_id)
            if customer:
                return Response(customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting customer {customer_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def put(self, request, customer_id):
        """Update customer - Authentication required"""
        try:
            customer_data = request.data
            updated_customer = self.customer_service.update_customer(
                customer_id, 
                customer_data, 
                request.current_user  # Set by decorator
            )
            
            if updated_customer:
                return Response(updated_customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error updating customer {customer_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @require_admin
    def delete(self, request, customer_id):
        """Delete customer - Admin only"""
        try:
            deleted = self.customer_service.delete_customer(
                customer_id, 
                request.current_user  # Set by decorator
            )
            
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
            logger.error(f"Error deleting customer {customer_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerRestoreView(APIView):
    """View for restoring soft-deleted customers"""
    def __init__(self):
        self.customer_service = CustomerService()

    @require_admin
    def post(self, request, customer_id):
        """Restore a soft-deleted customer - Admin only"""
        try:
            restored = self.customer_service.restore_customer(
                customer_id, 
                request.current_user
            )
            
            if restored:
                return Response(
                    {"message": "Customer restored successfully"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Customer not found or not deleted"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Error restoring customer {customer_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerHardDeleteView(APIView):
    """View for permanently deleting customers"""
    def __init__(self):
        self.customer_service = CustomerService()

    @require_admin
    def delete(self, request, customer_id):
        """PERMANENTLY delete customer - Admin only with confirmation"""
        try:
            # Require explicit confirmation
            confirm = request.query_params.get('confirm', '').lower()
            if confirm != 'yes':
                return Response(
                    {
                        "error": "Permanent deletion requires confirmation", 
                        "message": "Add ?confirm=yes to permanently delete this customer",
                        "warning": "THIS ACTION CANNOT BE UNDONE"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            deleted = self.customer_service.hard_delete_customer(
                customer_id, 
                request.current_user
            )
            
            if deleted:
                return Response(
                    {"message": "Customer permanently deleted", "warning": "This action cannot be undone"},
                    status=status.HTTP_200_OK
                )
            return Response(
                {"error": "Customer not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            logger.error(f"Error permanently deleting customer {customer_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerSearchView(APIView):
    """View for searching customers"""
    def __init__(self):
        self.customer_service = CustomerService()

    @require_authentication
    def get(self, request):
        """Search customers by name, email, or phone"""
        try:
            search_term = request.query_params.get('q', '').strip()
            if not search_term:
                return Response(
                    {"error": "Search term 'q' parameter is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            customers = self.customer_service.search_customers(search_term)
            return Response(customers, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error searching customers: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerByEmailView(APIView):
    """View for getting customer by email"""
    def __init__(self):
        self.customer_service = CustomerService()
        
    @require_authentication
    def get(self, request, email):
        """Get customer by email"""
        try:
            customer = self.customer_service.get_customer_by_email(email)
            if customer:
                return Response(customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error getting customer by email {email}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerStatisticsView(APIView):
    """View for customer statistics and analytics"""
    def __init__(self):
        self.customer_service = CustomerService()

    @require_authentication
    def get(self, request):
        """Get customer statistics"""
        try:
            stats = self.customer_service.get_customer_statistics()
            return Response(stats, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting customer statistics: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CustomerLoyaltyView(APIView):
    """View for managing customer loyalty points"""
    def __init__(self):
        self.customer_service = CustomerService()

    @require_authentication
    def post(self, request, customer_id):
        """Update customer loyalty points"""
        try:
            points_to_add = request.data.get('points', 0)
            reason = request.data.get('reason', 'Manual adjustment')
            
            if not isinstance(points_to_add, (int, float)) or points_to_add <= 0:
                return Response(
                    {"error": "Points must be a positive number"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            updated_customer = self.customer_service.update_loyalty_points(
                customer_id, 
                points_to_add, 
                reason, 
                request.current_user
            )
            
            if updated_customer:
                return Response(updated_customer, status=status.HTTP_200_OK)
            return Response(
                {"error": "Customer not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        except Exception as e:
            logger.error(f"Error updating loyalty points for customer {customer_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )