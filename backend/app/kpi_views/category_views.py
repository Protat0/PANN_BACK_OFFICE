from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.category_service import CategoryService, CategoryDisplayService, ProductSubcategoryService
import logging
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
from datetime import datetime

#====JWT HELPER==== 
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
        
        # Get full user document from database to check username
        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            return None
        
        # Determine the best username to use
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

# ================ CATEGORY VIEWS ================

class CategoryKPIView(APIView):
    def post(self, request):
        """Category Creation with JWT token authentication"""
        print("🚀🚀🚀 CategoryKPIView.post() WAS CALLED! 🚀🚀🚀")
        
        # ✅ Debug: Check what headers we're receiving
        print(f"🔍 REQUEST HEADERS:")
        for key, value in request.headers.items():
            if 'auth' in key.lower():
                print(f"  {key}: {value[:50]}..." if len(str(value)) > 50 else f"  {key}: {value}")
        
        try:
            category_service = CategoryService()
            
            # Extract category data from request
            category_name = request.data.get('category_name')
            description = request.data.get('description', '')
            status_value = request.data.get('status', 'active')
            sub_categories = request.data.get('sub_categories', [])
            
            # Extract image fields
            image_url = request.data.get('image_url')
            image_filename = request.data.get('image_filename')
            image_size = request.data.get('image_size')
            image_type = request.data.get('image_type')
            image_uploaded_at = request.data.get('image_uploaded_at')
            
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
            
            # Include image fields if they exist
            if image_url:
                category_data.update({
                    'image_url': image_url,
                    'image_filename': image_filename,
                    'image_size': image_size,
                    'image_type': image_type,
                    'image_uploaded_at': image_uploaded_at
                })

            # ✅ FIXED: Get user data from JWT token instead of request.user
            current_user = None
            
            try:
                authorization = request.headers.get("Authorization")
                if authorization and authorization.startswith("Bearer "):
                    token = authorization.split(" ")[1]
                    
                    from ..services.auth_services import AuthService
                    auth_service = AuthService()
                    
                    user_data = auth_service.get_current_user(token)
                    print(f"🔍 User data from token: {user_data}")
                    
                    if user_data:
                        user_id = user_data.get('user_id')
                        print(f"🔍 Getting full user data for user_id: {user_id}")
                        
                        # ✅ FIXED: Get the full user document from database to check username
                        from bson import ObjectId
                        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
                        
                        if user_doc:
                            print(f"🔍 Full user document fields: {list(user_doc.keys())}")
                            print(f"🔍 username field: {user_doc.get('username')}")
                            print(f"🔍 email field: {user_doc.get('email')}")
                            
                            # ✅ FIXED: Use actual username from database if it exists
                            actual_username = user_doc.get('username')
                            if actual_username and actual_username.strip():
                                display_username = actual_username
                                print(f"✅ Using database username: {display_username}")
                            else:
                                display_username = user_doc.get('email', 'unknown')
                                print(f"✅ No username found, using email: {display_username}")
                            
                            # ✅ Build current_user with proper username
                            current_user = {
                                "user_id": user_id,
                                "username": display_username,  # Use the actual username or email fallback
                                "email": user_doc.get('email'),
                                "branch_id": 1,
                                "role": user_doc.get('role', 'admin'),
                                "ip_address": request.META.get('REMOTE_ADDR'),
                                "user_agent": request.META.get('HTTP_USER_AGENT')
                            }
                            
                            print(f"✅ FINAL CURRENT_USER:")
                            print(f"  user_id: '{current_user['user_id']}'")
                            print(f"  username: '{current_user['username']}'")
                            print(f"  email: '{current_user['email']}'")
                            
                        else:
                            print(f"❌ Could not find user document in database")
                            return Response(
                                {"error": "User not found"}, 
                                status=status.HTTP_401_UNAUTHORIZED
                            )
                    else:
                        print(f"❌ Could not get user data from token")
                        return Response(
                            {"error": "Invalid token"}, 
                            status=status.HTTP_401_UNAUTHORIZED
                        )
                else:
                    print(f"❌ No Authorization header")
                    return Response(
                        {"error": "Authorization required"}, 
                        status=status.HTTP_401_UNAUTHORIZED
                    )
                    
            except Exception as auth_error:
                print(f"❌ Authentication error: {auth_error}")
                return Response(
                    {"error": "Authentication failed"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Create category with proper username
            print(f"🚀 Creating category with username: {current_user['username']}")
            result = category_service.create_category(category_data, current_user)
            
            return Response({
                "message": "Category created successfully",
                "category": result,
                "created_by": current_user['username']  # Show who created it
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """Get all categories or search categories"""
        try:
            category_service = CategoryService()
            
            # Check query parameters
            search_term = request.query_params.get('search')
            active_only = request.query_params.get('active_only', 'false').lower() == 'true'
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'  # NEW
            
            if search_term:
                categories = category_service.search_categories(search_term, include_deleted=include_deleted)
            elif active_only:
                categories = category_service.get_active_categories(include_deleted=include_deleted)
            else:
                categories = category_service.get_all_categories(include_deleted=include_deleted)
            
            return Response({
                "message": "Categories retrieved successfully",
                "categories": categories,
                "count": len(categories),
                "include_deleted": include_deleted  # NEW: Include this info in response
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
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'  # NEW
            
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
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, category_id):
        """Update a category with JWT authentication"""
        print("🚀🚀🚀 CategoryDetailView.put() - UPDATE CATEGORY! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for UPDATE: {current_user['username']}")
            
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
            
            # Handle image fields
            if 'image_url' in request.data:
                update_data['image_url'] = request.data['image_url']
            if 'image_filename' in request.data:
                update_data['image_filename'] = request.data['image_filename']
            if 'image_size' in request.data:
                update_data['image_size'] = request.data['image_size']
            if 'image_type' in request.data:
                update_data['image_type'] = request.data['image_type']
            if 'image_uploaded_at' in request.data:
                update_data['image_uploaded_at'] = request.data['image_uploaded_at']
            
            # Handle image removal
            if 'image_url' in request.data and request.data['image_url'] is None:
                print("🗑️ IMAGE: Removing image from category")
                update_data['image_url'] = None
                update_data['image_filename'] = None
                update_data['image_size'] = None
                update_data['image_type'] = None
                update_data['image_uploaded_at'] = None
            
            if not update_data:
                return Response(
                    {"error": "No valid fields to update"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🚀 Updating category {category_id} with user: {current_user['username']}")
            result = category_service.update_category(category_id, update_data, current_user)
            
            if not result:
                return Response(
                    {"error": "Category not found or no changes made"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category updated successfully",
                "category": result,
                "updated_by": current_user['username']
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"❌ Error updating category: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, category_id):
        """Soft delete a category with JWT authentication"""
        print("🚀🚀🚀 CategoryDetailView.delete() - SOFT DELETE! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for SOFT DELETE: {current_user['username']}")
            
            category_service = CategoryService()
            print(f"🚀 Soft deleting category {category_id} with user: {current_user['username']}")
            result = category_service.soft_delete_category(category_id, current_user)
            
            if not result:
                return Response(
                    {"error": "Category not found or already deleted"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category soft deleted successfully",
                "action": "soft_delete",
                "deleted_by": current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ Error soft deleting category: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================ NEW DELETE VIEWS ================

class CategorySoftDeleteView(APIView):
    """Soft delete operations for categories"""
    
    def delete(self, request, category_id):
        """Soft delete a category with JWT authentication"""
        print("🚀🚀🚀 CategorySoftDeleteView.delete() - SOFT DELETE! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for SOFT DELETE: {current_user['username']}")
            
            category_service = CategoryService()
            print(f"🚀 Soft deleting category {category_id} with user: {current_user['username']}")
            result = category_service.soft_delete_category(category_id, current_user)
                        
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
                "deleted_by": current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ Error soft deleting category: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Bulk soft delete categories"""
        try:
            category_service = CategoryService()
            category_ids = request.data.get('category_ids', [])
            
            if not category_ids:
                return Response(
                    {"error": "Category IDs are required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            result = category_service.bulk_soft_delete_categories(category_ids)
            
            return Response({
                "message": f"Bulk soft delete completed",
                "result": result
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryHardDeleteView(APIView):
    """Hard delete operations for categories (Admin only)"""
    
    def delete(self, request, category_id):
        """Hard delete a category with JWT authentication (Admin only)"""
        print("🚀🚀🚀 CategoryHardDeleteView.delete() - HARD DELETE! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required for hard delete"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            print(f"✅ Authenticated ADMIN user for HARD DELETE: {current_user['username']}")
            
            category_service = CategoryService()
            admin_user_id = current_user.get('user_id')
            
            print(f"🚀 Hard deleting category {category_id} with admin: {current_user['username']}")
            result = category_service.hard_delete_category(
                category_id, 
                admin_user_id=admin_user_id, 
                current_user=current_user
            )
            
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
                "deleted_by": current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ Error hard deleting category: {str(e)}")
            return Response(
                {"error": str(e)}, 
               status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryRestoreView(APIView):
    """Restore soft-deleted categories"""
    
    def post(self, request, category_id):
        """Restore a soft-deleted category"""
        try:
            category_service = CategoryService()
            result = category_service.restore_category(category_id)
            
            if not result:
                return Response(
                    {"error": "Category not found or not deleted"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Category restored successfully",
                "category": result,
                "action": "restore"
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategoryDeletedListView(APIView):
    """Get list of soft-deleted categories (for admin recovery)"""
    
    def get(self, request):
        """Get all soft-deleted categories"""
        try:
            category_service = CategoryService()
            deleted_categories = category_service.get_deleted_categories()
            
            return Response({
                "message": "Deleted categories retrieved successfully",
                "categories": deleted_categories,
                "count": len(deleted_categories)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

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
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================ EXISTING VIEWS (Updated) ================

class CategorySubcategoryView(APIView):
    def post(self, request, category_id):
        """Add a subcategory to a category with JWT authentication"""
        print("🚀🚀🚀 CategorySubcategoryView.post() - ADD SUBCATEGORY! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for ADD SUBCATEGORY: {current_user['username']}")
            
            category_service = CategoryService()
            subcategory_data = request.data.get('subcategory')
            
            if not subcategory_data:
                return Response(
                    {"error": "Subcategory data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🚀 Adding subcategory to {category_id} with user: {current_user['username']}")
            result = category_service.add_subcategory(category_id, subcategory_data, current_user)
            
            if not result:
                return Response(
                    {"error": "Failed to add subcategory or category not found/deleted"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory added successfully",
                "added_by": current_user['username']
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            print(f"❌ Error adding subcategory: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request, category_id):
        """Remove a subcategory from a category with JWT authentication"""
        print("🚀🚀🚀 CategorySubcategoryView.delete() - REMOVE SUBCATEGORY! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for REMOVE SUBCATEGORY: {current_user['username']}")
            
            category_service = CategoryService()
            subcategory_data = request.data.get('subcategory')
            
            if not subcategory_data:
                return Response(
                    {"error": "Subcategory data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🚀 Removing subcategory from {category_id} with user: {current_user['username']}")
            result = category_service.remove_subcategory(category_id, subcategory_data, current_user)
            
            if not result:
                return Response(
                    {"error": "Failed to remove subcategory or category not found/deleted"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Subcategory removed successfully",
                "removed_by": current_user['username']
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"❌ Error removing subcategory: {str(e)}")
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
            # Check query parameters
            include_deleted = request.query_params.get('include_deleted', 'false').lower() == 'true'  # NEW
            
            category_service = CategoryDisplayService()
            result = category_service.get_categories_display(include_deleted=include_deleted)
            
            return Response({
                "categories": result,
                "count": len(result),
                "include_deleted": include_deleted  # NEW: Include this info
            }, status=status.HTTP_200_OK)
            
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
            include_deleted = request.GET.get('include_deleted', 'false').lower() == 'true'  # NEW
            
            print(f"🚀 Export request: format={format_type}, include_sales_data={include_sales_data}, include_deleted={include_deleted}")
            
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
                print(f"📅 Date filter applied: {date_filter}")
            
            # Initialize service
            category_service = CategoryDisplayService()
            
            # Validate export parameters first
            try:
                category_service.validate_export_params(format_type, include_sales_data, date_filter, include_deleted)
            except Exception as validation_error:
                print(f"❌ Validation error: {validation_error}")
                return JsonResponse({
                    'error': f'Invalid parameters: {str(validation_error)}'
                }, status=400)
            
            # Export data based on format
            if format_type == 'csv':
                export_result = category_service.export_categories_csv(
                    include_sales_data=include_sales_data,
                    date_filter=date_filter,
                    include_deleted=include_deleted  # NEW
                )
            else:  # json
                export_result = category_service.export_categories_json(
                    include_sales_data=include_sales_data,
                    date_filter=date_filter,
                    include_deleted=include_deleted  # NEW
                )
            
            print(f"✅ Export successful: {export_result['filename']}, {export_result['total_records']} records")
            
            # Create response with proper headers
            response = HttpResponse(
                export_result['content'],
                content_type=export_result['content_type']
            )
            
            # Set download headers
            response['Content-Disposition'] = f'attachment; filename="{export_result["filename"]}"'
            response['Content-Length'] = len(export_result['content'])
            response['X-Total-Records'] = export_result['total_records']
            response['X-Include-Deleted'] = str(include_deleted)  # NEW
            
            # Add CORS headers for frontend
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition, Content-Length, X-Total-Records, X-Include-Deleted'
            
            return response
            
        except Exception as e:
            print(f"❌ Error in CategoryExportView: {e}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            
            # Return JSON error response
            return JsonResponse({
                'error': f'Export failed: {str(e)}',
                'details': 'Check server logs for more information'
            }, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class CategoryExportStatsView(APIView):
    """Get export statistics for categories"""
    
    def get(self, request):
        try:
            include_deleted = request.GET.get('include_deleted', 'false').lower() == 'true'  # NEW
            
            category_service = CategoryDisplayService()
            stats = category_service.get_export_stats(include_deleted=include_deleted)
            
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

# ================ PRODUCT SUBCATEGORY VIEWS ================

class ProductSubcategoryUpdateView(APIView):
    """Update product subcategory within a category"""
    
    def put(self, request):
        """Update product subcategory with JWT authentication"""
        print("🚀🚀🚀 ProductSubcategoryUpdateView.put() - UPDATE PRODUCT SUBCATEGORY! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for UPDATE PRODUCT SUBCATEGORY: {current_user['username']}")
            
            # Extract data from request
            product_id = request.data.get('product_id')
            new_subcategory = request.data.get('new_subcategory')
            category_id = request.data.get('category_id')
            
            # Validate required fields
            if not product_id:
                return Response(
                    {"error": "product_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not category_id:
                return Response(
                    {"error": "category_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize service
            service = ProductSubcategoryService()
            
            # Validate the update first
            validation = service.validate_subcategory_update(product_id, new_subcategory, category_id)
            
            if not validation.get('is_valid'):
                return Response(
                    {"error": validation.get('error')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            print(f"🚀 Updating product {product_id} subcategory with user: {current_user['username']}")
            # Perform the update with current_user for audit logging
            result = service.update_product_subcategory(
                product_id, 
                new_subcategory, 
                category_id, 
                current_user=current_user  # Pass user for audit logging
            )
            
            if result.get('success'):
                return Response({
                    "message": result.get('message'),
                    "result": result,
                    "updated_by": current_user['username']
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": result.get('message', 'Update failed')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            print(f"❌ Error updating product subcategory: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductCategoryInfoView(APIView):
    """Get product's current category and subcategory information"""
    
    def get(self, request, product_id):
        """Get current category/subcategory info for a product"""
        try:
            
            service = ProductSubcategoryService()
            info = service.get_product_category_info(product_id)
            
            if not info:
                return Response(
                    {"error": "Product not found in any category"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            return Response({
                "message": "Product category information retrieved successfully",
                "info": info
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class CategorySubcategoriesListView(APIView):
    """Get available subcategories for a category"""
    
    def get(self, request, category_id):
        """Get list of available subcategories for a category"""
        try:
         
            
            service = ProductSubcategoryService()
            subcategories = service.get_available_subcategories(category_id)
            
            return Response({
                "message": "Available subcategories retrieved successfully",
                "subcategories": subcategories,
                "count": len(subcategories)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
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
            info = service.get_uncategorized_category_info()
            
            return Response({
                "message": "Uncategorized category information retrieved successfully",
                "uncategorized_category": info
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create/ensure the Uncategorized category exists"""
        try:
            service = ProductSubcategoryService()
            category = service.ensure_uncategorized_category_exists()
            
            return Response({
                "message": "Uncategorized category ensured successfully",
                "category": category
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MigrateUncategorizedProductsView(APIView):
    """One-time migration of existing uncategorized products"""
    
    def post(self, request):
        """Migrate all existing uncategorized products to the Uncategorized category"""
        try:
            service = ProductSubcategoryService()
            results = service.migrate_existing_uncategorized_products()
            
            return Response({
                "message": "Migration completed successfully",
                "migration_results": results
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class UncategorizedCategoryProductsView(APIView):
    """Get products in the Uncategorized category"""
    
    def get(self, request):
        """Get all products in the Uncategorized category"""
        try:
            service = ProductSubcategoryService()
            
            # Get uncategorized category info
            category_info = service.get_uncategorized_category_info()
            
            if not category_info.get('exists'):
                return Response({
                    "message": "Uncategorized category does not exist",
                    "products": [],
                    "count": 0
                }, status=status.HTTP_200_OK)
            
            # Get products using existing method but filter for uncategorized
            from ..services.category_service import CategoryService
            category_service = CategoryService()
            
            # Use the FindProdcategory method with uncategorized category ID
            products = category_service.FindProdcategory({
                'id': category_info['category_id']
            })
            
            return Response({
                "message": "Uncategorized products retrieved successfully",
                "products": products,
                "count": len(products),
                "category_info": category_info
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class ProductMoveToUncategorizedView(APIView):
    """Move a single product to Uncategorized category"""
    
    def put(self, request):
        """Move a product to Uncategorized category with JWT authentication"""
        print("🚀🚀🚀 ProductMoveToUncategorizedView.put() - MOVE TO UNCATEGORIZED! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for MOVE TO UNCATEGORIZED: {current_user['username']}")
            
            # Extract data from request
            product_id = request.data.get('product_id')
            current_category_id = request.data.get('current_category_id')
            
            # Validate required fields
            if not product_id:
                return Response(
                    {"error": "product_id is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Initialize service
            service = ProductSubcategoryService()
            UNCATEGORIZED_CATEGORY_ID = '686a4de143821e2b21f725c6'
            
            print(f"🚀 Moving product {product_id} to uncategorized with user: {current_user['username']}")
            result = service.update_product_subcategory(
                product_id=product_id,
                new_subcategory=None,  # null triggers move to uncategorized
                category_id=UNCATEGORIZED_CATEGORY_ID,
                current_user=current_user  # Pass user for audit logging
            )
            
            if result.get('success'):
                return Response({
                    "message": "Product moved to Uncategorized category successfully",
                    "product_id": product_id,
                    "previous_category_id": current_category_id,
                    "new_category_id": UNCATEGORIZED_CATEGORY_ID,
                    "result": result,
                    "moved_by": current_user['username']
                }, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": result.get('message', 'Move to uncategorized failed')}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except Exception as e:
            print(f"❌ Error moving product to uncategorized: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ProductBulkMoveToUncategorizedView(APIView):
    """Move multiple products to Uncategorized category"""
    
    def put(self, request):
        """Bulk move products to Uncategorized category with JWT authentication"""
        print("🚀🚀🚀 ProductBulkMoveToUncategorizedView.put() - BULK MOVE TO UNCATEGORIZED! 🚀🚀🚀")
        
        try:
            # ✅ Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            print(f"✅ Authenticated user for BULK MOVE TO UNCATEGORIZED: {current_user['username']}")
            
            # Extract data from request
            product_ids = request.data.get('product_ids', [])
            current_category_id = request.data.get('current_category_id')
            
            # Validate required fields
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
            
            # Initialize service
            service = ProductSubcategoryService()
            UNCATEGORIZED_CATEGORY_ID = '686a4de143821e2b21f725c6'
            
            print(f"🚀 Bulk moving {len(product_ids)} products to uncategorized with user: {current_user['username']}")
            
            # Process each product
            results = []
            successful = 0
            failed = 0
            
            for product_id in product_ids:
                try:
                    # Move each product to uncategorized
                    result = service.update_product_subcategory(
                        product_id=product_id,
                        new_subcategory=None,  # null triggers move to uncategorized
                        category_id=UNCATEGORIZED_CATEGORY_ID,
                        current_user=current_user  # Pass user for audit logging
                    )
                    
                    if result.get('success'):
                        successful += 1
                        results.append({
                            "product_id": product_id,
                            "status": "success",
                            "message": "Moved to uncategorized successfully"
                        })
                    else:
                        failed += 1
                        results.append({
                            "product_id": product_id,
                            "status": "failed",
                            "error": result.get('message', 'Unknown error')
                        })
                        
                except Exception as e:
                    failed += 1
                    results.append({
                        "product_id": product_id,
                        "status": "failed",
                        "error": str(e)
                    })
            
            # Determine response status
            if successful > 0 and failed == 0:
                response_status = status.HTTP_200_OK
            elif successful > 0 and failed > 0:
                response_status = status.HTTP_207_MULTI_STATUS
            else:
                response_status = status.HTTP_400_BAD_REQUEST
            
            return Response({
                "message": f"Bulk move completed: {successful} successful, {failed} failed",
                "successful": successful,
                "failed": failed,
                "total_requested": len(product_ids),
                "previous_category_id": current_category_id,
                "new_category_id": UNCATEGORIZED_CATEGORY_ID,
                "results": results,
                "moved_by": current_user['username']
            }, status=response_status)
        
        except Exception as e:
            print(f"❌ Error bulk moving products: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )