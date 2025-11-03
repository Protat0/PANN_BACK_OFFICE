# Order History Not Showing - Debug Guide

## 🔍 Diagnostic Steps

I've added extensive logging to help diagnose why your order history isn't showing. Follow these steps:

### Step 1: Check Backend Logs

1. **Open your backend terminal** (where Django is running)
2. **Navigate to Order History** in the frontend
3. **Look for these log messages:**

```
=== ORDER HISTORY REQUEST ===
User: <username>
User authenticated: True/False
User ID: <user_id>
Has 'customer' attribute: True/False
✅ Customer ID extracted: CUST-XXXXX
✅ Customer email: user@example.com
Query params: status=None, limit=50, offset=0
📞 Calling service.get_customer_orders(customer_id=CUST-XXXXX)
📦 Service returned: <class 'list'> with X items
  - Order: ONLINE-000XXX | Status: pending | Customer: CUST-XXXXX
✅ FINAL: Found X orders for customer CUST-XXXXX
```

### Step 2: Check Browser Console

1. **Open browser DevTools** (F12)
2. **Go to Console tab**
3. **Navigate to Order History**
4. **Look for these messages:**

```javascript
📦 Loading orders from database...
🔑 Using JWT token from localStorage
🔍 Attempting to fetch from API endpoint: /api/v1/online/orders/history/
📡 API Response: { success: true, results: [...], count: X }
✅ Loaded X orders from database
```

### Step 3: Check Network Tab

1. **Open DevTools → Network tab**
2. **Navigate to Order History**
3. **Look for request to** `/api/v1/online/orders/history/`
4. **Check:**
   - Status Code (should be 200)
   - Response body (should have `success: true` and `results` array)
   - Request Headers (should have `Authorization: Bearer <token>`)

---

## 🐛 Common Issues & Solutions

### Issue 1: "User not authenticated" (401 Error)

**Symptoms:**
- Backend logs show: `❌ User not authenticated`
- Browser shows: `🔐 Authentication error - JWT token may be expired`

**Solution:**
```javascript
// In browser console, check if token exists:
localStorage.getItem('access_token')

// If null or expired, login again
```

### Issue 2: "Customer profile not found" (404 Error)

**Symptoms:**
- Backend logs show: `❌ User X has no customer attribute`
- User is authenticated but doesn't have customer profile

**Solution:**
The user account needs to be linked to a customer profile. Check:
1. Does the user have a customer record in MongoDB?
2. Is the `customer` field properly linked in the User model?

### Issue 3: "No orders found" (Returns empty array)

**Symptoms:**
- Backend logs show: `📦 Service returned: <class 'list'> with 0 items`
- User has customer profile but no orders returned

**Possible causes:**
1. **Wrong customer_id** - Check if the customer_id in backend logs matches the customer_id in your orders
2. **Orders in wrong collection** - Orders should be in `online_orders` collection
3. **Field name mismatch** - Check if orders use `customer_id` field (not `user_id` or something else)

**Debug:**
```python
# In MongoDB Compass or shell:
db.online_orders.find({ customer_id: "CUST-XXXXX" })  # Replace with your customer_id from logs
```

### Issue 4: Endpoint not found (404 Error)

**Symptoms:**
- Browser shows: `🔍 Endpoint not found`
- Network tab shows 404 for `/api/v1/online/orders/history/`

**Solution:**
Backend server needs to be restarted to load the new endpoint:
```bash
cd backend
python manage.py runserver
```

---

## 📋 Quick Checklist

Run through this checklist:

- [ ] Backend server is running
- [ ] User is logged in (token exists in localStorage)
- [ ] User has a customer profile (`user.customer` exists)
- [ ] Orders exist in `online_orders` collection
- [ ] Orders have `customer_id` field matching your customer ID
- [ ] Endpoint `/online/orders/history/` returns 200 status
- [ ] Response has `success: true` and `results` array

---

## 🛠️ Manual Database Check

If you want to manually verify orders in the database:

### Using MongoDB Compass:
1. Connect to your database
2. Open `online_orders` collection
3. Look for documents with your `customer_id`
4. Check the structure:
   ```json
   {
     "order_id": "ONLINE-000123",
     "customer_id": "CUST-00015",  // ← This must match!
     "order_status": "pending",
     "items": [...],
     "transaction_date": "2025-11-01T..."
   }
   ```

### Using MongoDB Shell:
```javascript
// Count orders for your customer
db.online_orders.count({ customer_id: "CUST-00015" })

// View orders
db.online_orders.find({ customer_id: "CUST-00015" }).pretty()

// Check all customer_ids in orders
db.online_orders.distinct("customer_id")
```

---

## 📤 What to Share for Help

If the issue persists, please share:

1. **Backend logs** (the section starting with `=== ORDER HISTORY REQUEST ===`)
2. **Browser console logs** (especially API response)
3. **Network tab screenshot** showing the request to `/online/orders/history/`
4. **Database query result:**
   ```javascript
   db.online_orders.count({ customer_id: "YOUR_CUSTOMER_ID" })
   ```

---

## 🎯 Expected Flow

When everything works correctly:

1. Frontend calls `/api/v1/online/orders/history/` with JWT token
2. Backend extracts user from JWT → gets customer_id
3. Queries `online_orders` collection for that customer_id
4. Returns array of orders
5. Frontend displays in OrderHistory.vue

**The logs will show exactly where this flow breaks!**

---

## 💡 Pro Tips

### Enable Debug Mode
Add this to your frontend to see more details:
```javascript
// In browser console
localStorage.setItem('VITE_DEBUG_CART', 'true')
```

### Check JWT Token
```javascript
// Decode JWT to see user info
const token = localStorage.getItem('access_token')
console.log(JSON.parse(atob(token.split('.')[1])))
```

### Force Reload
Sometimes caching causes issues:
1. Hard refresh: Ctrl+Shift+R
2. Clear localStorage: `localStorage.clear()` (then re-login)
3. Restart backend server

---

**Last Updated:** November 1, 2025  
**Status:** Awaiting diagnostic logs

