from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..services.pos_category_display import POSCategoryService
import logging

logger = logging.getLogger(__name__)

# ================ POS CATEGORY VIEWS ================

class POSCatalogView(APIView):
    """Lightweight POS catalog for product selection"""
    
    def get(self, request):
        """Get POS catalog structure"""
        try:
            pos_service = POSCategoryService()  # Create instance directly
            catalog = pos_service.get_pos_catalog_structure()
            
            return Response({
                "message": "POS catalog retrieved successfully",
                "catalog": catalog,
                "count": len(catalog)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error getting POS catalog: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class POSProductBatchView(APIView):
    """Batch fetch products for POS cart"""
    
    def post(self, request):
        """Batch fetch multiple products by IDs for POS cart"""
        try:
            pos_service = POSCategoryService()  # Create instance directly
            product_ids = request.data.get('product_ids', [])
            
            if not product_ids or not isinstance(product_ids, list):
                return Response({"error": "product_ids array is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            products = pos_service.get_products_for_pos_cart(product_ids)
            
            return Response({
                "message": "Products retrieved successfully",
                "products": products,
                "count": len(products)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error batch fetching products: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class POSBarcodeView(APIView):
    """POS barcode scanning"""
    
    def get(self, request, barcode):
        """Get product by barcode for POS scanner"""
        try:
            pos_service = POSCategoryService()  # Create instance directly
            product = pos_service.get_product_by_barcode_for_pos(barcode)
            
            if not product:
                return Response({"error": "Product not found for barcode"}, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                "message": "Product found",
                "product": product,
                "barcode": barcode
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error barcode lookup: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class POSSearchView(APIView):
    """POS product search"""
    
    def get(self, request):
        """Search products for POS by name or code"""
        try:
            pos_service = POSCategoryService()  # Create instance directly
            search_term = request.query_params.get('q')
            limit = int(request.query_params.get('limit', 20))
            
            if not search_term or not search_term.strip():
                return Response({"error": "Search term 'q' is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            products = pos_service.search_products_for_pos(search_term, limit)
            
            return Response({
                "message": "Search completed",
                "search_term": search_term,
                "products": products,
                "count": len(products)
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error POS search: {e}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class POSSubcategoryProductsView(APIView):
    def get(self, request, category_id, subcategory_name):
        """Get all products in subcategory for POS"""
        try:
            pos_service = POSCategoryService()
            products = pos_service.get_products_by_subcategory_for_pos(category_id, subcategory_name)
            
            return Response({
                "message": "Subcategory products retrieved successfully",
                "products": products,
                "count": len(products)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class POSStockCheckView(APIView):
    def post(self, request):
        """Check product stock for POS"""
        try:
            pos_service = POSCategoryService()
            product_id = request.data.get('product_id')
            requested_quantity = request.data.get('quantity', 1)
            
            stock_status = pos_service.check_product_stock_for_pos(product_id, requested_quantity)
            
            return Response({"message": "Stock check completed", "stock_status": stock_status}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class POSLowStockView(APIView):
    def get(self, request):
        """Get low stock products for POS"""
        try:
            pos_service = POSCategoryService()
            threshold = int(request.query_params.get('threshold', 10))
            products = pos_service.get_low_stock_products_for_pos(threshold)
            
            return Response({
                "message": "Low stock products retrieved",
                "products": products,
                "count": len(products)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class POSStockCheckView(APIView):
    
    def post(self, request):
        """Check product stock before adding to cart"""
        try:
            pos_service = POSCategoryService()
            product_id = request.data.get('product_id')
            requested_quantity = request.data.get('quantity', 1)
            
            if not product_id:
                return Response({"error": "product_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            stock_status = pos_service.check_product_stock_for_pos(product_id, requested_quantity)
            
            return Response({
                "message": "Stock check completed",
                "stock_status": stock_status
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class POSLowStockView(APIView):
    
    def get(self, request):
        """Get products with low stock for POS alerts"""
        try:
            pos_service = POSCategoryService()
            threshold = int(request.query_params.get('threshold', 10))
            
            low_stock_products = pos_service.get_low_stock_products_for_pos(threshold)
            
            return Response({
                "message": "Low stock products retrieved",
                "threshold": threshold,
                "products": low_stock_products,
                "count": len(low_stock_products)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class POSSubcategoryProductsView(APIView):
    
    def get(self, request, category_id, subcategory_name):
        """Get all products in subcategory for bulk POS selection"""
        try:
            pos_service = POSCategoryService()
            products = pos_service.get_products_by_subcategory_for_pos(category_id, subcategory_name)
            
            return Response({
                "message": "Subcategory products retrieved successfully",
                "category_id": category_id,
                "subcategory_name": subcategory_name,
                "products": products,
                "count": len(products)
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)