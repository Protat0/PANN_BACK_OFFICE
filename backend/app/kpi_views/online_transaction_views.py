from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from ..services.pos.online_transactions_services import OnlineTransactionService
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class OnlineTransactionServiceView(APIView):
    """Base view for online transaction operations"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self):
        super().__init__()
        self.service = OnlineTransactionService()

# ================================================================
# ORDER MANAGEMENT
# ================================================================

class CreateOnlineOrderView(OnlineTransactionServiceView):
    """Create a new online order"""
    # Override authentication and permission to allow JWT token authentication
    authentication_classes = []  # Disable default authentication, we'll validate JWT manually
    permission_classes = [AllowAny]  # Allow access without Django auth, we'll validate JWT manually
    
    def post(self, request):
        try:
            # Extract customer_id from JWT token if available, otherwise use request data
            import jwt
            from django.conf import settings
            
            logger.info(f"=== CREATE ORDER REQUEST ===")
            
            # Try to get customer_id from JWT token first
            auth_header = request.headers.get('Authorization', '')
            customer_id_from_token = None
            
            if auth_header.startswith('Bearer '):
                try:
                    token = auth_header.split(' ')[1]
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                    customer_id_from_token = payload.get('customer_id')
                    logger.info(f"✅ Customer ID extracted from JWT: {customer_id_from_token}")
                except jwt.ExpiredSignatureError:
                    logger.error("❌ JWT token expired")
                except jwt.InvalidTokenError as e:
                    logger.error(f"❌ Invalid JWT token: {str(e)}")
                except Exception as e:
                    logger.warning(f"⚠️ Could not decode JWT token: {str(e)}")
            
            order_data = request.data
            customer_id = customer_id_from_token or order_data.get('customer_id')
            
            if not customer_id:
                logger.error("❌ No customer_id found in token or request data")
                return Response(
                    {"error": "Customer ID is required. Please ensure you are logged in."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use customer_id from token if available, otherwise use the one from request
            if customer_id_from_token:
                order_data['customer_id'] = customer_id_from_token
                logger.info(f"✅ Using customer_id from JWT token: {customer_id_from_token}")
            
            result = self.service.create_online_order(order_data, customer_id)
            
            if result['success']:
                logger.info(f"✅ Order created successfully: {result.get('data', {}).get('order_id', 'N/A')}")
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                logger.error(f"❌ Order creation failed: {result.get('error', 'Unknown error')}")
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"❌ Error creating online order: {str(e)}")
            logger.exception(e)
            return Response(
                {"error": f"Failed to create order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetOnlineOrderView(OnlineTransactionServiceView):
    """Get a specific online order by ID"""
    
    def get(self, request, order_id):
        try:
            order = self.service.get_order_by_id(order_id)
            
            if order:
                # Add order_id alias for frontend compatibility
                if '_id' in order:
                    order['order_id'] = order['_id']
                return Response(order, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Order not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
                
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            return Response(
                {"error": f"Failed to fetch order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetCustomerOrdersView(OnlineTransactionServiceView):
    """Get all orders for a specific customer"""
    
    def get(self, request, customer_id):
        try:
            status_filter = request.query_params.get('status')
            limit = int(request.query_params.get('limit', 50))
            
            orders = self.service.get_customer_orders(
                customer_id, 
                status=status_filter, 
                limit=limit
            )
            
            # Add order_id alias for frontend compatibility
            for order in orders:
                if '_id' in order:
                    order['order_id'] = order['_id']
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching customer orders: {str(e)}")
            return Response(
                {"error": f"Failed to fetch customer orders: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetMyOrderHistoryView(OnlineTransactionServiceView):
    """Get order history for the currently logged-in customer (uses JWT auth)"""
    
    def get(self, request):
        try:
            # Extract customer_id from JWT token in Authorization header
            import jwt
            from django.conf import settings
            
            logger.info(f"=== ORDER HISTORY REQUEST ===")
            
            # Get JWT token from Authorization header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                logger.error("❌ No Bearer token in Authorization header")
                return Response(
                    {
                        "success": False,
                        "error": "Authentication required",
                        "results": []
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            token = auth_header.split(' ')[1]
            
            try:
                # Decode JWT token to get customer_id
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
                customer_id = payload.get('customer_id')
                
                if not customer_id:
                    logger.error("❌ No customer_id in JWT token payload")
                    return Response(
                        {
                            "success": False,
                            "error": "Invalid token: customer_id not found",
                            "results": []
                        }, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                
                logger.info(f"✅ Customer ID extracted from JWT: {customer_id}")
                logger.info(f"✅ Customer email from token: {payload.get('email', 'N/A')}")
                
            except jwt.ExpiredSignatureError:
                logger.error("❌ JWT token expired")
                return Response(
                    {
                        "success": False,
                        "error": "Token expired",
                        "results": []
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            except jwt.InvalidTokenError as e:
                logger.error(f"❌ Invalid JWT token: {str(e)}")
                return Response(
                    {
                        "success": False,
                        "error": "Invalid token",
                        "results": []
                    }, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get query parameters
            status_filter = request.query_params.get('status')
            limit = int(request.query_params.get('limit', 50))
            offset = int(request.query_params.get('offset', 0))
            
            logger.info(f"Query params: status={status_filter}, limit={limit}, offset={offset}")
            
            # Fetch orders from the online_orders collection
            logger.info(f"📞 Calling service.get_customer_orders(customer_id={customer_id})")
            orders_list = self.service.get_customer_orders(
                customer_id, 
                status=status_filter, 
                limit=limit
            )
            
            logger.info(f"📦 Service returned: {type(orders_list)} with {len(orders_list) if orders_list else 0} items")
            
            # Convert MongoDB documents to JSON-serializable format
            orders_json = []
            for order in orders_list:
                # Convert ObjectId to string (if needed) and add order_id alias
                if '_id' in order:
                    order['_id'] = str(order['_id'])
                    order['order_id'] = order['_id']  # Add order_id alias for frontend
                orders_json.append(order)
                logger.info(f"  - Order: {order.get('order_id')} | Status: {order.get('order_status')} | Customer: {order.get('customer_id')}")
            
            logger.info(f"✅ FINAL: Found {len(orders_json)} orders for customer {customer_id}")
            
            # Return in the format expected by frontend
            response_data = {
                'success': True,
                'results': orders_json,
                'count': len(orders_json)
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching customer order history: {str(e)}")
            logger.exception(e)  # Log full stack trace
            return Response(
                {
                    "success": False,
                    "error": f"Failed to fetch order history: {str(e)}",
                    "results": []  # Add empty results for frontend compatibility
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetAllOrdersView(OnlineTransactionServiceView):
    """Get all orders with optional filters (for staff)"""
    
    def get(self, request):
        try:
            filters = {}
            
            # Parse query parameters
            if request.query_params.get('status'):
                filters['status'] = request.query_params.get('status')
            if request.query_params.get('payment_status'):
                filters['payment_status'] = request.query_params.get('payment_status')
            if request.query_params.get('customer_id'):
                filters['customer_id'] = request.query_params.get('customer_id')
            if request.query_params.get('start_date'):
                filters['start_date'] = datetime.fromisoformat(
                    request.query_params.get('start_date')
                )
            if request.query_params.get('end_date'):
                filters['end_date'] = datetime.fromisoformat(
                    request.query_params.get('end_date')
                )
            
            limit = int(request.query_params.get('limit', 100))
            
            orders = self.service.get_all_orders(filters=filters, limit=limit)
            
            # Add order_id alias for frontend compatibility
            for order in orders:
                if '_id' in order:
                    order['order_id'] = order['_id']
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            return Response(
                {"error": f"Failed to fetch orders: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# ORDER STATUS MANAGEMENT
# ================================================================

class UpdateOrderStatusView(OnlineTransactionServiceView):
    """Update order status"""
    
    def post(self, request, order_id):
        try:
            new_status = request.data.get('status')
            updated_by = request.data.get('updated_by', request.user.id)
            notes = request.data.get('notes', '')
            
            if not new_status:
                return Response(
                    {"error": "Status is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order = self.service.update_order_status(
                order_id, 
                new_status, 
                updated_by, 
                notes
            )
            
            # Add order_id alias for frontend compatibility
            if order and '_id' in order:
                order['order_id'] = order['_id']
            
            return Response(order, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            return Response(
                {"error": f"Failed to update order status: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdatePaymentStatusView(OnlineTransactionServiceView):
    """Update payment status"""
    
    def post(self, request, order_id):
        try:
            payment_status = request.data.get('payment_status')
            payment_reference = request.data.get('payment_reference')
            confirmed_by = request.data.get('confirmed_by', request.user.id)
            
            if not payment_status:
                return Response(
                    {"error": "Payment status is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order = self.service.update_payment_status(
                order_id, 
                payment_status, 
                payment_reference, 
                confirmed_by
            )
            
            # Add order_id alias for frontend compatibility
            if order and '_id' in order:
                order['order_id'] = order['_id']
            
            return Response(order, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating payment status: {str(e)}")
            return Response(
                {"error": f"Failed to update payment status: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MarkReadyForDeliveryView(OnlineTransactionServiceView):
    """Mark order as ready for delivery"""
    
    def post(self, request, order_id):
        try:
            prepared_by = request.data.get('prepared_by', request.user.id)
            delivery_notes = request.data.get('delivery_notes', '')
            
            order = self.service.mark_ready_for_delivery(
                order_id, 
                prepared_by, 
                delivery_notes
            )
            
            # Add order_id alias for frontend compatibility
            if order and '_id' in order:
                order['order_id'] = order['_id']
            
            return Response(order, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error marking order ready: {str(e)}")
            return Response(
                {"error": f"Failed to mark order ready: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CompleteOrderView(OnlineTransactionServiceView):
    """Mark order as completed (delivered)"""
    
    def post(self, request, order_id):
        try:
            completed_by = request.data.get('completed_by', request.user.id)
            delivery_person = request.data.get('delivery_person')
            
            order = self.service.complete_order(
                order_id, 
                completed_by, 
                delivery_person
            )
            
            # Add order_id alias for frontend compatibility
            if order and '_id' in order:
                order['order_id'] = order['_id']
            
            return Response(order, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error completing order: {str(e)}")
            return Response(
                {"error": f"Failed to complete order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# ORDER CANCELLATION
# ================================================================

class CancelOrderView(OnlineTransactionServiceView):
    """Cancel an online order"""
    
    def post(self, request, order_id):
        try:
            cancellation_reason = request.data.get('cancellation_reason')
            cancelled_by = request.data.get('cancelled_by', request.user.id)
            
            if not cancellation_reason:
                return Response(
                    {"error": "Cancellation reason is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            order = self.service.cancel_online_order(
                order_id, 
                cancellation_reason, 
                cancelled_by
            )
            
            # Add order_id alias for frontend compatibility
            if order and '_id' in order:
                order['order_id'] = order['_id']
            
            return Response(order, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return Response(
                {"error": f"Failed to cancel order: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# AUTO-CANCELLATION MANAGEMENT
# ================================================================

class AutoCancelExpiredOrdersView(OnlineTransactionServiceView):
    """Manually trigger auto-cancellation of expired orders"""
    
    def post(self, request):
        try:
            expiry_minutes = request.data.get('expiry_minutes', 30)
            
            result = self.service.manual_check_expired_orders()
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in auto-cancellation: {str(e)}")
            return Response(
                {"error": f"Auto-cancellation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UpdateAutoCancellationSettingsView(OnlineTransactionServiceView):
    """Update auto-cancellation settings"""
    
    def post(self, request):
        try:
            enabled = request.data.get('enabled')
            check_interval = request.data.get('check_interval')
            expiry_minutes = request.data.get('expiry_minutes')
            
            result = self.service.update_auto_cancellation_settings(
                enabled=enabled,
                check_interval=check_interval,
                expiry_minutes=expiry_minutes
            )
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating auto-cancellation settings: {str(e)}")
            return Response(
                {"error": f"Failed to update settings: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetAutoCancellationStatusView(OnlineTransactionServiceView):
    """Get auto-cancellation status and statistics"""
    
    def get(self, request):
        try:
            status_info = self.service.get_scheduler_status()
            statistics = self.service.get_order_statistics()
            
            return Response({
                'scheduler_status': status_info,
                'order_statistics': statistics
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting auto-cancellation status: {str(e)}")
            return Response(
                {"error": f"Failed to get status: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# ORDER FILTERING AND STATUS VIEWS
# ================================================================

class GetPendingOrdersView(OnlineTransactionServiceView):
    """Get all pending orders"""
    
    def get(self, request):
        try:
            orders = self.service.get_pending_orders()
            
            # Add order_id alias for frontend compatibility
            for order in orders:
                if '_id' in order:
                    order['order_id'] = order['_id']
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching pending orders: {str(e)}")
            return Response(
                {"error": f"Failed to fetch pending orders: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetProcessingOrdersView(OnlineTransactionServiceView):
    """Get all orders being prepared"""
    
    def get(self, request):
        try:
            orders = self.service.get_processing_orders()
            
            # Add order_id alias for frontend compatibility
            for order in orders:
                if '_id' in order:
                    order['order_id'] = order['_id']
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching processing orders: {str(e)}")
            return Response(
                {"error": f"Failed to fetch processing orders: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GetOrdersByStatusView(OnlineTransactionServiceView):
    """Get orders by specific status"""
    
    def get(self, request, status):
        try:
            limit = int(request.query_params.get('limit', 50))
            orders = self.service.get_orders_by_status(status, limit)
            
            # Add order_id alias for frontend compatibility
            for order in orders:
                if '_id' in order:
                    order['order_id'] = order['_id']
            
            return Response(orders, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error fetching orders by status: {str(e)}")
            return Response(
                {"error": f"Failed to fetch orders: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# REPORTING AND ANALYTICS
# ================================================================

class GetOrderSummaryView(OnlineTransactionServiceView):
    """Get order summary for date range"""
    
    def get(self, request):
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date or not end_date:
                return Response(
                    {"error": "Both start_date and end_date are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)
            
            summary = self.service.get_order_summary(start_date, end_date)
            
            return Response(summary, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting order summary: {str(e)}")
            return Response(
                {"error": f"Failed to get summary: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================================================================
# UTILITY VIEWS
# ================================================================

class ValidateOrderStockView(APIView):
    """Validate stock availability for order items - Public access for customers"""
    permission_classes = []  # Allow public access for stock validation
    
    def __init__(self):
        super().__init__()
        self.service = OnlineTransactionService()
    
    def post(self, request):
        try:
            items = request.data.get('items', [])
            
            if not items:
                return Response(
                    {"error": "Items are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validation = self.service.validate_order_stock(items)
            
            return Response(validation, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error validating stock: {str(e)}")
            return Response(
                {"error": f"Stock validation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ValidatePointsRedemptionView(APIView):
    """Validate loyalty points redemption - Public access for customers"""
    permission_classes = []  # Allow public access for points validation
    
    def __init__(self):
        super().__init__()
        self.service = OnlineTransactionService()
    
    def post(self, request):
        try:
            customer_id = request.data.get('customer_id')
            points_to_redeem = request.data.get('points_to_redeem', 0)
            subtotal = request.data.get('subtotal', 0)
            
            if not customer_id:
                return Response(
                    {"error": "Customer ID is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            validation = self.service.validate_points_redemption(
                customer_id, 
                points_to_redeem, 
                subtotal
            )
            
            return Response(validation, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error validating points: {str(e)}")
            return Response(
                {"error": f"Points validation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CalculateServiceFeeView(OnlineTransactionServiceView):
    """Calculate service fee for payment method"""
    
    def post(self, request):
        try:
            subtotal_after_discount = request.data.get('subtotal_after_discount', 0)
            delivery_fee = request.data.get('delivery_fee', 0)
            payment_method = request.data.get('payment_method', 'cod')
            
            fee_data = self.service.calculate_service_fee(
                subtotal_after_discount,
                delivery_fee,
                payment_method
            )
            
            return Response(fee_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error calculating service fee: {str(e)}")
            return Response(
                {"error": f"Fee calculation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CalculateLoyaltyPointsView(APIView):
    """Calculate loyalty points earned - Public access for customers"""
    permission_classes = []  # Allow public access for points calculation
    
    def __init__(self):
        super().__init__()
        self.service = OnlineTransactionService()
    
    def post(self, request):
        try:
            subtotal_after_discount = request.data.get('subtotal_after_discount', 0)
            
            points = self.service.calculate_loyalty_points_earned(subtotal_after_discount)
            
            return Response({'points_earned': points}, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error calculating loyalty points: {str(e)}")
            return Response(
                {"error": f"Points calculation failed: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
