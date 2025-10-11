from django.urls import path

from .kpi_views.session_views import (
    SessionLogsView,
    SessionDetailView,  
    SessionDisplayView, 
    CombinedLogsView,
    ActiveSessionsView,
    UserSessionsView,
    SessionStatisticsView,
    SessionCleanupView,
    CleanupStatusView,  
    AutoCleanupControlView,  
    SessionExportView,  
    ForceLogoutView,
    BulkSessionControlView, 
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
    BulkDeleteProductsView, 
    
    # Product sync views
    ProductSyncView,
    
    # Product import/export views
    ProductImportView,
    ProductExportView,
    BulkCreateProductsView,
    ImportTemplateView,
    TestTemplateView,
)

# BATCH VIEWS - ADD THIS IMPORT
from .kpi_views.batch_views import (
    # Batch CRUD
    BatchListView,
    CreateBatchView,
    BatchDetailView,
    UpdateBatchQuantityView,
    
    # Batch queries
    ProductBatchesView,
    ExpiringBatchesView,
    ProductsWithExpirySummaryView,
    
    # Batch operations
    ProcessSaleFIFOView,
    CheckExpiryAlertsView,
    MarkExpiredBatchesView,
    
    # Integration
    ProductWithBatchSummaryView,
    RestockWithBatchView,
    
    # Analytics
    BatchStatisticsView,
)

from .kpi_views.category_views import (
     CategoryKPIView,
    CategoryDetailView,
    CategorySoftDeleteView,
    CategoryHardDeleteView,
    CategoryRestoreView,                  
    CategoryDeletedListView,               
    CategoryBulkOperationsView,         
    CategoryDeleteInfoView,               
    CategorySubcategoryView,              
    UncategorizedCategoryView,              
    SubcategoryProductsView,
    CategoryProductManagementView,  
)

# POS Operations
from .kpi_views.category_pos_views import (
    POSCatalogView,
    POSProductBatchView,
    POSBarcodeView,
    POSSearchView,
    POSStockCheckView,
    POSLowStockView,
    POSSubcategoryProductsView,  
)

