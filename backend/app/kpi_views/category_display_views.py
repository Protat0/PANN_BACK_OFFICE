from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..services.category_display_service import category_display_service
import logging

logger = logging.getLogger(__name__)

# ================ DISPLAY AND EXPORT VIEWS ================

class CategoryDataView(APIView):
    """Get categories with sales data"""
    
    def get(self, request):
        """Get all categories with sales data"""
        try:
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            result = category_display_service.get_categories_display(include_deleted=include_deleted)
            
            return Response({
                "success": True,
                "message": "Categories retrieved successfully",
                "categories": result,
                "count": len(result),
                "include_deleted": include_deleted
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Invalid parameter in CategoryDataView: {e}")
            return Response({
                "success": False,
                "error": f"Invalid parameter: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in CategoryDataView: {e}")
            return Response({
                "success": False,
                "error": "Internal server error"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryExportView(APIView):
    """Export categories in CSV or JSON format"""
    
    def get(self, request):
        """Export categories with optional filters"""
        try:
            format_type = request.GET.get('format', 'csv').lower()
            include_sales_data = request.GET.get('include_sales_data', 'true').lower() == 'true'
            include_deleted = request.GET.get('include_deleted', 'false').lower() == 'true'
            
            if format_type not in ['csv', 'json']:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid format. Use csv or json.'
                }, status=400)
            
            # Parse date filter
            date_filter = None
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            if start_date or end_date:
                date_filter = {'start_date': start_date, 'end_date': end_date}
            
            # Validate and export
            category_display_service.validate_export_params(format_type, include_sales_data, date_filter, include_deleted)
            
            if format_type == 'csv':
                export_result = category_display_service.export_categories_csv(
                    include_sales_data=include_sales_data, 
                    date_filter=date_filter, 
                    include_deleted=include_deleted
                )
            else:
                export_result = category_display_service.export_categories_json(
                    include_sales_data=include_sales_data, 
                    date_filter=date_filter, 
                    include_deleted=include_deleted
                )
            
            response = HttpResponse(export_result['content'], content_type=export_result['content_type'])
            response['Content-Disposition'] = f'attachment; filename="{export_result["filename"]}"'
            
            return response
            
        except ValueError as e:
            logger.error(f"Invalid parameter in CategoryExportView: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Invalid parameter: {str(e)}'
            }, status=400)
        except Exception as e:
            logger.error(f"Error in CategoryExportView: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Export failed: {str(e)}'
            }, status=500)


class CategoryStatsView(APIView):
    """Get category statistics"""
    
    def get(self, request):
        """Get comprehensive category statistics"""
        try:
            stats = category_display_service.get_category_stats()
            
            return Response({
                'success': True,
                'message': 'Category statistics retrieved successfully',
                'stats': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return Response({
                "success": False,
                "error": "Failed to retrieve category statistics"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CategoryDateFilterView(APIView):
    """Get categories with date-filtered sales data"""
    
    def get(self, request):
        """Get categories with sales data filtered by date range"""
        try:
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            frequency = request.query_params.get('frequency', 'monthly')
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            result = category_display_service.get_categories_display_with_date_filter(
                start_date=start_date,
                end_date=end_date,
                frequency=frequency,
                include_deleted=include_deleted
            )
            
            return Response({
                'success': True,
                'message': 'Categories with date filter retrieved successfully',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.error(f"Invalid parameter in CategoryDateFilterView: {e}")
            return Response({
                "success": False,
                "error": f"Invalid parameter: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in CategoryDateFilterView: {e}")
            return Response({
                "success": False,
                "error": "Failed to retrieve categories with date filter"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)