from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging
from datetime import datetime, timedelta

from ..services.batch_service import BatchService
from ..services.product_service import ProductService

logger = logging.getLogger(__name__)

class BatchView(View):
    def __init__(self):
        super().__init__()
        self.batch_service = BatchService()
        self.product_service = ProductService()

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

# ================================================================
# BATCH CRUD OPERATIONS
# ================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CreateBatchView(BatchView):
    def post(self, request):
        """Create a new batch when receiving stock"""
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['product_id', 'quantity_received']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }, status=400)
            
            # Create batch
            batch = self.batch_service.create_batch(data)
            
            return JsonResponse({
                'success': True,
                'message': 'Batch created successfully',
                'data': batch
            })
            
        except Exception as e:
            logger.error(f"Error creating batch: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch') 
class BatchListView(BatchView):
    def get(self, request):
        """Get all batches with optional filters"""
        try:
            # Get query parameters for filtering
            filters = {}
            
            product_id = request.GET.get('product_id')
            if product_id:
                filters['product_id'] = product_id
            
            status = request.GET.get('status')
            if status:
                filters['status'] = status
                
            supplier_id = request.GET.get('supplier_id')
            if supplier_id:
                filters['supplier_id'] = supplier_id
                
            # Check for expiring soon filter
            expiring_soon = request.GET.get('expiring_soon')
            if expiring_soon == 'true':
                days_ahead = int(request.GET.get('days_ahead', 30))
                filters['expiring_soon'] = True
                filters['days_ahead'] = days_ahead
            
            batches = self.batch_service.get_all_batches(filters)
            
            return JsonResponse({
                'success': True,
                'data': batches,
                'count': len(batches)
            })
            
        except Exception as e:
            logger.error(f"Error getting batches: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class BatchDetailView(BatchView):
    def get(self, request, batch_id):
        """Get batch details by ID"""
        try:
            batch = self.batch_service.get_batch_by_id(batch_id)
            
            if not batch:
                return JsonResponse({
                    'success': False,
                    'error': 'Batch not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': batch
            })
            
        except Exception as e:
            logger.error(f"Error getting batch details: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class UpdateBatchQuantityView(BatchView):
    def put(self, request, batch_id):
        """Update batch quantity when stock is used/sold"""
        try:
            data = json.loads(request.body)
            
            quantity_used = data.get('quantity_used')
            adjustment_type = data.get('adjustment_type', 'correction')
            adjusted_by = data.get('adjusted_by')
            notes = data.get('notes')
            
            if quantity_used is None:
                return JsonResponse({
                    'success': False,
                    'error': 'quantity_used is required'
                }, status=400)
            
            updated_batch = self.batch_service.update_batch_quantity(
                batch_id,
                quantity_used,
                adjustment_type=adjustment_type,
                adjusted_by=adjusted_by,
                notes=notes
            )
            
            if not updated_batch:
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to update batch or batch not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'message': 'Batch quantity updated successfully',
                'data': updated_batch
            })
            
        except Exception as e:
            logger.error(f"Error updating batch quantity: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# ================================================================
# BATCH QUERIES AND REPORTS
# ================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ProductBatchesView(BatchView):
    def get(self, request, product_id):
        """Get all batches for a specific product"""
        try:
            status = request.GET.get('status')  # Optional status filter
            
            batches = self.batch_service.get_batches_by_product(product_id, status)
            
            return JsonResponse({
                'success': True,
                'data': batches,
                'count': len(batches),
                'product_id': product_id
            })
            
        except Exception as e:
            logger.error(f"Error getting product batches: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ExpiringBatchesView(BatchView):
    def get(self, request):
        """Get batches expiring within specified days"""
        try:
            days_ahead = int(request.GET.get('days_ahead', 30))
            
            expiring_batches = self.batch_service.get_expiring_batches(days_ahead)
            
            return JsonResponse({
                'success': True,
                'data': expiring_batches,
                'count': len(expiring_batches),
                'days_ahead': days_ahead
            })
            
        except Exception as e:
            logger.error(f"Error getting expiring batches: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class ProductsWithExpirySummaryView(BatchView):
    def get(self, request):
        """Get products with their expiry summary information"""
        try:
            products = self.batch_service.get_products_with_expiry_summary()
            
            return JsonResponse({
                'success': True,
                'data': products,
                'count': len(products)
            })
            
        except Exception as e:
            logger.error(f"Error getting products with expiry summary: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# ================================================================
# BATCH OPERATIONS FOR SALES
# ================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ProcessSaleFIFOView(BatchView):
    def post(self, request):
        """Process a sale using FIFO logic"""
        try:
            data = json.loads(request.body)
            
            product_id = data.get('product_id')
            quantity_sold = data.get('quantity_sold')
            
            if not product_id or quantity_sold is None:
                return JsonResponse({
                    'success': False,
                    'error': 'product_id and quantity_sold are required'
                }, status=400)
            
            batches_used = self.batch_service.process_sale_fifo(product_id, quantity_sold)
            
            return JsonResponse({
                'success': True,
                'message': 'Sale processed successfully using FIFO',
                'data': {
                    'product_id': product_id,
                    'quantity_sold': quantity_sold,
                    'batches_used': batches_used
                }
            })
            
        except Exception as e:
            logger.error(f"Error processing FIFO sale: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# ================================================================
# BATCH MAINTENANCE AND ALERTS
# ================================================================

@method_decorator(csrf_exempt, name='dispatch')
class CheckExpiryAlertsView(BatchView):
    def post(self, request):
        """Check for expiring batches and send alerts"""
        try:
            data = json.loads(request.body) if request.body else {}
            days_ahead = data.get('days_ahead', 7)
            
            alert_count = self.batch_service.check_and_alert_expiring_batches(days_ahead)
            
            return JsonResponse({
                'success': True,
                'message': f'Expiry check completed',
                'data': {
                    'alerts_sent': alert_count,
                    'days_ahead': days_ahead
                }
            })
            
        except Exception as e:
            logger.error(f"Error checking expiry alerts: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class MarkExpiredBatchesView(BatchView):
    def post(self, request):
        """Mark expired batches as expired"""
        try:
            expired_count = self.batch_service.mark_expired_batches()
            
            return JsonResponse({
                'success': True,
                'message': 'Expired batches marked successfully',
                'data': {
                    'batches_marked_expired': expired_count
                }
            })
            
        except Exception as e:
            logger.error(f"Error marking expired batches: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# ================================================================
# INTEGRATION WITH PRODUCTS
# ================================================================

@method_decorator(csrf_exempt, name='dispatch')
class ProductWithBatchSummaryView(BatchView):
    def get(self, request, product_id):
        """Get product with its batch summary"""
        try:
            product_with_batches = self.product_service.get_product_with_batch_summary(product_id)
            
            if not product_with_batches:
                return JsonResponse({
                    'success': False,
                    'error': 'Product not found'
                }, status=404)
            
            return JsonResponse({
                'success': True,
                'data': product_with_batches
            })
            
        except Exception as e:
            logger.error(f"Error getting product with batch summary: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class RestockWithBatchView(BatchView):
    def post(self, request, product_id):
        """Restock product and create batch"""
        try:
            data = json.loads(request.body)
            
            quantity_received = data.get('quantity_received')
            if quantity_received is None:
                return JsonResponse({
                    'success': False,
                    'error': 'quantity_received is required'
                }, status=400)
            
            supplier_info = data.get('supplier_info')
            batch_info = data.get('batch_info')
            
            result = self.product_service.restock_product(
                product_id,
                quantity_received,
                supplier_info,
                batch_info
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Product restocked and batch created successfully',
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error restocking with batch: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# ================================================================
# BATCH STATISTICS AND ANALYTICS
# ================================================================

@method_decorator(csrf_exempt, name='dispatch')
class BatchStatisticsView(BatchView):
    def get(self, request):
        """Get batch statistics and analytics"""
        try:
            # Get all batches for analysis
            all_batches = self.batch_service.get_all_batches()
            
            # Calculate statistics
            total_batches = len(all_batches)
            active_batches = len([b for b in all_batches if b.get('status') == 'active'])
            depleted_batches = len([b for b in all_batches if b.get('status') == 'depleted'])
            expired_batches = len([b for b in all_batches if b.get('status') == 'expired'])
            
            # Get expiring soon (within 7 days)
            expiring_soon = self.batch_service.get_expiring_batches(7)
            
            # Calculate total stock from active batches
            total_stock = sum(b.get('quantity_remaining', 0) for b in all_batches if b.get('status') == 'active')
            
            statistics = {
                'total_batches': total_batches,
                'active_batches': active_batches,
                'depleted_batches': depleted_batches,
                'expired_batches': expired_batches,
                'expiring_within_7_days': len(expiring_soon),
                'total_active_stock': total_stock,
                'batch_status_breakdown': {
                    'active': active_batches,
                    'depleted': depleted_batches,
                    'expired': expired_batches
                }
            }
            
            return JsonResponse({
                'success': True,
                'data': statistics
            })
            
        except Exception as e:
            logger.error(f"Error getting batch statistics: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ProductsWithExpirySummaryView(BatchView):
    def get(self, request):
        """Get products with their expiry summary information"""
        try:
            products = self.batch_service.get_products_with_expiry_summary()
            
            return JsonResponse({
                'success': True,
                'data': products,
                'count': len(products)
            })
            
        except Exception as e:
            logger.error(f"Error getting products with expiry summary: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
        
@method_decorator(csrf_exempt, name='dispatch')
class ProcessBatchAdjustmentView(BatchView):
    def post(self, request):
        """Process a batch adjustment using FIFO logic"""
        try:
            data = json.loads(request.body)
            
            product_id = data.get('product_id')
            quantity_used = data.get('quantity_used')
            adjustment_type = data.get('adjustment_type', 'correction')
            adjusted_by = data.get('adjusted_by')  # User ID from frontend
            notes = data.get('notes')
            
            # Validate required fields
            if not product_id or quantity_used is None:
                return JsonResponse({
                    'success': False,
                    'error': 'product_id and quantity_used are required'
                }, status=400)
            
            if quantity_used <= 0:
                return JsonResponse({
                    'success': False,
                    'error': 'quantity_used must be greater than 0'
                }, status=400)
            
            # Process the adjustment
            result = self.batch_service.process_batch_adjustment(
                product_id, 
                quantity_used,
                adjustment_type,
                adjusted_by,
                notes
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Successfully adjusted {quantity_used} units using FIFO',
                'data': result
            })
            
        except Exception as e:
            logger.error(f"Error processing batch adjustment: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)