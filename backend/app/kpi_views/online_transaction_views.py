from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..decorators.authenticationDecorator import require_authentication
from ..services.online_transactions_service import OnlineTransactionService
import logging

logger = logging.getLogger(__name__)


class CreateOnlineOrderView(APIView):
    """Create a new online order (customer website)."""

    @require_authentication
    def post(self, request):
        try:
            service = OnlineTransactionService()

            customer_id = request.data.get('customer_id')
            # Fallback to token user id if not provided
            if not customer_id:
                user_ctx = getattr(request, 'current_user', None) or {}
                customer_id = user_ctx.get('user_id')

            if not customer_id:
                return Response({
                    'success': False,
                    'message': 'Customer ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)

            order_data = {
                'items': request.data.get('items', []),
                'delivery_address': request.data.get('delivery_address', {}),
                'delivery_type': request.data.get('delivery_type', 'delivery'),
                'payment_method': request.data.get('payment_method', 'cod'),
                'points_to_redeem': request.data.get('points_to_redeem', 0),
                'notes': request.data.get('notes') or request.data.get('special_instructions', ''),
            }

            result = service.create_online_order(order_data, customer_id)

            return Response({
                'success': True,
                'message': 'Order created successfully',
                'data': result['data']
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            logger.error(f"Online order validation error: {e}")
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Online order error: {e}")
            return Response({'success': False, 'message': f'Failed to create order: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetCustomerOrderHistoryView(APIView):
    """Get customer's order history from online_transactions collection."""
    
    @require_authentication
    def get(self, request):
        try:
            from ..database import db_manager
            
            # Get customer_id from JWT token
            user_ctx = getattr(request, 'current_user', None) or {}
            customer_id = user_ctx.get('user_id')
            
            if not customer_id:
                return Response({
                    'success': False,
                    'message': 'Customer ID is required'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Get limit from query params
            limit = int(request.query_params.get('limit', 50))
            
            # Query online_transactions collection
            db = db_manager.get_database()
            online_transactions = db.online_transactions
            
            query = {'customer_id': customer_id}
            orders = list(
                online_transactions.find(query)
                .sort('transaction_date', -1)  # Most recent first
                .limit(limit)
            )
            
            # Convert ObjectId to string if present
            for order in orders:
                if '_id' in order:
                    order['_id'] = str(order['_id'])
            
            return Response({
                'success': True,
                'results': orders,
                'count': len(orders)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting order history: {e}")
            return Response({
                'success': False,
                'error': f'Failed to get order history: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