# Display/Export Operations
from .kpi_views.category_display_views import (
    CategoryDataView,
    CategoryExportView,
    CategoryStatsView,
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
    DeletedPromotionsView,  
    PromotionHardDeleteView,
    ActivePromotionsView,
    PromotionActivationView,
    PromotionDeactivationView,
    PromotionExpirationView,
    PromotionApplicationView,
    PromotionStatisticsView,
    PromotionAuditView,
    PromotionSearchView,
    PromotionReportView,
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
    path('suppliers/health/', SupplierHealthCheckView.as_view(), name='health-check'),

    # === SPECIFIC PATHS FIRST (no parameters) ===
    path('suppliers/deleted/', DeletedSuppliersView.as_view(), name='deleted-suppliers'),

    # === SUPPLIER CRUD ===
    path('suppliers/', SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/<str:supplier_id>/', SupplierDetailView.as_view(), name='supplier-detail'),

    # === SUPPLIER MANAGEMENT ===
    path('suppliers/<str:supplier_id>/restore/', SupplierRestoreView.as_view(), name='supplier-restore'),
    path('suppliers/<str:supplier_id>/hard-delete/', SupplierHardDeleteView.as_view(), name='supplier-hard-delete'),

    # === PURCHASE ORDER - SPECIFIC PATHS FIRST ===
    path('suppliers/<str:supplier_id>/orders/deleted/', DeletedPurchaseOrdersView.as_view(), name='deleted-purchase-orders'),

    # === PURCHASE ORDER CRUD ===
    path('suppliers/<str:supplier_id>/orders/', PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('suppliers/<str:supplier_id>/orders/<str:order_id>/', PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),

    # === PURCHASE ORDER MANAGEMENT ===
    path('suppliers/<str:supplier_id>/orders/<str:order_id>/restore/', PurchaseOrderRestoreView.as_view(), name='purchase-order-restore'),
    path('suppliers/<str:supplier_id>/orders/<str:order_id>/hard-delete/', PurchaseOrderHardDeleteView.as_view(), name='purchase-order-hard-delete'),
        
    # ========== SESSION MANAGEMENT ==========
    path('session-logs/', SessionLogsView.as_view(), name='session-logs'),
    path('session-logs/display/', SessionDisplayView.as_view(), name='session-logs-display'),  # Move this BEFORE the parameterized one
    path('session-logs/combined/', CombinedLogsView.as_view(), name='combined-logs'),
    path('session-logs/<str:session_id>/', SessionDetailView.as_view(), name='session-detail'),
    # Session management
    path('sessions/active/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('sessions/user/<str:user_id>/', UserSessionsView.as_view(), name='user-sessions'),
    path('sessions/statistics/', SessionStatisticsView.as_view(), name='session-statistics'),
    # Cleanup and maintenance (Admin only)
    path('sessions/cleanup/', SessionCleanupView.as_view(), name='session-cleanup'),
    path('sessions/cleanup/status/', CleanupStatusView.as_view(), name='cleanup-status'),  
    path('sessions/cleanup/auto/', AutoCleanupControlView.as_view(), name='auto-cleanup-control'),  
    # Export functionality (Admin only)
    path('sessions/export/', SessionExportView.as_view(), name='session-export'), 
    # Admin control endpoints
    path('sessions/force-logout/<str:user_id>/', ForceLogoutView.as_view(), name='force-logout'),
    path('sessions/bulk-control/', BulkSessionControlView.as_view(), name='bulk-session-control'),  
    
    # ========== PRODUCT MANAGEMENT ==========
    # Product CRUD (static paths first)
    path('products/', ProductListView.as_view(), name='product-list'),  # GET (list), POST (create)
    path('products/sku/<str:sku>/', ProductBySkuView.as_view(), name='product-by-sku'),  # GET by SKU
    path('products/deleted/', DeletedProductsView.as_view(), name='deleted-products'),  # GET deleted products
    path('products/bulk-delete/', BulkDeleteProductsView.as_view(), name='bulk-delete-products'),  # POST
    
    # Product import/export
    path('products/import/', ProductImportView.as_view(), name='product-import'),  # POST
    path('products/test-template/', TestTemplateView.as_view(), name='test-template'),
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

    # ========== BATCH MANAGEMENT ==========
    # Batch CRUD (static paths first)
    path('batches/', BatchListView.as_view(), name='batch-list'),  # GET (list with filters)
    path('batches/create/', CreateBatchView.as_view(), name='batch-create'),  # POST
    path('batches/expiring/', ExpiringBatchesView.as_view(), name='expiring-batches'),  # GET
    path('batches/statistics/', BatchStatisticsView.as_view(), name='batch-statistics'),  # GET
    
    # Batch operations
    path('batches/process-sale/', ProcessSaleFIFOView.as_view(), name='process-sale-fifo'),  # POST
    path('batches/check-expiry-alerts/', CheckExpiryAlertsView.as_view(), name='check-expiry-alerts'),  # POST
    path('batches/mark-expired/', MarkExpiredBatchesView.as_view(), name='mark-expired-batches'),  # POST
    
    # Batch detail operations (parameterized paths last)
    path('batches/<str:batch_id>/', BatchDetailView.as_view(), name='batch-detail'),  # GET
    path('batches/<str:batch_id>/update-quantity/', UpdateBatchQuantityView.as_view(), name='batch-update-quantity'),  # PUT
    
    # Product-batch integration
    path('products/<str:product_id>/batches/', ProductBatchesView.as_view(), name='product-batches'),  # GET
    path('products/<str:product_id>/with-batches/', ProductWithBatchSummaryView.as_view(), name='product-with-batches'),  # GET
    path('products/<str:product_id>/restock-batch/', RestockWithBatchView.as_view(), name='restock-with-batch'),  # POST
    path('products/expiry-summary/', ProductsWithExpirySummaryView.as_view(), name='products-expiry-summary'),  # GET
    
    # ========== CATEGORY MANAGEMENT ==========
    # Core Category Operations
    path('category/', CategoryKPIView.as_view(), name='category-operations'),
    path('category/stats/', CategoryStatsView.as_view(), name='category-stats'),
    path('category/display/', CategoryDataView.as_view(), name='category-display'),
    path('category/export/', CategoryExportView.as_view(), name='category-export'),
    path('category/bulk/', CategoryBulkOperationsView.as_view(), name='category-bulk-operations'),
    path('category/product-management/', CategoryProductManagementView.as_view(), name='category-product-management'),

    # Admin-only Category Operations
    path('category/deleted/', CategoryDeletedListView.as_view(), name='category-deleted-list'),
    path('category/uncategorized/', UncategorizedCategoryView.as_view(), name='uncategorized-category'),

    # Individual Category Operations
    path('category/<str:category_id>/', CategoryDetailView.as_view(), name='category-detail'),
    path('category/<str:category_id>/delete-info/', CategoryDeleteInfoView.as_view(), name='category-delete-info'),
    path('category/<str:category_id>/soft-delete/', CategorySoftDeleteView.as_view(), name='category-soft-delete'),
    path('category/<str:category_id>/hard-delete/', CategoryHardDeleteView.as_view(), name='category-hard-delete'),
    path('category/<str:category_id>/restore/', CategoryRestoreView.as_view(), name='category-restore'),
    path('category/<str:category_id>/subcategories/', CategorySubcategoryView.as_view(), name='category-subcategories'),
    path('category/<str:category_id>/subcategories/<str:subcategory_name>/products/', SubcategoryProductsView.as_view(), name='subcategory-products'),

    # ========== POS OPERATIONS ==========
    path('pos/catalog/', POSCatalogView.as_view(), name='pos-catalog'),
    path('pos/products/batch/', POSProductBatchView.as_view(), name='pos-product-batch'),
    path('pos/search/', POSSearchView.as_view(), name='pos-search'),
    path('pos/barcode/<str:barcode>/', POSBarcodeView.as_view(), name='pos-barcode'),
    path('pos/stock/check/', POSStockCheckView.as_view(), name='pos-stock-check'),
    path('pos/stock/low/', POSLowStockView.as_view(), name='pos-low-stock'),
    path('pos/category/<str:category_id>/subcategory/<str:subcategory_name>/products/', POSSubcategoryProductsView.as_view(), name='pos-subcategory-products'),
    
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
    path('promotions/active/', ActivePromotionsView.as_view(), name='active-promotions'),  # GET
    path('promotions/deleted/', DeletedPromotionsView.as_view(), name='promotion-deleted-list'),  # GET - Admin only
    path('promotions/search/', PromotionSearchView.as_view(), name='promotion-search'),  # GET
    path('promotions/statistics/', PromotionStatisticsView.as_view(), name='promotion-statistics'),  # GET - Admin only
    path('promotions/apply/', PromotionApplicationView.as_view(), name='promotion-apply'),  # POST
    path('promotions/by-name/<str:promotion_name>/', PromotionByNameView.as_view(), name='promotion-by-name'),  # GET
    path('promotions/<str:promotion_id>/', PromotionDetailView.as_view(), name='promotion-detail'),  # GET, PUT, DELETE
    path('promotions/<str:promotion_id>/activate/', PromotionActivationView.as_view(), name='promotion-activate'),  # POST - Admin only
    path('promotions/<str:promotion_id>/deactivate/', PromotionDeactivationView.as_view(), name='promotion-deactivate'),  # POST - Admin only
    path('promotions/<str:promotion_id>/expire/', PromotionExpirationView.as_view(), name='promotion-expire'),  # POST - Admin only
    path('promotions/<str:promotion_id>/restore/', PromotionRestoreView.as_view(), name='promotion-restore'),  # POST - Admin only
    path('promotions/<str:promotion_id>/hard-delete/', PromotionHardDeleteView.as_view(), name='promotion-hard-delete'),  # DELETE - Admin only
    path('promotions/<str:promotion_id>/audit/', PromotionAuditView.as_view(), name='promotion-audit'),  # GET - Admin only
    path('promotions/<str:promotion_id>/report/', PromotionReportView.as_view(), name='promotion-report'),  # GET - Admin only


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