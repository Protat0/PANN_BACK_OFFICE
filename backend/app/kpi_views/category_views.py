from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ..services.category_service import CategoryService, CategoryDisplayService, ProductSubcategoryService
from ..decorators.authenticationDecorator import require_authentication, require_admin, require_permission
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

# ================ CATEGORY CRUD VIEWS ================

class CategoryKPIView(APIView):
    
    @require_authentication
    def post(self, request):
        """Create a new category"""
        try:
            logger.info(f"Creating category by user: {request.current_user['username']}")
            
            category_service = CategoryService()
            
            # Extract and validate category data
            category_data = {
                'category_name': request.data.get('category_name'),
                'description': request.data.get('description', ''),
                'status': request.data.get('status', 'active'),
                'sub_categories': request.data.get('sub_categories', [])
            }
            
            # Add image fields if present
            image_fields = ['image_url', 'image_filename', 'image_size', 'image_type', 'image_uploaded_at']
            for field in image_fields:
                if field in request.data and request.data[field] is not None:
                    category_data[field] = request.data[field]
            
            # Validate required fields
            if not category_data['category_name']:
                return Response(
                    {"error": "Category name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create category
            result = category_service.create_category(category_data, request.current_user)
            
            return Response({
                "message": "Category created successfully",
                "category": result,
                "created_by": request.current_user['username']
            }, status=status.HTTP_201_CREATED)

        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error creating category: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all categories or search categories"""
        try:
            category_service = CategoryService()
            
            # Check query parameters
            search_term = request.query_params.get('search')
            active_only = request.query_params.get('active_only', 'false').lower() == 'true'
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            limit = int(request.query_params.get('limit', 100))
            skip = int(request.query_params.get('skip', 0))
            
            if search_term:
                categories = category_service.search_categories(
                    search_term, 
                    include_deleted=include_deleted, 
                    limit=limit
                )
            elif active_only:
                categories = category_service.get_active_categories(include_deleted=include_deleted)
            else:
                categories = category_service.get_all_categories(
                    include_deleted=include_deleted, 
                    limit=limit, 
                    skip=skip
                )
            
            return Response({
                "message": "Categories retrieved successfully",
                "categories": categories,
                "count": len(categories),
                "include_deleted": include_deleted
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting categories: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryDetailView(APIView):
    
    def get(self, request, category_id):
        """Get a specific category by ID"""
        try:
            category_service = CategoryService()
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            category = category_service.get_category_by_id(category_id, include_deleted=include_deleted)
            
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
            logger.error(f"Error getting category {category_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def put(self, request, category_id):
        """Update a category"""
        try:
            logger.info(f"Updating category {category_id} by user: {request.current_user['username']}")
            
            category_service = CategoryService()
            
            # Extract update data (only include fields that are present)
            update_data = {}
            allowed_fields = ['category_name', 'description', 'status', 'sub_categories'] + \
                           ['image_url', 'image_filename', 'image_size', 'image_type', 'image_uploaded_at']
            
            for field in allowed_fields:
                if field in request.data:
                    update_data[field] = request.data[field]
            
            if not update_data:
                return Response(
                    {"error": "No valid fields to update"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update category
            result = category_service.update_category(category_id, update_data, request.current_user)
            
            if not result:
                return Response(
                    {"error": "Category not found or no changes made"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category updated successfully",
                "category": result,
                "updated_by": request.current_user['username']
            }, status=status.HTTP_200_OK)

        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating category {category_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def delete(self, request, category_id):
        """Remove a subcategory from a category"""
        try:
            logger.info(f"Removing subcategory from {category_id} by user: {request.current_user['username']}")
            
            category_service = CategoryService()
            subcategory_name = request.data.get('subcategory_name')
            
            if not subcategory_name:
                return Response(
                    {"error": "Subcategory name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.remove_subcategory(
                category_id, 
                subcategory_name, 
                request.current_user
            )
            
            if not result:
                return Response(
                    {"error": "Failed to remove subcategory or category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory removed successfully",
                "removed_by": request.current_user['username']
            }, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error removing subcategory: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ================ DELETE MANAGEMENT VIEWS ================

class CategoryHardDeleteView(APIView):
    
    @require_admin
    def delete(self, request, category_id):
        """Hard delete a category (Admin only)"""
        try:
            logger.warning(f"Hard deleting category {category_id} by admin: {request.current_user['username']}")
            
            category_service = CategoryService()
            
            result = category_service.hard_delete_category(category_id, request.current_user)
            
            if not result:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category permanently deleted",
                "category_id": category_id,
                "action": "hard_delete",
                "warning": "This action cannot be undone",
                "deleted_by": request.current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error hard deleting category {category_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryRestoreView(APIView):
    
    @require_admin
    def post(self, request, category_id):
        """Restore a soft-deleted category (Admin only)"""
        try:
            logger.info(f"Restoring category {category_id} by admin: {request.current_user['username']}")
            
            category_service = CategoryService()
            result = category_service.restore_category(category_id, request.current_user)
            
            if not result:
                return Response(
                    {"error": "Category not found or not deleted"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category restored successfully",
                "category_id": category_id,
                "action": "restore",
                "restored_by": request.current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error restoring category {category_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryDeletedListView(APIView):
    
    @require_admin
    def get(self, request):
        """Get list of soft-deleted categories (Admin only)"""
        try:
            category_service = CategoryService()
            deleted_categories = category_service.get_deleted_categories()
            
            return Response({
                "message": "Deleted categories retrieved successfully",
                "categories": deleted_categories,
                "count": len(deleted_categories)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting deleted categories: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CategoryBulkOperationsView(APIView):
    
    @require_authentication
    def post(self, request):
        """Bulk operations on categories"""
        try:
            operation = request.data.get('operation')
            category_ids = request.data.get('category_ids', [])
            
            if not operation:
                return Response(
                    {"error": "Operation type is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not category_ids:
                return Response(
                    {"error": "Category IDs are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            category_service = CategoryService()
            
            if operation == 'soft_delete':
                result = category_service.bulk_soft_delete_categories(category_ids, request.current_user)
            elif operation == 'update_status':
                new_status = request.data.get('new_status')
                if not new_status:
                    return Response(
                        {"error": "new_status is required for status update"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                result = category_service.bulk_update_categories_status(
                    category_ids, 
                    new_status, 
                    request.current_user
                )
            else:
                return Response(
                    {"error": f"Unknown operation: {operation}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                "message": f"Bulk {operation} completed",
                "result": result,
                "performed_by": request.current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error in bulk operations: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ================ SUBCATEGORY VIEWS ================

class CategorySubcategoryView(APIView):
    
    @require_authentication
    def post(self, request, category_id):
        """Add a subcategory to a category"""
        try:
            logger.info(f"Adding subcategory to {category_id} by user: {request.current_user['username']}")
            
            category_service = CategoryService()
            subcategory_data = request.data.get('subcategory')
            
            if not subcategory_data:
                return Response(
                    {"error": "Subcategory data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.add_subcategory(
                category_id, 
                subcategory_data, 
                request.current_user
            )
            
            if not result:
                return Response(
                    {"error": "Failed to add subcategory or category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory added successfully",
                "added_by": request.current_user['username']
            }, status=status.HTTP_201_CREATED)
        
        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding subcategory: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def delete(self, request, category_id):
        """Remove a subcategory from a category"""
        try:
            logger.info(f"Removing subcategory from {category_id} by user: {request.current_user['username']}")
            
            category_service = CategoryService()
            subcategory_name = request.data.get('subcategory_name')
            
            if not subcategory_name:
                return Response(
                    {"error": "Subcategory name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.remove_subcategory(
                category_id, 
                subcategory_name, 
                request.current_user
            )
            
            if not result:
                return Response(
                    {"error": "Failed to remove subcategory or category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory removed successfully",
                "removed_by": request.current_user['username']
            }, status=status.HTTP_200_OK)
        
        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error removing subcategory: {e}")
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
            logger.error(f"Error getting subcategories: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ================ DISPLAY AND EXPORT VIEWS ================

class CategoryDataView(APIView):
    """Get categories with sales data"""
    
    def get(self, request):
        """Get all categories with sales data"""
        try:
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'
            
            category_service = CategoryDisplayService()
            result = category_service.get_categories_display(include_deleted=include_deleted)
            
            return Response({
                "categories": result,
                "count": len(result),
                "include_deleted": include_deleted
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in CategoryDataView: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@method_decorator(csrf_exempt, name='dispatch')
class CategoryExportView(APIView):
    """Export categories in CSV or JSON format"""
    
    def get(self, request):
        """Export categories with optional filters"""
        try:
            # Get query parameters
            format_type = request.GET.get('format', 'csv').lower()
            include_sales_data = request.GET.get('include_sales_data', 'true').lower() == 'true'
            include_deleted = request.GET.get('include_deleted', 'false').lower() == 'true'
            
            logger.info(f"Export request: format={format_type}, include_sales_data={include_sales_data}, include_deleted={include_deleted}")
            
            # Validate format
            if format_type not in ['csv', 'json']:
                return JsonResponse({
                    'error': 'Invalid format. Use csv or json.'
                }, status=400)
            
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
            
            # Initialize service and validate parameters
            category_service = CategoryDisplayService()
            category_service.validate_export_params(
                format_type, 
                include_sales_data, 
                date_filter, 
                include_deleted
            )
            
            # Export data based on format
            if format_type == 'csv':
                export_result = category_service.export_categories_csv(
                    include_sales_data=include_sales_data,
                    date_filter=date_filter,
                    include_deleted=include_deleted
                )
            else:  # json
                export_result = category_service.export_categories_json(
                    include_sales_data=include_sales_data,
                    date_filter=date_filter,
                    include_deleted=include_deleted
                )
            
            logger.info(f"Export successful: {export_result['filename']}, {export_result['total_records']} records")
            
            # Create response with proper headers
            response = HttpResponse(
                export_result['content'],
                content_type=export_result['content_type']
            )
            
            # Set download headers
            response['Content-Disposition'] = f'attachment; filename="{export_result["filename"]}"'
            response['Content-Length'] = len(export_result['content'])
            response['X-Total-Records'] = export_result['total_records']
            response['X-Include-Deleted'] = str(include_deleted)
            
            # Add CORS headers
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length, X-Total-Records, X-Include-Deleted'
            
            return response
            
        except ValueError as ve:
            return JsonResponse({'error': str(ve)}, status=400)
        except Exception as e:
            logger.error(f"Error in CategoryExportView: {e}")
            return JsonResponse({
                'error': f'Export failed: {str(e)}',
                'details': 'Check server logs for more information'
            }, status=500)


class CategoryStatsView(APIView):
    """Get category statistics"""
    
    def get(self, request):
        """Get comprehensive category statistics"""
        try:
            category_service = CategoryService()
            stats = category_service.get_category_stats()
            
            return Response({
                'success': True,
                'message': 'Category statistics retrieved successfully',
                'stats': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting category stats: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ================ PRODUCT SUBCATEGORY VIEWS ================

class ProductSubcategoryUpdateView(APIView):
    
    @require_authentication
    def put(self, request):
        """Update product subcategory"""
        try:
            logger.info(f"Updating product subcategory by user: {request.current_user['username']}")
            
            # Extract and validate data
            product_id = request.data.get('product_id')
            new_subcategory = request.data.get('new_subcategory')
            category_id = request.data.get('category_id')
            
            if not product_id or not category_id:
                return Response(
                    {"error": "product_id and category_id are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize service and validate
            service = ProductSubcategoryService()
            validation = service.validate_subcategory_update(product_id, new_subcategory, category_id)
            
            if not validation.get('is_valid'):
                return Response(
                    {"error": validation.get('error')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Perform update
            result = service.update_product_subcategory(
                product_id, 
                new_subcategory, 
                category_id,
                current_user=request.current_user
            )
            
            if result.get('success'):
                return Response({
                    "message": result.get('message'),
                    "result": result,
                    "updated_by": request.current_user['username']
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": result.get('message', 'Update failed')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error updating product subcategory: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductMoveToUncategorizedView(APIView):
    
    @require_authentication
    def put(self, request):
        """Move a product to Uncategorized category"""
        try:
            logger.info(f"Moving product to uncategorized by user: {request.current_user['username']}")
            
            product_id = request.data.get('product_id')
            current_category_id = request.data.get('current_category_id')
            
            if not product_id:
                return Response(
                    {"error": "product_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            service = ProductSubcategoryService()
            
            # FIXED: Use the public method instead of private method
            result = service.move_product_to_uncategorized_category(
                product_id=product_id,
                current_category_id=current_category_id
            )
            
            if result.get('success'):
                return Response({
                    "message": "Product moved to Uncategorized category successfully",
                    "product_id": product_id,
                    "result": result,
                    "moved_by": request.current_user['username']
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": result.get('error', 'Move to uncategorized failed')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            logger.error(f"Error moving product to uncategorized: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductBulkMoveToUncategorizedView(APIView):
    
    @require_authentication
    def put(self, request):
        """Bulk move products to Uncategorized category"""
        try:
            logger.info(f"Bulk moving products to uncategorized by user: {request.current_user['username']}")
            
            product_ids = request.data.get('product_ids', [])
            current_category_id = request.data.get('current_category_id')
            
            if not product_ids or not isinstance(product_ids, list):
                return Response(
                    {"error": "product_ids array is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if len(product_ids) == 0:
                return Response(
                    {"error": "At least one product_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            service = ProductSubcategoryService()
            result = service.bulk_move_products_to_uncategorized(
                product_ids, 
                current_category_id
            )
            
            # Determine response status based on results
            if result.get('successful', 0) > 0 and result.get('failed', 0) == 0:
                response_status = status.HTTP_200_OK
            elif result.get('successful', 0) > 0 and result.get('failed', 0) > 0:
                response_status = status.HTTP_207_MULTI_STATUS
            else:
                response_status = status.HTTP_400_BAD_REQUEST
            
            return Response({
                "message": result.get('message'),
                "result": result,
                "moved_by": request.current_user['username']
            }, status=response_status)
        
        except Exception as e:
            logger.error(f"Error bulk moving products: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# ================ UTILITY VIEWS ================

class CategoryDeleteInfoView(APIView):
    """Get information about category before deletion"""
    
    def get(self, request, category_id):
        """Get category deletion impact information"""
        try:
            category_service = CategoryService()
            delete_info = category_service.get_category_delete_info(category_id)
            
            if not delete_info:
                return Response(
                    {"error": "Category not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category delete information retrieved successfully",
                "delete_info": delete_info
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting category delete info: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UncategorizedCategoryView(APIView):
    """Manage the special 'Uncategorized' category"""
    
    def get(self, request):
        """Get information about the Uncategorized category"""
        try:
            service = ProductSubcategoryService()
            uncategorized_category = service._ensure_uncategorized_category_exists()
            
            return Response({
                "message": "Uncategorized category information retrieved successfully",
                "uncategorized_category": uncategorized_category
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting uncategorized category info: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_admin
    def post(self, request):
        """Create/ensure the Uncategorized category exists (Admin only)"""
        try:
            logger.info(f"Ensuring uncategorized category by admin: {request.current_user['username']}")
            
            service = ProductSubcategoryService()
            category = service._ensure_uncategorized_category_exists()
            
            return Response({
                "message": "Uncategorized category ensured successfully",
                "category": category,
                "ensured_by": request.current_user['username']
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error ensuring uncategorized category: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductToSubcategoryView(APIView):
    """Assign products to subcategories"""
    
    @require_authentication
    def post(self, request):
        """Add product to subcategory (for imports and manual assignments)"""
        try:
            logger.info(f"Adding product to subcategory by user: {request.current_user['username']}")
            
            # Extract data
            category_id = request.data.get('category_id')
            subcategory_name = request.data.get('subcategory_name')
            product_identifier = request.data.get('product_identifier')  # Can be ID or name
            
            if not all([category_id, subcategory_name, product_identifier]):
                return Response(
                    {"error": "category_id, subcategory_name, and product_identifier are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Use CategoryService to add product
            category_service = CategoryService()
            result = category_service.add_product_to_subcategory(
                category_id, 
                subcategory_name, 
                product_identifier, 
                request.current_user
            )
            
            if result.get('success'):
                return Response({
                    "message": result.get('message'),
                    "result": result,
                    "added_by": request.current_user['username']
                }, status=status.HTTP_201_CREATED)
            else:
                return Response(
                    {"error": result.get('message', 'Failed to add product to subcategory')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except ValueError as ve:
            return Response(
                {"error": str(ve)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error adding product to subcategory: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @require_authentication
    def delete(self, request, category_id):
        """Soft delete a category"""
        try:
            logger.info(f"Soft deleting category {category_id} by user: {request.current_user['username']}")
            
            category_service = CategoryService()
            deletion_context = request.data.get('deletion_context', 'user_initiated_deletion')
            
            result = category_service.soft_delete_category(
                category_id, 
                request.current_user, 
                deletion_context
            )
            
            if not result:
                return Response(
                    {"error": "Category not found or already deleted"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category soft deleted successfully",
                "category_id": category_id,
                "action": "soft_delete",
                "can_restore": True,
                "deleted_by": request.current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error soft deleting category {category_id}: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SubcategoryProductsView(APIView):
    """Get products in a subcategory with details"""
    
    def get(self, request, category_id, subcategory_name):
        """Get all products in a subcategory with full details"""
        try:
            category_service = CategoryService()
            products = category_service.get_subcategory_products_with_details(
                category_id, 
                subcategory_name
            )
            
            return Response({
                "message": "Subcategory products retrieved successfully",
                "category_id": category_id,
                "subcategory_name": subcategory_name,
                "products": products,
                "count": len(products)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting subcategory products: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )