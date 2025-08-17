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
from .kpi_views.authentication_views import (
    # Authentication views
    LoginView,
    LogoutView,
    RefreshTokenView,
    CurrentUserView,
    VerifyTokenView,
)

from .kpi_views.product_views import (
   # Product views
    ProductListView,
    ProductDetailView,
    ProductBySkuView,
    ProductCreateView,
    ProductUpdateView,
    ProductDeleteView,
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
    UnsyncedProductsView,
    SyncStatusView,
    
    # Product import/export views
    ProductImportView,
    ProductExportView,
    BulkCreateProductsView,
    ImportTemplateView,
)

from .kpi_views.category_views import (
    CategoryKPIView,                    # Create & List categories
    CategoryDetailView,                 # Get, Update, Soft Delete individual category
    CategoryDataView,                   # Categories with sales data
    CategoryExportView,                 # Export categories (CSV/JSON)
    CategoryStatsView,                  # Category statistics ()
    CategoryHardDeleteView,             # Hard delete (Admin only)
    CategoryRestoreView,                # Restore deleted (Admin only) 
    CategoryDeletedListView,            # List deleted categories (Admin only)
    CategoryDeleteInfoView,             # Pre-delete information
    CategoryBulkOperationsView,         # Bulk operations (centralized)
    CategorySubcategoryView,            # Add/Remove/Get subcategories
    ProductSubcategoryUpdateView,       # Update product subcategory
    ProductMoveToUncategorizedView,     # Move single product to uncategorized
    ProductBulkMoveToUncategorizedView, # Bulk move products to uncategorized
    UncategorizedCategoryView,  # Uncategorized Category Management
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

from .views import (
    APIDocumentationView,
    
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


urlpatterns = [
    path('', SystemStatusView.as_view(), name='system-status'),  # Root endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
   # User endpoints
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/email/<str:email>/', UserByEmailView.as_view(), name='user-by-email'),
    path('users/username/<str:username>/', UserByUsernameView.as_view(), name='user-by-username'),
    path('users/<str:user_id>/', UserDetailView.as_view(), name='user-detail'),
   
    # Customer endpoints
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/search/', CustomerSearchView.as_view(), name='customer-search'),
    path('customers/statistics/', CustomerStatisticsView.as_view(), name='customer-statistics'),
    path('customers/email/<str:email>/', CustomerByEmailView.as_view(), name='customer-by-email'),
    path('customers/<str:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),
    path('customers/<str:customer_id>/restore/', CustomerRestoreView.as_view(), name='customer-restore'),
    path('customers/<str:customer_id>/hard-delete/', CustomerHardDeleteView.as_view(), name='customer-hard-delete'),
    path('customers/<str:customer_id>/loyalty/', CustomerLoyaltyView.as_view(), name='customer-loyalty'),
    
    # Product CRUD endpoints - REORGANIZED FOR BETTER ROUTING
    path('products/', ProductListView.as_view(), name='product-list'),  # GET (list), POST (create)
    path('products/create/', ProductCreateView.as_view(), name='product-create'),  # POST
    path('products/sku/<str:sku>/', ProductBySkuView.as_view(), name='product-by-sku'),  # GET - MOVED UP
    path('products/deleted/', DeletedProductsView.as_view(), name='deleted-products'),  # GET - MOVED UP
    
    # Product import/export endpoints - MOVED UP TO AVOID CONFLICTS
    path('products/import/', ProductImportView.as_view(), name='product-import'),  # POST
    path('products/import/template/', ImportTemplateView.as_view(), name='import-template'),  # GET
    path('products/export/', ProductExportView.as_view(), name='product-export'),  # GET
    path('products/bulk-create/', BulkCreateProductsView.as_view(), name='bulk-create-products'),  # POST
    
    # Product reports and filtering endpoints - MOVED UP TO AVOID CONFLICTS
    path('products/reports/low-stock/', LowStockProductsView.as_view(), name='low-stock-products'),  # GET
    path('products/reports/expiring/', ExpiringProductsView.as_view(), name='expiring-products'),  # GET
    path('products/category/<str:category_id>/', ProductsByCategoryView.as_view(), name='products-by-category'),  # GET
    
    # Product synchronization endpoints - MOVED UP TO AVOID CONFLICTS
    path('products/sync/', ProductSyncView.as_view(), name='product-sync'),  # POST
    path('products/sync/unsynced/', UnsyncedProductsView.as_view(), name='unsynced-products'),  # GET
    
    # Stock management endpoints - MOVED UP TO AVOID CONFLICTS
    path('products/stock/bulk-update/', BulkStockUpdateView.as_view(), name='bulk-stock-update'),  # POST
    
    # Product detail endpoints with ID parameters - MOVED DOWN TO AVOID CONFLICTS
    path('products/<str:product_id>/', ProductDetailView.as_view(), name='product-detail'),  # GET, PUT, DELETE
    path('products/<str:product_id>/update/', ProductUpdateView.as_view(), name='product-update'),  # PUT/PATCH
    path('products/<str:product_id>/delete/', ProductDeleteView.as_view(), name='product-delete'),  # DELETE
    path('products/<str:product_id>/restore/', ProductRestoreView.as_view(), name='product-restore'),  # POST
    
    # Stock management endpoints with ID parameters - MOVED DOWN
    path('products/<str:product_id>/stock/', ProductStockUpdateView.as_view(), name='product-stock-update'),  # PUT/PATCH
    path('products/<str:product_id>/stock/adjust/', StockAdjustmentView.as_view(), name='stock-adjustment'),  # POST
    path('products/<str:product_id>/stock/history/', StockHistoryView.as_view(), name='stock-history'),  # GET
    path('products/<str:product_id>/restock/', RestockProductView.as_view(), name='restock-product'),  # POST
    
    # Product sync endpoints with ID parameters - MOVED DOWN
    path('products/<str:product_id>/sync/status/', SyncStatusView.as_view(), name='sync-status'),  # GET, PUT
    
    # Authentication endpoints
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', RefreshTokenView.as_view(), name='refresh-token'),
    path('auth/me/', CurrentUserView.as_view(), name='current-user'),
    path('auth/verify-token/', VerifyTokenView.as_view(), name='verify-token'),
    
    # Session logs endpoints
    path('session-logs/', SessionLogsView.as_view(), name='session-logs'),
    path('session-logs/display/', SessionDisplayView.as_view(), name='session-logs-display'),
    path('session-logs/combined/', CombinedLogsView.as_view(), name='combined-logs'),
    
    # Session management endpoints
    path('sessions/active/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('sessions/user/<str:user_id>/', UserSessionsView.as_view(), name='user-sessions'),
    path('sessions/statistics/', SessionStatisticsView.as_view(), name='session-statistics'),
    
    # NEW: Admin session management endpoints
    path('sessions/cleanup/', SessionCleanupView.as_view(), name='session-cleanup'),
    path('sessions/force-logout/<str:user_id>/', ForceLogoutView.as_view(), name='force-logout'),
    
    # System status endpoint (if you want to keep it)
    path('category/stats/', CategoryStatsView.as_view(), name='category-stats'),
    # Categories with sales data (MUST come before category/<str:category_id>/)
    path('category/display/', CategoryDataView.as_view(), name='category-display'),  
    # Export operations (MUST come before category/<str:category_id>/) - FIX: Add the actual path here
    path('category/export/', CategoryExportView.as_view(), name='category-export'), 
    # Deleted categories management (MUST come before category/<str:category_id>/)
    path('category/deleted/', CategoryDeletedListView.as_view(), name='category-deleted-list'),
    # Centralized bulk operations (MUST come before category/<str:category_id>/)
    path('category/bulk/', CategoryBulkOperationsView.as_view(), name='category-bulk-operations'),
    # Uncategorized category management (MUST come before category/<str:category_id>/)
    path('category/uncategorized/', UncategorizedCategoryView.as_view(), name='uncategorized-category'),

    # ========== MAIN CATEGORY OPERATIONS ==========
    # Category list and create
    path('category/', CategoryKPIView.as_view(), name='category-operations'),

    # ========== PARAMETERIZED PATHS (MUST COME LAST) ==========
    # Individual category operations (Get, Update, Soft Delete)
    path('category/<str:category_id>/', CategoryDetailView.as_view(), name='category-detail'),
    # Category-specific operations with parameters
    path('category/<str:category_id>/delete-info/', CategoryDeleteInfoView.as_view(), name='category-delete-info'),
    path('category/<str:category_id>/hard-delete/', CategoryHardDeleteView.as_view(), name='category-hard-delete'),
    path('category/<str:category_id>/restore/', CategoryRestoreView.as_view(), name='category-restore'),
    path('category/<str:category_id>/subcategories/', CategorySubcategoryView.as_view(), name='category-subcategories'),
    
    # ========== PRODUCT OPERATIONS ==========
    # Update product subcategory
    path('product/subcategory/update/', ProductSubcategoryUpdateView.as_view(), name='product-subcategory-update'),
    # Move products to uncategorized
    path('product/move-to-uncategorized/', ProductMoveToUncategorizedView.as_view(), name='product-move-to-uncategorized'),
    path('product/bulk-move-to-uncategorized/', ProductBulkMoveToUncategorizedView.as_view(), name='product-bulk-move-to-uncategorized'),


   # Bulk import and template endpoints (MUST be first)
    path('invoices/bulk-import/', SalesLogBulkImportView.as_view(), name='invoice-bulk-import'),
    path('invoices/export/', SalesLogExportView.as_view(), name='invoice-export'),
   # path('invoices/template/', SalesLogTemplateView.as_view(), name='invoice-template'), this is debugging
    path('invoices/stats/', SalesLogStatsView.as_view(), name='invoice-stats'),
    
    # Generic CRUD operations (MUST be last)
    path('invoices/', SalesLogView.as_view(), name='invoice-list-create'),
    path('invoices/<str:invoice_id>/', SalesLogView.as_view(), name='invoice-detail'),

    #Sales item Transaction History
    path('reports/top-item/', SalesTopItemView.as_view(), name='top-items'),
    path('reports/top-chart-item/', SalesTopItemChartView.as_view(), name='top-chart-items'), 
    path('reports/item-history/', SalesItemHistoryView.as_view(), name='item-history'),

    # Promotion
    path('promotions/health/', PromotionHealthCheckView.as_view(), name='promotion-health'),  # ✅ CHANGED: promotions/health/
    path('promotions/', PromotionListView.as_view(), name='promotion-list'),  # ✅ CHANGED: promotions/
    path('promotions/<str:promotion_id>/', PromotionDetailView.as_view(), name='promotion-detail'),  # ✅ CHANGED: promotions/
    path('promotions/<str:promotion_id>/hard-delete/', PromotionHardDeleteView.as_view(), name='promotion-hard-delete'),  # ✅ CHANGED: promotions/
    path('promotions/<str:promotion_id>/restore/', PromotionRestoreView.as_view(), name='promotion-restore'),  # ✅ CHANGED: promotions/
    path('promotions/deleted/', PromotionDeletedListView.as_view(), name='promotion-deleted-list'),  # ✅ CHANGED: promotions/deleted/
    path('promotions/by-name/<str:promotion_name>/', PromotionByNameView.as_view(), name='promotion-by-name'),  # ✅ CHANGED: promotions/by-name/
    
    #Sales Report
     # Core API endpoints
    path('sales-report/summary/', SalesSummaryView.as_view(), name='sales_summary'),
    path('sales-report/transactions/', SalesTransactionsView.as_view(), name='sales_transactions'), 
    path('sales-report/by-period/', SalesByPeriodView.as_view(), name='sales_by_period'),
    
    # Convenience endpoints
    path('sales-report/dashboard/', DashboardSummaryView.as_view(), name='dashboard_summary'),
    path('sales-report/comparison/', SalesComparisonView.as_view(), name='sales_comparison'),

    ##PromotionCon Services/ POS
    path('pos/transaction/', POSTransactionView.as_view(), name='pos_transaction'),
    path('pos/stock-validation/', StockValidationView.as_view(), name='stock_validation'),
    path('pos/stock-warnings/', StockWarningsView.as_view(), name='stock_warnings'),
    path('pos/promotion-preview/', PromotionCheckoutView.as_view(), name='promotion_preview'),
    path('pos/kpi/transactions/', POSTransactionKPIView.as_view(), name='pos_transaction_kpi'),
    path('pos/kpi/inventory/', InventoryKPIView.as_view(), name='inventory_kpi'),
    path('pos/kpi/stock-alerts/', StockAlertKPIView.as_view(), name='stock_alert_kpi'),
    path('pos/health/', POSHealthCheckView.as_view(), name='pos_health_check'),

    ##Sales Services
     # Core sales endpoints
    path('sales/create/', SalesServiceView.as_view(), name='create_unified_sale'),
    path('sales/pos/create/', CreatePOSSale.as_view(), name='create_pos_sale'),
    path('sales/log/create/', CreateSalesLog.as_view(), name='create_sales_log'),
    path('sales/recent/', FetchRecentSales.as_view(), name='recent_sales'),
    path('sales/get/<str:sale_id>/', GetSaleID.as_view(), name='get_sale_by_id'),


    # API Documentation
    path('docs/', APIDocumentationView.as_view(), name='api-documentation'),
]