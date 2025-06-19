from django.urls import path
from .views import (
    HealthCheckView, 
    UserListView, 
    UserDetailView, 
    UserByEmailView, 
    UserByUsernameView,
    CustomerListView,
    CustomerDetailView,
    
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
    
    # Authentication views
    LoginView,
    LogoutView,
    RefreshTokenView,
    CurrentUserView,
    VerifyTokenView,
    
    # Session management views
    SessionLogsView,
    SystemStatusView,
    SessionManagementView,
    ActiveSessionsView,
    UserSessionsView,
    SessionStatisticsView,
    APIDocumentationView
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

    # Session management endpoints
    path('sessions/', SessionManagementView.as_view(), name='session-management'),
    path('sessions/active/', ActiveSessionsView.as_view(), name='active-sessions'),
    path('sessions/user/<str:user_id>/', UserSessionsView.as_view(), name='user-sessions'),
    path('sessions/statistics/', SessionStatisticsView.as_view(), name='session-statistics'),

    # API Documentation
    path('docs/', APIDocumentationView.as_view(), name='api-documentation'),
]