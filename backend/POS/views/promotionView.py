from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from services.promotionCon import PromoConnection
import logging

def get_authenticated_user_from_jwt(request):
    """Helper function to get authenticated user with proper username from JWT token"""
    try:
        authorization = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        
        token = authorization.split(" ")[1]
        
        from ...app.services.auth_services import AuthService
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
            "role": user_doc.get('role', 'employee'),
            "ip_address": request.META.get('REMOTE_ADDR'),
            "user_agent": request.META.get('HTTP_USER_AGENT')
        }
        
    except Exception as e:
        print(f"JWT Auth helper error: {e}")
        return None

class POSTransactionView(APIView):
    """Handle complete POS transactions with promotions and inventory management"""
    
    def post(self, request):
        """Process a complete POS transaction"""
        try:
            # Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            promo_service = PromoConnection()
            
            # Extract required data
            checkout_data = request.data.get('checkout_data', [])
            promotion_name = request.data.get('promotion_name')
            cashier_id = current_user.get('user_id')  # Use authenticated user ID
            
            # Validate required fields
            if not checkout_data:
                return Response(
                    {"error": "Checkout data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate checkout items
            for i, item in enumerate(checkout_data):
                if not all(key in item for key in ['product_id', 'quantity', 'price']):
                    return Response(
                        {"error": f"Item {i+1} missing required fields: product_id, quantity, price"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Process the transaction
            result = promo_service.pos_transaction(
                checkout_data=checkout_data,
                promotion_name=promotion_name,
                cashier_id=cashier_id
            )
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logging.error(f"Error processing POS transaction: {str(e)}")
            return Response(
                {"error": f"Error processing transaction: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StockValidationView(APIView):
    """Validate stock availability before transaction"""
    
    def post(self, request):
        """Check if sufficient stock is available for checkout items"""
        try:
            promo_service = PromoConnection()
            checkout_data = request.data.get('checkout_data', [])
            
            if not checkout_data:
                return Response(
                    {"error": "Checkout data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate stock
            validation_result = promo_service.validate_stock_availability(checkout_data)
            
            return Response({
                "success": True,
                "validation": validation_result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error validating stock: {str(e)}")
            return Response(
                {"error": f"Error validating stock: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StockWarningsView(APIView):
    """Check for low stock warnings"""
    
    def post(self, request):
        """Get low stock warnings for checkout items"""
        try:
            # Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            promo_service = PromoConnection()
            checkout_data = request.data.get('checkout_data', [])
            
            if not checkout_data:
                return Response(
                    {"error": "Checkout data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get warnings
            warnings = promo_service.check_low_stock_warnings(checkout_data, current_user)
            
            return Response({
                "success": True,
                "warnings": warnings,
                "warnings_count": len(warnings)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error checking stock warnings: {str(e)}")
            return Response(
                {"error": f"Error checking stock warnings: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get all products with low stock"""
        try:
            promo_service = PromoConnection()
            low_stock_products = promo_service.check_all_low_stock_products()
            
            return Response({
                "success": True,
                "low_stock_products": low_stock_products,
                "count": len(low_stock_products)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error getting low stock products: {str(e)}")
            return Response(
                {"error": f"Error getting low stock products: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromotionCheckoutView(APIView):
    """Handle promotion application to checkout"""
    
    def post(self, request):
        """Apply promotion to checkout and calculate discounts"""
        try:
            promo_service = PromoConnection()
            checkout_data = request.data.get('checkout_data', [])
            promotion_name = request.data.get('promotion_name')
            
            if not checkout_data:
                return Response(
                    {"error": "Checkout data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if not promotion_name:
                return Response(
                    {"error": "Promotion name is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Apply promotion
            result = promo_service.checkout_list(checkout_data, promotion_name)
            
            return Response(result, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error applying promotion: {str(e)}")
            return Response(
                {"error": f"Error applying promotion: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class SalesTransactionView(APIView):
    """Handle individual sales transaction creation"""
    
    def post(self, request):
        """Create a sales transaction record"""
        try:
            # Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            promo_service = PromoConnection()
            sales_data = request.data
            
            # Add cashier_id from authenticated user
            sales_data['cashier_id'] = current_user.get('user_id')
            
            # Create sales record
            result = promo_service.create_sales(sales_data)
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logging.error(f"Error creating sales transaction: {str(e)}")
            return Response(
                {"error": f"Error creating sales transaction: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InventoryUpdateView(APIView):
    """Handle inventory updates after sales"""
    
    def post(self, request):
        """Update inventory after sale (reduce stock quantities)"""
        try:
            # Get authenticated user from JWT
            current_user = get_authenticated_user_from_jwt(request)
            
            if not current_user:
                return Response(
                    {"error": "Authentication required"}, 
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            promo_service = PromoConnection()
            checkout_data = request.data.get('checkout_data', [])
            
            if not checkout_data:
                return Response(
                    {"error": "Checkout data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update inventory
            promo_service.update_inventory(checkout_data)
            
            return Response({
                "success": True,
                "message": "Inventory updated successfully"
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error updating inventory: {str(e)}")
            return Response(
                {"error": f"Error updating inventory: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ReceiptGenerationView(APIView):
    """Generate receipt for completed transactions"""
    
    def post(self, request):
        """Generate receipt from sales record"""
        try:
            promo_service = PromoConnection()
            sales_record = request.data.get('sales_record')
            
            if not sales_record:
                return Response(
                    {"error": "Sales record is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Generate receipt
            receipt = promo_service.generate_receipt(sales_record)
            
            return Response({
                "success": True,
                "receipt": receipt
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Error generating receipt: {str(e)}")
            return Response(
                {"error": f"Error generating receipt: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class PromotionConnectionView(APIView):
    """Handle promotion-category connections"""
    
    def post(self, request):
        """Create promotion-category connection"""
        try:
            promo_service = PromoConnection()
            promotion_data = request.data
            
            if not promotion_data:
                return Response(
                    {"error": "Promotion data is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create promotion connection
            result = promo_service.promotion_product_category_connection(promotion_data)
            
            if result['success']:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logging.error(f"Error creating promotion connection: {str(e)}")
            return Response(
                {"error": f"Error creating promotion connection: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

# ================ POS KPI Views ================
class POSTransactionKPIView(APIView):
    """Get POS transaction statistics"""
    
    def get(self, request):
        try:
            promo_service = PromoConnection()
            
            # Get basic transaction count (you'll need to add this method to PromoConnection)
            # For now, returning a placeholder response
            return Response({
                "message": "POS Transaction KPI - Add get_transaction_statistics method to PromoConnection service",
                "total_transactions": 0,
                "daily_transactions": 0,
                "monthly_transactions": 0
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"POS Transaction KPI error: {str(e)}")
            print(f"POS Transaction KPI error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class InventoryKPIView(APIView):
    """Get inventory statistics"""
    
    def get(self, request):
        try:
            promo_service = PromoConnection()
            low_stock_products = promo_service.check_all_low_stock_products()
            
            return Response({
                "low_stock_count": len(low_stock_products),
                "low_stock_products": low_stock_products
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Inventory KPI error: {str(e)}")
            print(f"Inventory KPI error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class StockAlertKPIView(APIView):
    """Get stock alert statistics"""
    
    def get(self, request):
        try:
            promo_service = PromoConnection()
            low_stock_products = promo_service.check_all_low_stock_products()
            
            # Calculate KPIs
            total_products = promo_service.products_collection.count_documents({"isDeleted": {"$ne": True}})
            out_of_stock = promo_service.products_collection.count_documents({
                "stock": {"$lte": 0},
                "isDeleted": {"$ne": True}
            })
            low_stock_count = len(low_stock_products)
            
            return Response({
                "total_products": total_products,
                "out_of_stock": out_of_stock,
                "low_stock": low_stock_count,
                "stock_health_percentage": round(((total_products - low_stock_count) / total_products * 100), 2) if total_products > 0 else 0
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logging.error(f"Stock Alert KPI error: {str(e)}")
            print(f"Stock Alert KPI error: {str(e)}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

