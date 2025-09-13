from django.urls import path

from .kpi_views.session_views import (
    SessionLogsView,
    SessionDisplayView, 
    CombinedLogsView,
    ActiveSessionsView,
    UserSessionsView,
    SessionStatisticsView,
    SessionCleanupView,
    ForceLogoutView,
    SystemStatusView
)

from .kpi_views.user_views import (
    HealthCheckView, 
    UserListView, 
    UserDetailView, 
    UserByEmailView, 
    UserByUsernameView,
    UserRestoreView,       
    UserHardDeleteView,     
    DeletedUsersView,       
)

from .kpi_views.customer_views import (
    CustomerListView,
    CustomerDetailView,
    CustomerRestoreView,
    CustomerHardDeleteView,
    CustomerSearchView,
    CustomerByEmailView,
    CustomerStatisticsView,
    CustomerLoyaltyView,
)

from .kpi_views.supplier_views import (
    SupplierHealthCheckView,
    SupplierListView, 
    SupplierDetailView,
    SupplierRestoreView,
    SupplierHardDeleteView,
    DeletedSuppliersView,
    PurchaseOrderListView,
    PurchaseOrderDetailView,
    PurchaseOrderRestoreView,
    PurchaseOrderHardDeleteView,
    DeletedPurchaseOrdersView
)

from .kpi_views.authentication_views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    CurrentUserView,
    VerifyTokenView,
)

from .kpi_views.product_views import (
    # Product CRUD views
    ProductListView,
    ProductDetailView,
    ProductBySkuView,
    ProductRestoreView,
    
    # Stock management views
    ProductStockUpdateView,
    BulkStockUpdateView,
    StockHistoryView,
    StockAdjustmentView,
    RestockProductView,
    
    # Product reports views
    LowStockProductsView,
    ExpiringProductsView,
    ProductsByCategoryView,
    DeletedProductsView,
    
    # Product sync views
    ProductSyncView,
    
    # Product import/export views
    ProductImportView,
    ProductExportView,
    BulkCreateProductsView,
    ImportTemplateView,
)

from .kpi_views.category_views import (
    CategoryKPIView,                    # Create & List categories
    CategoryDetailView,                 # Get, Update individual category
    CategoryDataView,                   # Categories with sales data
    CategoryExportView,                 # Export categories (CSV/JSON)
    CategoryStatsView,                  # Category statistics
    CategoryHardDeleteView,             # Hard delete (Admin only)
    CategorySoftDeleteView,             # Soft delete
    CategoryRestoreView,                # Restore deleted (Admin only) 
    CategoryDeletedListView,            # List deleted categories (Admin only)
    CategoryDeleteInfoView,             # Pre-delete information
    CategoryBulkOperationsView,         # Bulk operations (centralized)
    CategorySubcategoryView,            # Add/Remove/Get subcategories
    ProductSubcategoryUpdateView,       # Update product subcategory
    ProductMoveToUncategorizedView,     # Move single product to uncategorized
    ProductBulkMoveToUncategorizedView, # Bulk move products to uncategorized
    UncategorizedCategoryView,          # Uncategorized Category Management
    ProductToSubcategoryView,           # Assign products to subcategories
    SubcategoryProductsView,            # Get products in subcategory
    # POS Category views
    POSCatalogView,                     # POS catalog structure
    POSProductBatchView,                # Batch fetch products for POS
    POSSubcategoryProductsView,         # POS subcategory products
    POSBarcodeView,                     # POS barcode scanning
    POSSearchView,                      # POS product search
    POSStockCheckView,                  # POS stock validation
    POSLowStockView,                    # POS low stock alerts
)

from .kpi_views.saleslog_views import (
    SalesLogView,
    SalesLogStatsView,
    SalesItemHistoryView,
    SalesTopItemView,
    SalesTopItemChartView,
)

from .kpi_views.sales_bulk_views import (
    SalesLogBulkImportView,
    SalesLogTemplateView,
    SalesLogExportView,
)

from .kpi_views.promotion_views import (
    PromotionHealthCheckView,
    PromotionListView,
    PromotionDetailView,
    PromotionByNameView,
    PromotionRestoreView,
    PromotionDeletedListView,
    PromotionHardDeleteView,
)

from .kpi_views.pos.salesReportView import (
    SalesSummaryView,
    SalesTransactionsView,
    SalesByPeriodView,
    DashboardSummaryView,
    SalesComparisonView,
)

