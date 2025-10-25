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


