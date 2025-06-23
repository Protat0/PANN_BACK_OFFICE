from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from ..services.category_service import CategoryService
import logging


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


