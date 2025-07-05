from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.category_service import CategoryService, CategoryDisplayService
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

# ================ CATEGORY VIEWS ================

class CategoryKPIView(APIView):
    def post(self, request):
        """Category Creation"""
        try:
            category_service = CategoryService()
            
            # Extract category data from request
            category_name = request.data.get('category_name')
            description = request.data.get('description', '')
            status_value = request.data.get('status', 'active')
            sub_categories = request.data.get('sub_categories', [])
            
            # Validate required fields
            if not category_name:
                return Response(
                    {"error": "Category name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare category data
            category_data = {
                'category_name': category_name,
                'description': description,
                'status': status_value,
                'sub_categories': sub_categories
            }
            
            # Create the category
            result = category_service.create_category(category_data)
            
            return Response({
                "message": "Category created successfully",
                "category": result
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all categories or search categories"""
        try:
            category_service = CategoryService()
            
            # Check if there's a search query
            search_term = request.query_params.get('search')
            active_only = request.query_params.get('active_only', 'false').lower() == 'true'
            
            if search_term:
                categories = category_service.search_categories(search_term)
            elif active_only:
                categories = category_service.get_active_categories()
            else:
                categories = category_service.get_all_categories()
            
            return Response({
                "message": "Categories retrieved successfully",
                "categories": categories,
                "count": len(categories)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryDetailView(APIView):
    def get(self, request, category_id):
        """Get a specific category by ID"""
        try:
            category_service = CategoryService()
            category = category_service.get_category_by_id(category_id)
            
            if not category:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category retrieved successfully",
                "category": category
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, category_id):
        """Update a category"""
        try:
            category_service = CategoryService()
            
            # Extract update data
            update_data = {}
            if 'category_name' in request.data:
                update_data['category_name'] = request.data['category_name']
            if 'description' in request.data:
                update_data['description'] = request.data['description']
            if 'status' in request.data:
                update_data['status'] = request.data['status']
            if 'sub_categories' in request.data:
                update_data['sub_categories'] = request.data['sub_categories']
            
            if not update_data:
                return Response(
                    {"error": "No valid fields to update"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.update_category(category_id, update_data)
            
            if not result:
                return Response(
                    {"error": "Category not found or no changes made"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category updated successfully",
                "category": result
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, category_id):
        """Delete (deactivate) a category"""
        try:
            category_service = CategoryService()
            result = category_service.delete_category(category_id)
            
            if not result:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category deleted successfully"
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategorySubcategoryView(APIView):
    def post(self, request, category_id):
        """Add a subcategory to a category"""
        try:
            category_service = CategoryService()
            subcategory_data = request.data.get('subcategory')
            
            if not subcategory_data:
                return Response(
                    {"error": "Subcategory data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.add_subcategory(category_id, subcategory_data)
            
            if not result:
                return Response(
                    {"error": "Failed to add subcategory or category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory added successfully"
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, category_id):
        """Remove a subcategory from a category"""
        try:
            category_service = CategoryService()
            subcategory_data = request.data.get('subcategory')
            
            if not subcategory_data:
                return Response(
                    {"error": "Subcategory data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.remove_subcategory(category_id, subcategory_data)
            
            if not result:
                return Response(
                    {"error": "Failed to remove subcategory or category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory removed successfully"
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request, category_id):
        """Get all subcategories for a category"""
        try:
            category_service = CategoryService()
            subcategories = category_service.get_subcategories(category_id)
            
            return Response({
                "message": "Subcategories retrieved successfully",
                "subcategories": subcategories,
                "count": len(subcategories)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryDataView(APIView):
    def get(self, request):
        """Get all categories with sales data"""
        try:
            #Lines with this symbol (#) are for debugging
          #  print("=== CategoryDataView.get called ===")
          #  print(f"Request path: {request.path}")
          #  print(f"Request method: {request.method}")
          #  print(f"Request GET params: {request.GET}")
          #  print(f"URL kwargs: {getattr(self, 'kwargs', {})}")
            
            category_service = CategoryDisplayService()
            result = category_service.get_categories_display()
            
          #  print("=== CategoryDataView.get completed successfully ===")
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"ERROR in CategoryDataView: {e}")
            import traceback
            print(f"TRACEBACK: {traceback.format_exc()}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@method_decorator(csrf_exempt, name='dispatch')
class CategoryExportView(APIView):
    """Export categories in CSV or JSON format"""
    
    def get(self, request):
        try:
            # Get query parameters
            format_type = request.GET.get('format', 'csv').lower()
            include_sales_data = request.GET.get('include_sales_data', 'true').lower() == 'true'
            
            print(f"Export request: format={format_type}, include_sales_data={include_sales_data}")
            
            # Parse date filter if provided
            date_filter = None
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            frequency = request.GET.get('frequency', 'monthly')
            
            if start_date or end_date:
                date_filter = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'frequency': frequency
                }
            
            # Initialize service
            category_service = CategoryDisplayService()
            
            # Export data based on format
            if format_type == 'csv':
                export_result = category_service.export_categories_csv(
                    include_sales_data=include_sales_data,
                    date_filter=date_filter
                )
            elif format_type == 'json':
                export_result = category_service.export_categories_json(
                    include_sales_data=include_sales_data,
                    date_filter=date_filter
                )
            else:
                return JsonResponse({
                    'error': 'Invalid format. Use csv or json.'
                }, status=400)
            
            # Return file for download
            response = HttpResponse(
                export_result['content'],
                content_type=export_result['content_type']
            )
            response['Content-Disposition'] = f'attachment; filename="{export_result["filename"]}"'
            return response
            
        except Exception as e:
            print(f"Error in CategoryExportView: {e}")
            return JsonResponse({
                'error': f'Export failed: {str(e)}'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CategoryExportStatsView(APIView):
    """Get export statistics for categories"""
    
    def get(self, request):
        try:
            category_service = CategoryDisplayService()
            stats = category_service.get_export_stats()
            
            return JsonResponse({
                'success': True,
                'message': 'Export statistics retrieved successfully',
                'data': stats
            })
            
        except Exception as e:
            print(f"Error in CategoryExportStatsView: {e}")
            return JsonResponse({
                'error': f'Failed to get export stats: {str(e)}'
            }, status=500)