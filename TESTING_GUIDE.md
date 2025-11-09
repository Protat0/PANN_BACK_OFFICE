# Online Orders - Quick Testing Guide

## 🚀 Quick Start

### Step 1: Start the Backend
```bash
cd backend
python manage.py runserver
```
Backend should be running on `http://localhost:8000`

### Step 2: Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend should be running on `http://localhost:5173` (or similar)

### Step 3: Login to Back Office
1. Open browser to frontend URL
2. Login with your admin credentials
3. You should see the dashboard

## ✅ Test Checklist

### Test 1: Navigation & Page Load
- [ ] Click "Online Orders" in the sidebar (shopping cart icon)
- [ ] Page loads without errors
- [ ] Statistics cards show numbers
- [ ] Orders table displays (or empty state if no orders)

### Test 2: Create Test Order (via API or Frontend)
If no orders exist, create a test order:

**Option A: Via Backend Admin or API**
```bash
# Example using curl
curl -X POST http://localhost:8000/api/v1/online-orders/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-00001",
    "items": [
      {
        "product_id": "product_id_here",
        "product_name": "Test Product",
        "quantity": 2,
        "price": 100.00
      }
    ],
    "subtotal": 200.00,
    "delivery_fee": 50.00,
    "service_fee": 10.00,
    "total_amount": 260.00,
    "payment_method": "cod",
    "delivery_address": "Test Address"
  }'
```

**Option B: Via Customer Frontend (if available)**
- Go to customer-facing site
- Login as a customer
- Add items to cart
- Place an order
- Note the Order ID

### Test 3: View Order Details
- [ ] Click on an order in the table
- [ ] Order details modal opens
- [ ] All information displays correctly:
  - Order ID
  - Customer ID
  - Order date
  - Items list
  - Pricing (subtotal, fees, total)
  - Current status
  - Payment status

### Test 4: Update Order Status
- [ ] In order details modal, scroll to "Update Order Status"
- [ ] Change "Order Status" from "Pending" to "Confirmed"
- [ ] Add a note: "Order confirmed by admin"
- [ ] Click "💾 Save Changes"
- [ ] Success message appears
- [ ] Close modal
- [ ] Order status in table now shows "Confirmed" badge
- [ ] Reopen order
- [ ] Check "Status History" section shows the update

### Test 5: Update Payment Status
- [ ] Open an order with payment status "Pending"
- [ ] Change "Payment Status" to "Paid"
- [ ] Save changes
- [ ] Payment badge updates from yellow to green

### Test 6: Status Progression
Test the full order workflow:
- [ ] Create new order (status: Pending)
- [ ] Update to: Confirmed
- [ ] Update to: Preparing
- [ ] Update to: Ready
- [ ] Update to: Out for Delivery
- [ ] Update to: Delivered
- [ ] Update to: Completed

### Test 7: Filters
- [ ] Use "Status Filter" dropdown
- [ ] Select "Pending"
- [ ] Only pending orders show
- [ ] Select "Completed"
- [ ] Only completed orders show
- [ ] Click "Clear Filters"
- [ ] All orders return

### Test 8: Customer ID Search
- [ ] Enter a customer ID in "Search Customer" field
- [ ] Orders filter to that customer
- [ ] Clear search
- [ ] All orders return

### Test 9: Auto-Refresh
- [ ] Open Online Orders page
- [ ] Create a new order in another tab/browser
- [ ] Wait 30 seconds
- [ ] New order should appear automatically

### Test 10: Pagination
If you have many orders:
- [ ] Navigate between pages
- [ ] Verify correct orders show on each page
- [ ] Page numbers update correctly

## 🐛 Common Issues & Solutions

### Issue: "Failed to fetch orders"
**Solution:**
- Check backend is running
- Check console for CORS errors
- Verify API_BASE_URL in frontend/.env
- Check JWT token is valid (re-login if needed)

### Issue: "Order not found"
**Solution:**
- Verify order exists in database
- Check order_id format is correct
- Verify you have permission to view order

### Issue: "Status update failed"
**Solution:**
- Check you're logged in as admin/staff
- Verify order is not already completed/cancelled
- Check backend logs for errors
- Ensure required fields are filled

### Issue: Orders not displaying
**Solution:**
- Check MongoDB is running
- Verify `online_transactions` collection exists
- Check backend console for errors
- Verify authentication token

## 📊 Expected Results

### After Implementation
✅ You should see:
1. "Online Orders" menu item in sidebar
2. Orders page loads successfully
3. Statistics dashboard shows counts
4. Orders table displays all orders
5. Clicking orders opens details modal
6. Status updates work and save
7. Auto-refresh updates data every 30 seconds

### Customer-Facing (If Implemented)
✅ Customers should see:
1. Their order history in profile/account
2. Current status of each order
3. Status updates in real-time
4. Order details when clicking on order

## 🔧 Testing with Different Order States

Create test orders in different states:

1. **Pending Order**: Just created, awaiting confirmation
2. **Confirmed Order**: Confirmed but not started
3. **Preparing Order**: Currently being prepared
4. **Ready Order**: Ready for pickup/delivery
5. **Delivered Order**: Successfully delivered
6. **Cancelled Order**: Cancelled by customer or admin

This helps test:
- Status badge colors
- Filter functionality
- Statistics accuracy
- Status progression logic

## 📝 Testing Notes Template

Use this to document your testing:

```
Date: _____________
Tester: _____________

Test 1: Navigation ☐ Pass ☐ Fail
Notes: __________________

Test 2: View Orders ☐ Pass ☐ Fail
Notes: __________________

Test 3: Order Details ☐ Pass ☐ Fail
Notes: __________________

Test 4: Status Update ☐ Pass ☐ Fail
Notes: __________________

Test 5: Filters ☐ Pass ☐ Fail
Notes: __________________

Overall Status: ☐ Pass ☐ Fail ☐ Needs Work
Issues Found: __________________
```

## 🎯 Success Criteria

All tests should:
- ✅ Execute without errors
- ✅ Display correct data
- ✅ Update data correctly
- ✅ Show appropriate feedback messages
- ✅ Handle errors gracefully
- ✅ Work on different screen sizes

## 🔍 Where to Check for Errors

1. **Browser Console** (F12):
   - Check for JavaScript errors
   - Check for network errors (red requests)
   - Verify API responses

2. **Backend Console**:
   - Check for Python exceptions
   - Verify database queries
   - Check for authentication errors

3. **Network Tab** (F12 → Network):
   - Verify API calls are made
   - Check response status codes
   - Verify request/response data

## 📞 Need Help?

If tests fail:
1. Check the error messages carefully
2. Review browser console logs
3. Review backend console logs
4. Check the ONLINE_ORDERS_IMPLEMENTATION.md file
5. Verify all files were created correctly

---

**Ready to Test!** Start with Test 1 and work through systematically. 🚀

