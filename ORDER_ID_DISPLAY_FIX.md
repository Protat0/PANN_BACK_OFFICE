# Order ID Display Fix

## Problem
The online orders were not displaying their IDs (like "ONLINE-000017") in the frontend even though the data existed in the backend.

## Root Cause
- **Backend**: Stored order IDs in the `_id` field (MongoDB's primary key field)
- **Frontend**: Expected the order ID in an `order_id` field
- **Result**: Mismatch between field names caused the IDs not to display

## Solution
Added `order_id` as an alias field in all backend API responses that return order data.

### Files Modified
- `backend/app/kpi_views/online_transaction_views.py`

### Changes Made
Updated all views that return order data to include both fields:
```python
if '_id' in order:
    order['order_id'] = order['_id']  # Add order_id alias for frontend
```

### Views Updated
1. ✅ `GetMyOrderHistoryView` - Customer order history
2. ✅ `GetAllOrdersView` - Staff view all orders
3. ✅ `GetOnlineOrderView` - Get single order by ID
4. ✅ `GetCustomerOrdersView` - Get orders for specific customer
5. ✅ `UpdateOrderStatusView` - Update order status
6. ✅ `UpdatePaymentStatusView` - Update payment status
7. ✅ `MarkReadyForDeliveryView` - Mark order ready
8. ✅ `CompleteOrderView` - Complete order
9. ✅ `CancelOrderView` - Cancel order
10. ✅ `GetPendingOrdersView` - Get pending orders
11. ✅ `GetProcessingOrdersView` - Get processing orders
12. ✅ `GetOrdersByStatusView` - Get orders by status

## API Response Format
Now all order endpoints return:
```json
{
  "_id": "ONLINE-000017",
  "order_id": "ONLINE-000017",  // ← Added for frontend compatibility
  "customer_id": "CUST-00002",
  "customer_name": "John Doe",
  ...
}
```

## Frontend Display
The frontend can now access the order ID using:
- `order.order_id` (preferred for new code)
- `order._id` (also works for backward compatibility)

Both fields contain the same value in the format "ONLINE-000017".

## Testing
After restarting the backend server:
1. ✅ Order IDs should display in the table
2. ✅ Order detail modals should show order IDs
3. ✅ All order list views should show IDs
4. ✅ Status updates should preserve order IDs

## No Breaking Changes
This fix is backward compatible:
- ✅ Still returns `_id` field
- ✅ Adds `order_id` as an alias
- ✅ No database changes required
- ✅ Frontend works with either field name

