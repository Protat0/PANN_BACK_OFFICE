# views/promotion_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from bson import ObjectId
from ..services.promotions_service import PromotionService
import logging

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
        user_doc = auth_service.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_doc:
            return None
        
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

class PromotionHealthCheckView(APIView):
    def get(self, request):
        return Response({
            "message": "Promotion Management API is running!",
            "status": "active",
            "version": "1.0.0"
        }, status=status.HTTP_200_OK)

class PromotionListView(APIView):
    def get(self, request):
        """Get all promotions - ENHANCED with database debugging"""
        try:
            promotion_service = PromotionService()
            
            # Check if include_deleted parameter is passed
            include_deleted = request.GET.get('include_deleted', 'false').lower() == 'true'
            print(f"🔍 PromotionListView - include_deleted parameter: {include_deleted}")
            
            # DEBUG: Check database directly first
            total_in_db = promotion_service.collection.count_documents({})
            deleted_in_db = promotion_service.collection.count_documents({'isDeleted': True})
            active_in_db = total_in_db - deleted_in_db
            
            print(f"🔍 Database stats - Total: {total_in_db}, Active: {active_in_db}, Deleted: {deleted_in_db}")
            
            # DEBUG: Look for the specific promotion you showed me
            target_promo = promotion_service.collection.find_one({
                '_id': ObjectId('687e7b79d892409de86ea4e4')
            })
            
            if target_promo:
                print(f"🔍 Found target promotion 'ter': isDeleted={target_promo.get('isDeleted')}, status={target_promo.get('status')}")
            else:
                print("❌ Target promotion '687e7b79d892409de86ea4e4' not found in database!")
            
            # Get promotions with the include_deleted flag
            promotions = promotion_service.get_all_promotions(include_deleted=include_deleted)
            
            print(f"🔍 PromotionListView - returned {len(promotions)} promotions")
            
            # Debug: show info about returned promotions
            for i, promo in enumerate(promotions):
                print(f"🔍 Returned promotion {i+1}: {promo.get('promotion_name')} - isDeleted: {promo.get('isDeleted')} - status: {promo.get('status')}")
            
            return Response(promotions, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"❌ Error in PromotionListView.get: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create new promotion - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            promotion_service = PromotionService()
            promotion_data = request.data
            
            # ✅ UPDATED: Pass current_user to service
            result = promotion_service.create_promotions(promotion_data, current_user)
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )

class PromotionDetailView(APIView):
    def get(self, request, promotion_id):
        """Get promotion by ID - No changes needed"""
        try:
            promotion_service = PromotionService()
            promotion = promotion_service.get_promotion_by_id(promotion_id)
            if promotion:
                return Response(promotion, status=status.HTTP_200_OK)
            return Response(
                {"error": "Promotion not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request, promotion_id):
        """Update promotion - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            promotion_service = PromotionService()
            promotion_data = request.data
            
            # ✅ UPDATED: Pass current_user to service
            result = promotion_service.update_promotion(promotion_id, promotion_data, current_user)
            
            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, promotion_id):
        """Delete promotion - UPDATED with JWT auth"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            promotion_service = PromotionService()
            
            # ✅ UPDATED: Pass current_user to service
            result = promotion_service.soft_delete_promotion(promotion_id, current_user)
            
            if result['success']:
                return Response(
                    {"message": "Promotion deleted successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromotionByNameView(APIView):
    def get(self, request, promotion_name):
        """Get promotion by name - No changes needed"""
        try:
            promotion_service = PromotionService()
            promotions = promotion_service.search_promotions(promotion_name)
            
            # Find exact match
            exact_match = [p for p in promotions if p.get('promotion_name', '').lower() == promotion_name.lower()]
            
            if exact_match:
                return Response(exact_match[0], status=status.HTTP_200_OK)
            return Response(
                {"error": "Promotion not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromotionRestoreView(APIView):
    def post(self, request, promotion_id):
        """Restore soft-deleted promotion"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            promotion_service = PromotionService()
            
            # ✅ UPDATED: Pass current_user to service
            result = promotion_service.restore_promotion(promotion_id, current_user)
            
            if result['success']:
                return Response(
                    {"message": "Promotion restored successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromotionDeletedListView(APIView):
    def get(self, request):
        """Get all soft-deleted promotions - Admin only"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            promotion_service = PromotionService()
            deleted_promotions = promotion_service.get_deleted_promotions()
            
            return Response(deleted_promotions, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromotionHardDeleteView(APIView):
    def delete(self, request, promotion_id):
        """Hard delete promotion - Admin only (PERMANENT)"""
        try:
            # ✅ ADD: Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # ✅ ADD: Check if user is admin
            if current_user.get('role', '').lower() != 'admin':
                return Response(
                    {"error": "Admin permissions required"}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            
            promotion_service = PromotionService()
            admin_user_id = current_user.get('user_id')
            
            # ✅ Call hard delete from your service
            result = promotion_service.hard_delete_promotion(promotion_id, admin_user_id, current_user)
            
            if result['success']:
                return Response(
                    {"message": "Promotion permanently deleted successfully"}, 
                    status=status.HTTP_200_OK
                )
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class PromotionDatabaseDebugView(APIView):
    def get(self, request):
        """Debug view to check what's actually in the database"""
        try:
            promotion_service = PromotionService()
            
            # Get RAW data directly from MongoDB
            all_promotions_raw = list(promotion_service.collection.find({}))
            
            debug_info = {
                'total_documents': len(all_promotions_raw),
                'database_name': promotion_service.db.name,
                'collection_name': promotion_service.collection.name,
                'promotions': []
            }
            
            for promo in all_promotions_raw:
                debug_info['promotions'].append({
                    '_id': str(promo['_id']),
                    'promotion_name': promo.get('promotion_name', 'N/A'),
                    'status': promo.get('status', 'N/A'),
                    'isDeleted': promo.get('isDeleted', 'MISSING'),
                    'deleted_at': str(promo.get('deleted_at', 'N/A')),
                    'all_fields': list(promo.keys())
                })
            
            # Specifically look for the deleted promotion
            target_promotion = promotion_service.collection.find_one({
                '_id': ObjectId('687e7b79d892409de86ea4e4')
            })
            
            debug_info['target_promotion_found'] = target_promotion is not None
            if target_promotion:
                debug_info['target_promotion'] = {
                    '_id': str(target_promotion['_id']),
                    'promotion_name': target_promotion.get('promotion_name'),
                    'status': target_promotion.get('status'),
                    'isDeleted': target_promotion.get('isDeleted'),
                    'deleted_at': str(target_promotion.get('deleted_at')),
                    'all_fields': list(target_promotion.keys())
                }
            
            # Count by deletion status
            deleted_count = promotion_service.collection.count_documents({'isDeleted': True})
            active_count = promotion_service.collection.count_documents({'isDeleted': {'$ne': True}})
            
            debug_info['counts'] = {
                'total': len(all_promotions_raw),
                'deleted': deleted_count,
                'active': active_count
            }
            
            return Response(debug_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )