# Checking Live Backend Logs

Since your backend is already running, here's how to check the logs:

## 🔍 Option 1: Check Backend Terminal/Console

If the backend is running in a terminal window:

1. **Find the terminal/console** where the backend is running
2. **Navigate to Order History** in your frontend (http://localhost:8080 or wherever it's running)
3. **Watch the terminal** - you should see new log entries appear

Look for:
```
=== ORDER HISTORY REQUEST ===
User: <username>
✅ Customer ID extracted: CUST-XXXXX
📦 Service returned: <class 'list'> with X items
```

---

## 🔄 Option 2: Restart Backend (to load new endpoint & logging)

**The new endpoint `/online/orders/history/` won't work until you restart the backend!**

### If using Command Prompt/PowerShell:
```bash
# Stop the current backend (Ctrl+C in the terminal)
# Then restart:
cd C:\Users\nemen\Documents\USC\2025\IT\Capstone\PANN_BACK_OFFICE\backend
python manage.py runserver
```

### If using VS Code or another IDE:
- Stop the running server
- Start it again

### If running as a service:
- Restart the Django service

---

## 🌐 Option 3: Check Browser Network Tab (Easiest)

You can diagnose without touching the backend:

1. **Open your frontend** (wherever `npm run serve` is serving it)
2. **Open DevTools** (F12)
3. **Go to Network tab**
4. **Navigate to Order History page**
5. **Look for the request to** `/api/v1/online/orders/history/`

### What to check:

#### ✅ If you see the request:
- **Status Code:**
  - `200` = Success (check response body for orders)
  - `401` = Not authenticated (need to re-login)
  - `404` = Endpoint not found (backend needs restart)
  - `500` = Server error (check backend logs)

- **Response Preview:**
  Click on the request → Preview tab
  ```json
  {
    "success": true,
    "results": [
      { "order_id": "ONLINE-000123", ... }
    ],
    "count": 5
  }
  ```

#### ❌ If you DON'T see the request:
- The frontend isn't calling the API
- Check browser Console for errors

---

## 🧪 Quick Test: Is the endpoint working?

**Test the endpoint directly** (in browser or Postman):

1. **Get your JWT token:**
   ```javascript
   // In browser console (F12)
   localStorage.getItem('access_token')
   ```
   Copy the token value

2. **Test in browser address bar OR Postman:**
   ```
   GET http://localhost:8000/api/v1/online/orders/history/
   
   Headers:
   Authorization: Bearer <paste_your_token_here>
   ```

3. **Expected response:**
   ```json
   {
     "success": true,
     "results": [ /* your orders */ ],
     "count": 5
   }
   ```

---

## 📊 Browser Console Debugging

Open browser console and run this to see detailed info:

```javascript
// Check if orders API is working
ordersAPI.getAll().then(result => {
  console.log('📦 Orders result:', result);
  console.log('Success:', result.success);
  console.log('Count:', result.results?.length || 0);
  if (result.results?.length > 0) {
    console.log('First order:', result.results[0]);
  } else {
    console.log('❌ No orders returned');
  }
});
```

---

## 🎯 Most Likely Issue

Since the backend is already running, it likely **hasn't loaded the new endpoint** yet.

**The new `/online/orders/history/` endpoint I added won't work until you restart the Django server!**

### Quick Fix:
1. **Stop the backend** (find the terminal running it, press Ctrl+C)
2. **Start it again:**
   ```bash
   cd C:\Users\nemen\Documents\USC\2025\IT\Capstone\PANN_BACK_OFFICE\backend
   python manage.py runserver
   ```
3. **Refresh your frontend** (Ctrl+F5)
4. **Navigate to Order History**

---

## 📤 Share This Info

To help you debug, please share:

1. **Browser Network tab screenshot** showing:
   - The request to `/online/orders/history/`
   - Status code
   - Response body (if any)

2. **Browser Console output** after running:
   ```javascript
   console.log('Token:', localStorage.getItem('access_token') ? 'Exists' : 'Missing');
   ordersAPI.getAll().then(r => console.log('API result:', r));
   ```

3. **Backend terminal output** (if accessible) when you visit Order History

---

**Bottom line:** The backend needs to be restarted to load the new endpoint! 🔄

