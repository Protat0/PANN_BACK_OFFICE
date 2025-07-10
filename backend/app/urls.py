from django.urls import path

from .kpi_views.session_views import (
    # Session management views
    SessionLogsView,
    SystemStatusView,
    SessionManagementView,
    ActiveSessionsView,
    UserSessionsView,
    SessionStatisticsView,
    SessionDisplayView,
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

    #Customer KPI Views
    ActiveCustomerKPIView,
    MonthlyCustomerKPIView,
    DailyCustomerKPIView,
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
    CategoryDetailView,
    CategoryKPIView,
    CategorySubcategoryView,
    CategoryDataView,
    CategoryExportView,      
    CategoryExportStatsView,
    CategorySoftDeleteView,
    CategoryHardDeleteView,
    CategoryRestoreView,
    CategoryDeletedListView,
    CategoryDeleteInfoView,
    ProductSubcategoryUpdateView,
    ProductCategoryInfoView, 
    CategorySubcategoriesListView,
    UncategorizedCategoryProductsView,
    UncategorizedCategoryView, 
    MigrateUncategorizedProductsView,
    ProductBulkMoveToUncategorizedView,
    ProductMoveToUncategorizedView
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

urlpatterns = [
    path('', SystemStatusView.as_view(), name='system-status'),  # Root endpoint
    path('health/', HealthCheckView.as_view(), name='health-check'),
    
    # User endpoints
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<str:user_id>/', UserDetailView.as_view(), name='user-detail'),
    path('users/email/<str:email>/', UserByEmailView.as_view(), name='user-by-email'),
    path('users/username/<str:username>/', UserByUsernameView.as_view(), name='user-by-username'),
    
    # Customer endpoints
    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/<str:customer_id>/', CustomerDetailView.as_view(), name='customer-detail'),
    
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
    
    # Session logs endpoint
    path('session-logs/', SessionLogsView.as_view(), name='session-logs'),
    path('session-logs/display/', SessionDisplayView.as_view(), name='session-logs-display'), #Data View

    # Session management endpoints
    path('sessions/', SessionManagementView.as_view(), name='session-management'),
    path('sessions/active/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('sessions/user/<str:user_id>/', UserSessionsView.as_view(), name='user-sessions'),
    path('sessions/statistics/', SessionStatisticsView.as_view(), name='session-statistics'),

    # Customer KPI Views
    path('customerkpi/', ActiveCustomerKPIView.as_view(), name="get-active-users"), #Gets Active Users
    path('customerkpimonthly/', MonthlyCustomerKPIView.as_view(), name="get-monthly-users"),
     path('customerkpidaily/', DailyCustomerKPIView.as_view(), name="get-daily-users"),

    # Category endpoints  
    path('category/', CategoryKPIView.as_view(), name="category-operations"),
    path('category/dataview/', CategoryDataView.as_view(), name="category-dataview"),
    path('category/exportcat/', CategoryExportView.as_view(), name='export_categories'),  
    path('category/export/stats/', CategoryExportStatsView.as_view(), name='export_categories_stats'),  

    # Product movement endpoints 
    path('category/product/subcategory/update/', ProductSubcategoryUpdateView.as_view(), name='product-subcategory-update'),
    path('category/product/move-to-uncategorized/', ProductMoveToUncategorizedView.as_view(), name='product-move-to-uncategorized'), # NEW
    path('category/product/bulk-move-to-uncategorized/', ProductBulkMoveToUncategorizedView.as_view(), name='product-bulk-move-to-uncategorized'), # NEW
    path('category/product/<str:product_id>/info/', ProductCategoryInfoView.as_view(), name='product-category-info'),

    # Category detail endpoints  
    path('category/<str:category_id>/', CategoryDetailView.as_view(), name="category-detail"),
    path('category/<str:category_id>/subcategories/', CategorySubcategoryView.as_view(), name="category-subcategories"),
    path('category/<str:category_id>/subcategories/list/', CategorySubcategoriesListView.as_view(), name='category-subcategories-list'),

    # Soft Delete Operations
    path('category/<str:category_id>/soft-delete/', CategorySoftDeleteView.as_view(), name='category-soft-delete'),
    path('category/bulk-soft-delete/', CategorySoftDeleteView.as_view(), name='category-bulk-soft-delete'), 

    # Hard Delete Operations (Admin only)
    path('category/<str:category_id>/hard-delete/', CategoryHardDeleteView.as_view(), name='category-hard-delete'),

    # Restore Operations
    path('category/<str:category_id>/restore/', CategoryRestoreView.as_view(), name='category-restore'),

    # Deleted Categories Management
    path('category/deleted/list/', CategoryDeletedListView.as_view(), name='category-deleted-list'),

    # Delete Information (for confirmation dialogs)
    path('category/<str:category_id>/delete-info/', CategoryDeleteInfoView.as_view(), name='category-delete-info'),

    # Uncategorized category management
    path('category/uncategorized/', UncategorizedCategoryView.as_view(), name='uncategorized-category'),
    path('category/uncategorized/products/', UncategorizedCategoryProductsView.as_view(), name='uncategorized-category-products'),
    path('category/uncategorized/migrate/', MigrateUncategorizedProductsView.as_view(), name='migrate-uncategorized-products'),



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

    # API Documentation
    path('docs/', APIDocumentationView.as_view(), name='api-documentation'),
]