from .kpi_views.pos.promotionConView import (
    POSTransactionView,
    StockValidationView,
    StockWarningsView,
    PromotionCheckoutView,
    POSTransactionKPIView,
    InventoryKPIView,
    StockAlertKPIView,
    POSHealthCheckView
)

from .kpi_views.pos.salesServiceView import (
    SalesServiceView,
    CreatePOSSale,
    CreateSalesLog,
    GetSaleID,
    FetchRecentSales,
)

from .views import (
    APIDocumentationView,
)

urlpatterns = [
    # ========== SYSTEM & HEALTH ==========
    path('', SystemStatusView.as_view(), name='system-status'),  # Root endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),
    path('docs/', APIDocumentationView.as_view(), name='api-documentation'),
    
    # ========== AUTHENTICATION ==========
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    
    # ========== USER MANAGEMENT ==========
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/deleted/', DeletedUsersView.as_view(), name='deleted-users'),
    path('users/email/<str:email>/', UserByEmailView.as_view(), name='user-by-email'),
    path('users/username/<str:username>/', UserByUsernameView.as_view(), name='user-by-username'),
    path('users/<str:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/<str:user_id>/restore/', UserRestoreView.as_view(), name='user-restore'),
    path('users/<str:user_id>/hard-delete/', UserHardDeleteView.as_view(), name='user-hard-delete'),
    
    # ========== CUSTOMER MANAGEMENT ==========
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/search/', CustomerSearchView.as_view(), name='customer-search'),
    path('customers/statistics/', CustomerStatisticsView.as_view(), name='customer-statistics'),
    path('customers/email/<str:email>/', CustomerByEmailView.as_view(), name='customer-by-email'),
    path('customers/<str:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<str:customer_id>/restore/', CustomerRestoreView.as_view(), name='customer-restore'),
    path('customers/<str:customer_id>/hard-delete/', CustomerHardDeleteView.as_view(), name='customer-hard-delete'),
    path('customers/<str:customer_id>/loyalty/', CustomerLoyaltyView.as_view(), name='customer-loyalty'),
    
    # ========== SUPPLIER MANAGEMENT ==========
    path('health/', SupplierHealthCheckView.as_view(), name='health-check'),
    # Supplier CRUD operations
    path('', SupplierListView.as_view(), name='supplier-list'),  # GET (list), POST (create)
    path('<str:supplier_id>/', SupplierDetailView.as_view(), name='supplier-detail'),  # GET, PUT, DELETE
    # Supplier management operations
    path('<str:supplier_id>/restore/', SupplierRestoreView.as_view(), name='supplier-restore'),
    path('<str:supplier_id>/hard-delete/', SupplierHardDeleteView.as_view(), name='supplier-hard-delete'),
    path('deleted/', DeletedSuppliersView.as_view(), name='deleted-suppliers'),
    # Purchase Order operations
    path('<str:supplier_id>/orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),  # GET (list), POST (create)
    path('<str:supplier_id>/orders/<str:order_id>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),  # GET, PUT, DELETE
    # Purchase Order management operations
    path('<str:supplier_id>/orders/<str:order_id>/restore/', PurchaseOrderRestoreView.as_view(), name='purchase-order-restore'),
    path('<str:supplier_id>/orders/<str:order_id>/hard-delete/', PurchaseOrderHardDeleteView.as_view(), name='purchase-order-hard-delete'),
    path('<str:supplier_id>/orders/deleted/', DeletedPurchaseOrdersView.as_view(), name='deleted-purchase-orders'),

    # ========== SESSION MANAGEMENT ==========
    path('session-logs/', SessionLogsView.as_view(), name='session-logs'),
    path('session-logs/display/', SessionDisplayView.as_view(), name='session-logs-display'),
    path('session-logs/combined/', CombinedLogsView.as_view(), name='combined-logs'),
    path('sessions/active/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('sessions/user/<str:user_id>/', UserSessionsView.as_view(), name='user-sessions'),
    path('sessions/statistics/', SessionStatisticsView.as_view(), name='session-statistics'),
    path('sessions/cleanup/', SessionCleanupView.as_view(), name='session-cleanup'),  # Admin only
    path('sessions/force-logout/<str:user_id>/', ForceLogoutView.as_view(), name='force-logout'),  # Admin only
    
    # ========== PRODUCT MANAGEMENT ==========
    # Product CRUD (static paths first)
    path('products/', ProductListView.as_view(), name='product-list'),  # GET (list), POST (create)
    path('products/sku/<str:sku>/', ProductBySkuView.as_view(), name='product-by-sku'),  # GET by SKU
    path('products/deleted/', DeletedProductsView.as_view(), name='deleted-products'),  # GET deleted products
    
    # Product import/export
    path('products/import/', ProductImportView.as_view(), name='product-import'),  # POST
    path('products/import/template/', ImportTemplateView.as_view(), name='import-template'),  # GET
    path('products/export/', ProductExportView.as_view(), name='product-export'),  # GET
    path('products/bulk-create/', BulkCreateProductsView.as_view(), name='bulk-create-products'),  # POST
    
    # Product reports
    path('products/reports/low-stock/', LowStockProductsView.as_view(), name='low-stock-products'),  # GET
    path('products/reports/expiring/', ExpiringProductsView.as_view(), name='expiring-products'),  # GET
    path('products/reports/by-category/<str:category_id>/', ProductsByCategoryView.as_view(), name='products-by-category'),  # GET
    
    # Product synchronization
    path('products/sync/', ProductSyncView.as_view(), name='product-sync'),  # POST
    
    # Bulk stock management
    path('products/stock/bulk-update/', BulkStockUpdateView.as_view(), name='bulk-stock-update'),  # POST
    
    # Product detail operations (parameterized paths last)
    path('products/<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),  # GET, PUT, DELETE
    path('products/<str:product_id>/restore/', ProductRestoreView.as_view(), name='product-restore'),  # POST
    path('products/<str:product_id>/stock/', ProductStockUpdateView.as_view(), name='product-stock-update'),  # PUT/PATCH
    path('products/<str:product_id>/stock/adjust/', StockAdjustmentView.as_view(), name='stock-adjustment'),  # POST
    path('products/<str:product_id>/stock/history/', StockHistoryView.as_view(), name='stock-history'),  # GET
    path('products/<str:product_id>/restock/', RestockProductView.as_view(), name='restock-product'),  # POST

    
    # ========== CATEGORY MANAGEMENT ==========
    # Category operations (static paths first)
    path('category/', CategoryKPIView.as_view(), name='category-operations'),  # GET (list), POST (create)
    path('category/stats/', CategoryStatsView.as_view(), name='category-stats'),  # GET statistics
    path('category/display/', CategoryDataView.as_view(), name='category-display'),  # GET with sales data
    path('category/export/', CategoryExportView.as_view(), name='category-export'),  # GET CSV/JSON export
    path('category/deleted/', CategoryDeletedListView.as_view(), name='category-deleted-list'),  # GET deleted categories
    path('category/bulk/', CategoryBulkOperationsView.as_view(), name='category-bulk-operations'),  # POST bulk operations
    path('category/uncategorized/', UncategorizedCategoryView.as_view(), name='uncategorized-category'),  # GET/POST uncategorized
    
    # Category detail operations (parameterized paths last)
    path('category/<str:category_id>/', CategoryDetailView.as_view(), name='category-detail'),  # GET, PUT
    path('category/<str:category_id>/delete-info/', CategoryDeleteInfoView.as_view(), name='category-delete-info'),  # GET pre-delete info
    path('category/<str:category_id>/soft-delete/', CategorySoftDeleteView.as_view(), name='category-soft-delete'),  # DELETE (soft)
    path('category/<str:category_id>/hard-delete/', CategoryHardDeleteView.as_view(), name='category-hard-delete'),  # DELETE (permanent) - Admin only
    path('category/<str:category_id>/restore/', CategoryRestoreView.as_view(), name='category-restore'),  # POST restore - Admin only
    path('category/<str:category_id>/subcategories/', CategorySubcategoryView.as_view(), name='category-subcategories'),  # GET/POST/DELETE subcategories
    path('category/<str:category_id>/subcategories/<str:subcategory_name>/products/', SubcategoryProductsView.as_view(), name='subcategory-products'),  # GET products in subcategory
    
    # ========== SALES & INVOICES ==========
    # Sales log operations
    path('invoices/', SalesLogView.as_view(), name='invoice-list-create'),  # GET (list), POST (create)
    path('invoices/bulk-import/', SalesLogBulkImportView.as_view(), name='invoice-bulk-import'),  # POST
    path('invoices/export/', SalesLogExportView.as_view(), name='invoice-export'),  # GET
    path('invoices/stats/', SalesLogStatsView.as_view(), name='invoice-stats'),  # GET
    path('invoices/<str:invoice_id>/', SalesLogView.as_view(), name='invoice-detail'),  # GET, PUT, DELETE
    
    # Sales reports
    path('reports/top-item/', SalesTopItemView.as_view(), name='top-items'),
    path('reports/top-chart-item/', SalesTopItemChartView.as_view(), name='top-chart-items'), 
    path('reports/item-history/', SalesItemHistoryView.as_view(), name='item-history'),
    
    # Sales report API endpoints
    path('sales-report/summary/', SalesSummaryView.as_view(), name='sales_summary'),
    path('sales-report/transactions/', SalesTransactionsView.as_view(), name='sales_transactions'), 
    path('sales-report/by-period/', SalesByPeriodView.as_view(), name='sales_by_period'),
    path('sales-report/dashboard/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('sales-report/comparison/', SalesComparisonView.as_view(), name='sales_comparison'),
    
    # Sales services
    path('sales/create/', SalesServiceView.as_view(), name='create_unified_sale'),
    path('sales/pos/create/', CreatePOSSale.as_view(), name='create_pos_sale'),
    path('sales/log/create/', CreateSalesLog.as_view(), name='create_sales_log'),
    path('sales/recent/', FetchRecentSales.as_view(), name='recent_sales'),
    path('sales/get/<str:sale_id>/', GetSaleID.as_view(), name='get_sale_by_id'),
    
    # ========== PROMOTIONS ==========
    path('promotions/', PromotionListView.as_view(), name='promotion-list'),  # GET (list), POST (create)
    path('promotions/health/', PromotionHealthCheckView.as_view(), name='promotion-health'),  # GET
    path('promotions/deleted/', PromotionDeletedListView.as_view(), name='promotion-deleted-list'),  # GET
    path('promotions/by-name/<str:promotion_name>/', PromotionByNameView.as_view(), name='promotion-by-name'),  # GET
    path('promotions/<str:promotion_id>/', PromotionDetailView.as_view(), name='promotion-detail'),  # GET, PUT, DELETE
    path('promotions/<str:promotion_id>/hard-delete/', PromotionHardDeleteView.as_view(), name='promotion-hard-delete'),  # DELETE - Admin only
    path('promotions/<str:promotion_id>/restore/', PromotionRestoreView.as_view(), name='promotion-restore'),  # POST - Admin only
    
    # ========== POS OPERATIONS ==========
    # POS health and core functionality
    path('pos/health/', POSHealthCheckView.as_view(), name='pos_health_check'),  # GET
    path('pos/catalog/', POSCatalogView.as_view(), name='pos_catalog'),  # GET category catalog
    path('pos/products/batch/', POSProductBatchView.as_view(), name='pos_product_batch'),  # POST batch fetch
    path('pos/search/', POSSearchView.as_view(), name='pos_search'),  # GET product search
    path('pos/stock-check/', POSStockCheckView.as_view(), name='pos_stock_check'),  # POST stock validation
    path('pos/low-stock/', POSLowStockView.as_view(), name='pos_low_stock'),  # GET low stock alerts
    path('pos/barcode/<str:barcode>/', POSBarcodeView.as_view(), name='pos_barcode'),  # GET barcode lookup
    path('pos/subcategory/<str:category_id>/<str:subcategory_name>/', POSSubcategoryProductsView.as_view(), name='pos_subcategory_products'),  # GET subcategory products
    
    # POS transactions and operations
    path('pos/transaction/', POSTransactionView.as_view(), name='pos_transaction'),
    path('pos/stock-validation/', StockValidationView.as_view(), name='stock_validation'),
    path('pos/stock-warnings/', StockWarningsView.as_view(), name='stock_warnings'),
    path('pos/promotion-preview/', PromotionCheckoutView.as_view(), name='promotion_preview'),
    
    # POS KPIs
    path('pos/kpi/transactions/', POSTransactionKPIView.as_view(), name='pos_transaction_kpi'),
    path('pos/kpi/inventory/', InventoryKPIView.as_view(), name='inventory_kpi'),
    path('pos/kpi/stock-alerts/', StockAlertKPIView.as_view(), name='stock_alert_kpi'),
]