from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.supplier_service import SupplierService
from ..decorators.authenticationDecorator import require_admin, require_authentication, require_permission, get_authenticated_user_from_jwt
import logging

logger = logging.getLogger(__name__)

# ================================================================
# SUPPLIER VIEW CLASSES
# ================================================================

class SupplierHealthCheckView(APIView):
    def get(self, request):
        return Response({
            "message": "Supplier Management API is running!",
            "status": "active",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)

class SupplierListView(APIView):
    def __init__(self):
        self.supplier_service = SupplierService()
    
    @require_authentication
    def get(self, request):
        """Get suppliers with pagination and filters"""
        try:
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 50))
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            # Only admins can view deleted suppliers
            if include_deleted and request.current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required to view deleted suppliers"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Build filters
            filters = {}
            if request.query_params.get('search'):
                filters['search'] = request.query_params.get('search')
            if request.query_params.get('status'):
                filters['status'] = request.query_params.get('status')
            
            result = self.supplier_service.get_suppliers(
                filters=filters,
                include_deleted=include_deleted,
                page=page,
                per_page=per_page
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting suppliers: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def post(self, request):
        """Create new supplier - Requires authentication"""
        try:
            # Basic validation
            if not request.data.get('supplier_name'):
                return Response(
                    {"error": "Supplier name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user ID from authenticated user
            user_id = request.current_user.get('_id', 'system')
            
            new_supplier = self.supplier_service.create_supplier(request.data, user_id=user_id)
            return Response(new_supplier, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error creating supplier: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class SupplierDetailView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def get(self, request, supplier_id):
        """Get supplier by ID (with optional deleted suppliers for admin)"""
        try:
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            # Only admins can view deleted suppliers
            if include_deleted:
                current_user = request.current_user 
                if not current_user or current_user.get('role', '').lower() != 'admin':
                    return Response(
                        {"error": "Admin permissions required to view deleted suppliers"}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            supplier = self.supplier_service.get_supplier_by_id(supplier_id, include_deleted=include_deleted)
            if not supplier:
                return Response(
                    {"error": "Supplier not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(supplier, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def put(self, request, supplier_id):
        """Update supplier - Requires authentication"""
        try:
            # Get user ID from authenticated user
            user_id = request.current_user.get('_id', 'system')
            
            updated_supplier = self.supplier_service.update_supplier(
                supplier_id, 
                request.data,
                user_id=user_id
            )
            
            if not updated_supplier:
                return Response(
                    {"error": "Supplier not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(updated_supplier, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @require_authentication
    def delete(self, request, supplier_id):
        """Soft delete supplier - Requires authentication"""
        try:
            # Get user ID from authenticated user
            user_id = request.current_user.get('_id', 'system')
            
            deleted = self.supplier_service.delete_supplier(
                supplier_id, 
                hard_delete=False,
                user_id=user_id
            )
            
            if not deleted:
                return Response(
                    {"error": "Supplier not found or already deleted"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Supplier deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error deleting supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SupplierRestoreView(APIView):
    """View for restoring soft-deleted suppliers"""
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def post(self, request, supplier_id):
        """Add purchase order to supplier"""
        try:
            # Basic validation
            if not request.data.get('order_id'):
                return Response(
                    {"error": "Order ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not request.data.get('items') or not isinstance(request.data.get('items'), list):
                return Response(
                    {"error": "Items array is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get authenticated user ID - this should work with your decorator
            user_id = request.current_user.get('_id', 'system')
            print(f"Creating order with user_id: {user_id}")  # Debug log
            
            updated_supplier = self.supplier_service.add_purchase_order(
                supplier_id, 
                request.data,
                user_id=user_id
            )
            
            if not updated_supplier:
                return Response(
                    {"error": "Failed to add purchase order"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                "message": "Purchase order added successfully",
                "supplier": updated_supplier
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error adding purchase order to supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class SupplierHardDeleteView(APIView):
    """View for permanently deleting suppliers (DANGEROUS)"""
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def delete(self, request, supplier_id):
        """PERMANENTLY delete supplier - Requires admin authentication"""
        try:
            current_user = request.current_user
            if not current_user or current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            confirm = request.query_params.get('confirm', '').lower()
            if confirm != 'yes':
                return Response({
                    "error": "Permanent deletion requires confirmation", 
                    "message": "Add ?confirm=yes to permanently delete this supplier"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = current_user.get('_id', 'system')
            
            deleted = self.supplier_service.delete_supplier(
                supplier_id, 
                hard_delete=True,
                user_id=user_id
            )
            
            if not deleted:
                return Response(
                    {"error": "Supplier not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                "message": "Supplier permanently deleted"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeletedSuppliersView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def get(self, request):
        """Get soft-deleted suppliers - Admin only"""
        try:
            current_user = request.current_user
            if not current_user or current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            page = int(request.query_params.get('page', 1))
            per_page = int(request.query_params.get('per_page', 50))
            
            result = self.supplier_service.get_deleted_suppliers(page=page, per_page=per_page)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting deleted suppliers: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# PURCHASE ORDER VIEW CLASSES
# ================================================================

class PurchaseOrderListView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def get(self, request, supplier_id):
        """Get purchase orders for a supplier"""
        try:
            status_filter = request.query_params.get('status')
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            # Only admins can view deleted orders
            if include_deleted and request.current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required to view deleted orders"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            orders = self.supplier_service.get_purchase_orders(
                supplier_id, 
                status=status_filter, 
                include_deleted=include_deleted
            )
            
            return Response({
                'orders': orders,
                'supplier_id': supplier_id,
                'total': len(orders)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting purchase orders for supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def post(self, request, supplier_id):
        """Add purchase order to supplier"""
        try:
            # Basic validation
            if not request.data.get('order_id'):
                return Response(
                    {"error": "Order ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not request.data.get('items') or not isinstance(request.data.get('items'), list):
                return Response(
                    {"error": "Items array is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user ID from authenticated user
            user_id = request.current_user.get('_id', 'system')
            
            updated_supplier = self.supplier_service.add_purchase_order(
                supplier_id, 
                request.data,
                user_id=user_id
            )
            
            if not updated_supplier:
                return Response(
                    {"error": "Failed to add purchase order"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                "message": "Purchase order added successfully",
                "supplier": updated_supplier
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error adding purchase order to supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class PurchaseOrderDetailView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def get(self, request, supplier_id, order_id):
        """Get specific purchase order"""
        try:
            order = self.supplier_service.get_purchase_order_by_id(supplier_id, order_id)
            
            if not order:
                return Response(
                    {"error": "Purchase order not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response(order, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting purchase order {order_id} for supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def put(self, request, supplier_id, order_id):
        """Update purchase order"""
        try:
            # Get user ID from authenticated user
            user_id = request.current_user.get('_id', 'system')
            
            updated_supplier = self.supplier_service.update_purchase_order(
                supplier_id, 
                order_id, 
                request.data,
                user_id=user_id
            )
            
            if not updated_supplier:
                return Response(
                    {"error": "Purchase order not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Purchase order updated successfully",
                "supplier": updated_supplier
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating purchase order {order_id} for supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @require_authentication
    def delete(self, request, supplier_id, order_id):
        """Soft delete purchase order"""
        try:
            # Get user ID from authenticated user
            user_id = request.current_user.get('_id', 'system')
            
            deleted = self.supplier_service.delete_purchase_order(
                supplier_id, 
                order_id, 
                hard_delete=False,
                user_id=user_id
            )
            
            if not deleted:
                return Response(
                    {"error": "Purchase order not found or already deleted"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Purchase order deleted successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error deleting purchase order {order_id} for supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PurchaseOrderRestoreView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def post(self, request, supplier_id, order_id):
        """Restore soft-deleted purchase order - Admin only"""
        try:
            current_user = request.current_user
            if not current_user or current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            user_id = current_user.get('_id', 'system')
            
            restored = self.supplier_service.restore_purchase_order(
                supplier_id, 
                order_id,
                user_id=user_id
            )
            
            if not restored:
                return Response(
                    {"error": "Purchase order not found or not deleted"},
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Purchase order restored successfully"},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error restoring purchase order {order_id} for supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PurchaseOrderHardDeleteView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def delete(self, request, supplier_id, order_id):
        """PERMANENTLY delete purchase order - Admin only"""
        try:
            current_user = request.current_user
            if not current_user or current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            confirm = request.query_params.get('confirm', '').lower()
            if confirm != 'yes':
                return Response({
                    "error": "Permanent deletion requires confirmation", 
                    "message": "Add ?confirm=yes to permanently delete this purchase order"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_id = current_user.get('_id', 'system')
            
            deleted = self.supplier_service.delete_purchase_order(
                supplier_id, 
                order_id, 
                hard_delete=True,
                user_id=user_id
            )
            
            if not deleted:
                return Response(
                    {"error": "Purchase order not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            return Response({
                "message": "Purchase order permanently deleted"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class DeletedPurchaseOrdersView(APIView):
    def __init__(self):
        super().__init__()
        self.supplier_service = SupplierService()

    @require_authentication
    def get(self, request, supplier_id):
        """Get soft-deleted purchase orders for a supplier - Admin only"""
        try:
            current_user = request.current_user
            if not current_user or current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            deleted_orders = self.supplier_service.get_deleted_purchase_orders(supplier_id)
            
            return Response({
                'orders': deleted_orders,
                'supplier_id': supplier_id,
                'total': len(deleted_orders)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting deleted purchase orders for supplier {supplier_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )