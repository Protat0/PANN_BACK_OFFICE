"""
Dashboard CRUD Simulation Test
Simulates the actual queries that the Dashboard makes
Tests performance WITH and WITHOUT image exclusion
"""
import sys
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure Django before importing services
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posbackend.settings')

import django
django.setup()

from app.database import db_manager

print("=" * 70)
print("📊 DASHBOARD SIMULATION TEST")
print("=" * 70)
print(f"Testing actual Dashboard queries...")
print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
print("=" * 70)

# Get database connection
db = db_manager.get_database()

# Track results
results = {
    'with_images': {},
    'without_images': {}
}

print("\n" + "="*70)
print("PART 1: Testing WITH Images (Old Way)")
print("="*70)

# Test 1: Fetch Products for List (with images)
print("\n1. Fetching products for list (WITH images)...")
start = time.time()
try:
    # Simulate fetching 100 products like Dashboard does
    products_with = list(db.products.find({}).limit(100))
    elapsed = time.time() - start
    results['with_images']['products'] = elapsed
    print(f"   ✅ Fetched {len(products_with)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['products'] = None

# Test 2: Fetch Sales Display (with images in products)
print("\n2. Fetching sales display data (WITH images)...")
start = time.time()
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # This calls the OLD version that fetches all product data
    # Temporarily use the old method
    sales = list(db.sales.find({
        'transaction_date': {'$gte': start_date, '$lte': end_date}
    }))
    
    # Get unique product IDs
    product_ids = set()
    for sale in sales:
        for item in sale.get('items', []):
            pid = item.get('product_id')
            if pid:
                product_ids.add(pid)
    
    # Fetch products WITH images (old way)
    products_for_sales = list(db.products.find({
        '$or': [
            {'_id': {'$in': list(product_ids)}},
            {'product_id': {'$in': list(product_ids)}}
        ]
    }))
    
    elapsed = time.time() - start
    results['with_images']['sales_display'] = elapsed
    print(f"   ✅ Processed {len(sales)} sales, {len(products_for_sales)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['sales_display'] = None

# Test 3: Count operations (fast, for comparison)
print("\n3. Count operations (should be fast)...")
start = time.time()
try:
    product_count = db.products.count_documents({})
    sales_count = db.sales.count_documents({})
    elapsed = time.time() - start
    results['with_images']['counts'] = elapsed
    print(f"   ✅ Products: {product_count}, Sales: {sales_count}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['counts'] = None

# Test 4: Recent sales (with product details)
print("\n4. Fetching recent sales (WITH product images)...")
start = time.time()
try:
    recent_sales = list(db.sales.find({}).sort('transaction_date', -1).limit(20))
    
    # Get product details for each sale (WITH images)
    product_ids = set()
    for sale in recent_sales:
        for item in sale.get('items', []):
            product_ids.add(item.get('product_id'))
    
    products_in_sales = list(db.products.find({
        '$or': [
            {'_id': {'$in': list(product_ids)}},
            {'product_id': {'$in': list(product_ids)}}
        ]
    }))
    
    elapsed = time.time() - start
    results['with_images']['recent_sales'] = elapsed
    print(f"   ✅ Fetched {len(recent_sales)} sales, {len(products_in_sales)} product details")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['recent_sales'] = None

# Test 5: Top Products of the Month (WITH images)
print("\n5. Fetching top products of the month (WITH product images)...")
start = time.time()
try:
    # Get current month's date range
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    if now.month == 12:
        month_end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        month_end = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
    
    # Get sales for current month
    month_sales = list(db.sales.find({
        'transaction_date': {'$gte': month_start, '$lte': month_end},
        'status': {'$ne': 'voided'}
    }))
    
    # Aggregate sales by product
    from collections import defaultdict
    product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0})
    
    for sale in month_sales:
        for item in sale.get('items', []):
            pid = item.get('product_id')
            product_sales[pid]['quantity'] += item.get('quantity', 0)
            product_sales[pid]['revenue'] += item.get('subtotal', 0)
    
    # Get top 10 product IDs
    top_product_ids = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]
    top_ids = [pid for pid, _ in top_product_ids]
    
    # Fetch product details WITH images
    top_products = list(db.products.find({
        '$or': [
            {'_id': {'$in': top_ids}},
            {'product_id': {'$in': top_ids}}
        ]
    }))
    
    elapsed = time.time() - start
    results['with_images']['top_products_month'] = elapsed
    print(f"   ✅ Analyzed {len(month_sales)} sales, found top {len(top_products)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['top_products_month'] = None

# Test 6: Total Profit (All Time)
print("\n6. Calculating total profit (all time)...")
start = time.time()
try:
    # Get all sales
    all_sales = list(db.sales.find({'status': {'$ne': 'voided'}}))
    
    total_revenue = 0
    product_ids_for_cost = set()
    quantity_by_product = defaultdict(int)
    
    for sale in all_sales:
        total_revenue += sale.get('total_amount', 0)
        for item in sale.get('items', []):
            pid = item.get('product_id')
            product_ids_for_cost.add(pid)
            quantity_by_product[pid] += item.get('quantity', 0)
    
    # Fetch products WITH images to get cost prices
    products_for_cost = list(db.products.find({
        '$or': [
            {'_id': {'$in': list(product_ids_for_cost)}},
            {'product_id': {'$in': list(product_ids_for_cost)}}
        ]
    }))
    
    # Calculate total cost
    product_costs = {p.get('product_id') or p.get('_id'): p.get('cost_price', 0) for p in products_for_cost}
    total_cost = sum(product_costs.get(pid, 0) * qty for pid, qty in quantity_by_product.items())
    total_profit = total_revenue - total_cost
    
    elapsed = time.time() - start
    results['with_images']['total_profit'] = elapsed
    print(f"   ✅ Analyzed {len(all_sales)} sales")
    print(f"   💰 Revenue: ${total_revenue:,.2f}, Profit: ${total_profit:,.2f}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['total_profit'] = None

# Test 7: Top Performing Month of the Year
print("\n7. Finding top performing month of the year (WITH images)...")
start = time.time()
try:
    # Get current year
    current_year = datetime.now().year
    year_start = datetime(current_year, 1, 1)
    year_end = datetime(current_year, 12, 31, 23, 59, 59)
    
    # Get all sales for the year
    year_sales = list(db.sales.find({
        'transaction_date': {'$gte': year_start, '$lte': year_end},
        'status': {'$ne': 'voided'}
    }))
    
    # Group by month
    monthly_revenue = defaultdict(float)
    monthly_product_ids = defaultdict(set)
    monthly_quantities = defaultdict(lambda: defaultdict(int))
    
    for sale in year_sales:
        month = sale.get('transaction_date').month
        monthly_revenue[month] += sale.get('total_amount', 0)
        
        for item in sale.get('items', []):
            pid = item.get('product_id')
            monthly_product_ids[month].add(pid)
            monthly_quantities[month][pid] += item.get('quantity', 0)
    
    # Find top month
    if monthly_revenue:
        top_month = max(monthly_revenue.items(), key=lambda x: x[1])
        top_month_num, top_revenue = top_month
        
        # Fetch products for top month WITH images
        top_month_products = list(db.products.find({
            '$or': [
                {'_id': {'$in': list(monthly_product_ids[top_month_num])}},
                {'product_id': {'$in': list(monthly_product_ids[top_month_num])}}
            ]
        }))
        
        # Calculate profit for top month
        product_costs = {p.get('product_id') or p.get('_id'): p.get('cost_price', 0) for p in top_month_products}
        top_month_cost = sum(product_costs.get(pid, 0) * qty for pid, qty in monthly_quantities[top_month_num].items())
        top_month_profit = top_revenue - top_month_cost
    else:
        top_month_num = 0
        top_revenue = 0
        top_month_profit = 0
    
    elapsed = time.time() - start
    results['with_images']['top_month'] = elapsed
    print(f"   ✅ Analyzed {len(year_sales)} sales across {len(monthly_revenue)} months")
    print(f"   📅 Top month: {top_month_num}, Revenue: ${top_revenue:,.2f}, Profit: ${top_month_profit:,.2f}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['with_images']['top_month'] = None

# Calculate total time with images
total_with = sum([v for v in results['with_images'].values() if v is not None])
print(f"\n📊 TOTAL TIME (WITH images): {total_with:.3f}s")

# ============================================================================

print("\n" + "="*70)
print("PART 2: Testing WITHOUT Images (Optimized)")
print("="*70)

# Test 1: Fetch Products for List (without images)
print("\n1. Fetching products for list (WITHOUT images)...")
start = time.time()
try:
    projection = {
        'image_url': 0,
        'image_filename': 0,
        'image_type': 0,
        'image_size': 0
    }
    products_without = list(db.products.find({}, projection).limit(100))
    elapsed = time.time() - start
    results['without_images']['products'] = elapsed
    print(f"   ✅ Fetched {len(products_without)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['products'] = None

# Test 2: Fetch Sales Display (without images in products)
print("\n2. Fetching sales display data (WITHOUT images)...")
start = time.time()
try:
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    sales = list(db.sales.find({
        'transaction_date': {'$gte': start_date, '$lte': end_date}
    }))
    
    # Get unique product IDs
    product_ids = set()
    for sale in sales:
        for item in sale.get('items', []):
            pid = item.get('product_id')
            if pid:
                product_ids.add(pid)
    
    # Fetch products WITHOUT images (optimized!)
    projection = {
        'image_url': 0,
        'image_filename': 0,
        'image_type': 0,
        'image_size': 0
    }
    
    products_for_sales = list(db.products.find({
        '$or': [
            {'_id': {'$in': list(product_ids)}},
            {'product_id': {'$in': list(product_ids)}}
        ]
    }, projection))
    
    elapsed = time.time() - start
    results['without_images']['sales_display'] = elapsed
    print(f"   ✅ Processed {len(sales)} sales, {len(products_for_sales)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['sales_display'] = None

# Test 3: Count operations (same as before)
print("\n3. Count operations (should be same)...")
start = time.time()
try:
    product_count = db.products.count_documents({})
    sales_count = db.sales.count_documents({})
    elapsed = time.time() - start
    results['without_images']['counts'] = elapsed
    print(f"   ✅ Products: {product_count}, Sales: {sales_count}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['counts'] = None

# Test 4: Recent sales (without product images)
print("\n4. Fetching recent sales (WITHOUT product images)...")
start = time.time()
try:
    recent_sales = list(db.sales.find({}).sort('transaction_date', -1).limit(20))
    
    # Get product details for each sale (WITHOUT images)
    product_ids = set()
    for sale in recent_sales:
        for item in sale.get('items', []):
            product_ids.add(item.get('product_id'))
    
    projection = {
        'image_url': 0,
        'image_filename': 0,
        'image_type': 0,
        'image_size': 0
    }
    
    products_in_sales = list(db.products.find({
        '$or': [
            {'_id': {'$in': list(product_ids)}},
            {'product_id': {'$in': list(product_ids)}}
        ]
    }, projection))
    
    elapsed = time.time() - start
    results['without_images']['recent_sales'] = elapsed
    print(f"   ✅ Fetched {len(recent_sales)} sales, {len(products_in_sales)} product details")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['recent_sales'] = None

# Test 5: Top Products of the Month (WITHOUT images)
print("\n5. Fetching top products of the month (WITHOUT product images)...")
start = time.time()
try:
    # Get current month's date range
    now = datetime.now()
    month_start = datetime(now.year, now.month, 1)
    if now.month == 12:
        month_end = datetime(now.year + 1, 1, 1) - timedelta(seconds=1)
    else:
        month_end = datetime(now.year, now.month + 1, 1) - timedelta(seconds=1)
    
    # Get sales for current month
    month_sales = list(db.sales.find({
        'transaction_date': {'$gte': month_start, '$lte': month_end},
        'status': {'$ne': 'voided'}
    }))
    
    # Aggregate sales by product
    from collections import defaultdict
    product_sales = defaultdict(lambda: {'quantity': 0, 'revenue': 0})
    
    for sale in month_sales:
        for item in sale.get('items', []):
            pid = item.get('product_id')
            product_sales[pid]['quantity'] += item.get('quantity', 0)
            product_sales[pid]['revenue'] += item.get('subtotal', 0)
    
    # Get top 10 product IDs
    top_product_ids = sorted(product_sales.items(), key=lambda x: x[1]['revenue'], reverse=True)[:10]
    top_ids = [pid for pid, _ in top_product_ids]
    
    # Fetch product details WITHOUT images (OPTIMIZED!)
    projection = {
        'image_url': 0,
        'image_filename': 0,
        'image_type': 0,
        'image_size': 0
    }
    
    top_products = list(db.products.find({
        '$or': [
            {'_id': {'$in': top_ids}},
            {'product_id': {'$in': top_ids}}
        ]
    }, projection))
    
    elapsed = time.time() - start
    results['without_images']['top_products_month'] = elapsed
    print(f"   ✅ Analyzed {len(month_sales)} sales, found top {len(top_products)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['top_products_month'] = None

# Test 6: Total Profit (All Time) WITHOUT images
print("\n6. Calculating total profit (all time) WITHOUT images...")
start = time.time()
try:
    # Get all sales
    all_sales = list(db.sales.find({'status': {'$ne': 'voided'}}))
    
    total_revenue = 0
    product_ids_for_cost = set()
    quantity_by_product = defaultdict(int)
    
    for sale in all_sales:
        total_revenue += sale.get('total_amount', 0)
        for item in sale.get('items', []):
            pid = item.get('product_id')
            product_ids_for_cost.add(pid)
            quantity_by_product[pid] += item.get('quantity', 0)
    
    # Fetch products WITHOUT images (OPTIMIZED!)
    projection = {
        'image_url': 0,
        'image_filename': 0,
        'image_type': 0,
        'image_size': 0
    }
    
    products_for_cost = list(db.products.find({
        '$or': [
            {'_id': {'$in': list(product_ids_for_cost)}},
            {'product_id': {'$in': list(product_ids_for_cost)}}
        ]
    }, projection))
    
    # Calculate total cost
    product_costs = {p.get('product_id') or p.get('_id'): p.get('cost_price', 0) for p in products_for_cost}
    total_cost = sum(product_costs.get(pid, 0) * qty for pid, qty in quantity_by_product.items())
    total_profit = total_revenue - total_cost
    
    elapsed = time.time() - start
    results['without_images']['total_profit'] = elapsed
    print(f"   ✅ Analyzed {len(all_sales)} sales")
    print(f"   💰 Revenue: ${total_revenue:,.2f}, Profit: ${total_profit:,.2f}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['total_profit'] = None

# Test 7: Top Performing Month of the Year WITHOUT images
print("\n7. Finding top performing month of the year (WITHOUT images)...")
start = time.time()
try:
    # Get current year
    current_year = datetime.now().year
    year_start = datetime(current_year, 1, 1)
    year_end = datetime(current_year, 12, 31, 23, 59, 59)
    
    # Get all sales for the year
    year_sales = list(db.sales.find({
        'transaction_date': {'$gte': year_start, '$lte': year_end},
        'status': {'$ne': 'voided'}
    }))
    
    # Group by month
    monthly_revenue = defaultdict(float)
    monthly_product_ids = defaultdict(set)
    monthly_quantities = defaultdict(lambda: defaultdict(int))
    
    for sale in year_sales:
        month = sale.get('transaction_date').month
        monthly_revenue[month] += sale.get('total_amount', 0)
        
        for item in sale.get('items', []):
            pid = item.get('product_id')
            monthly_product_ids[month].add(pid)
            monthly_quantities[month][pid] += item.get('quantity', 0)
    
    # Find top month
    if monthly_revenue:
        top_month = max(monthly_revenue.items(), key=lambda x: x[1])
        top_month_num, top_revenue = top_month
        
        # Fetch products for top month WITHOUT images (OPTIMIZED!)
        projection = {
            'image_url': 0,
            'image_filename': 0,
            'image_type': 0,
            'image_size': 0
        }
        
        top_month_products = list(db.products.find({
            '$or': [
                {'_id': {'$in': list(monthly_product_ids[top_month_num])}},
                {'product_id': {'$in': list(monthly_product_ids[top_month_num])}}
            ]
        }, projection))
        
        # Calculate profit for top month
        product_costs = {p.get('product_id') or p.get('_id'): p.get('cost_price', 0) for p in top_month_products}
        top_month_cost = sum(product_costs.get(pid, 0) * qty for pid, qty in monthly_quantities[top_month_num].items())
        top_month_profit = top_revenue - top_month_cost
    else:
        top_month_num = 0
        top_revenue = 0
        top_month_profit = 0
    
    elapsed = time.time() - start
    results['without_images']['top_month'] = elapsed
    print(f"   ✅ Analyzed {len(year_sales)} sales across {len(monthly_revenue)} months")
    print(f"   📅 Top month: {top_month_num}, Revenue: ${top_revenue:,.2f}, Profit: ${top_month_profit:,.2f}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
except Exception as e:
    print(f"   ❌ Error: {e}")
    results['without_images']['top_month'] = None

# Calculate total time without images
total_without = sum([v for v in results['without_images'].values() if v is not None])
print(f"\n📊 TOTAL TIME (WITHOUT images): {total_without:.3f}s")

# ============================================================================

print("\n" + "="*70)
print("📊 PERFORMANCE COMPARISON - DASHBOARD SIMULATION")
print("="*70)

print("\nQuery-by-Query Breakdown:")
print(f"{'Operation':<30} {'WITH Images':<15} {'WITHOUT Images':<15} {'Speedup':<10}")
print("-" * 70)

operations = [
    ('Fetch 100 Products', 'products'),
    ('Sales Display Query', 'sales_display'),
    ('Count Operations', 'counts'),
    ('Recent Sales + Products', 'recent_sales'),
    ('Top Products of Month', 'top_products_month'),
    ('Total Profit (All Time)', 'total_profit'),
    ('Top Performing Month', 'top_month')
]

for op_name, op_key in operations:
    with_time = results['with_images'].get(op_key, 0)
    without_time = results['without_images'].get(op_key, 0)
    
    if with_time and without_time and without_time > 0:
        speedup = with_time / without_time
        speedup_str = f"{speedup:.1f}x"
    else:
        speedup_str = "N/A"
    
    with_str = f"{with_time:.3f}s" if with_time else "Failed"
    without_str = f"{without_time:.3f}s" if without_time else "Failed"
    
    print(f"{op_name:<30} {with_str:<15} {without_str:<15} {speedup_str:<10}")

print("-" * 70)
print(f"{'TOTAL DASHBOARD LOAD':<30} {total_with:.3f}s{' '*7} {total_without:.3f}s{' '*7} ", end='')
if total_with > 0 and total_without > 0:
    total_speedup = total_with / total_without
    print(f"{total_speedup:.1f}x")
else:
    print("N/A")

# Analysis
print("\n" + "="*70)
print("🎯 ANALYSIS")
print("="*70)

if total_without < 10:
    print(f"\n✅ EXCELLENT! Dashboard will load in {total_without:.1f} seconds")
    print("   This is well under the 30-second timeout!")
elif total_without < 20:
    print(f"\n✅ GOOD! Dashboard will load in {total_without:.1f} seconds")
    print("   This should work, but may still feel slow.")
else:
    print(f"\n⚠️  Dashboard will take {total_without:.1f} seconds")
    print("   Consider additional optimizations (Cloudinary, caching, etc.)")

if total_with > 0 and total_without > 0:
    improvement = ((total_with - total_without) / total_with) * 100
    time_saved = total_with - total_without
    
    print(f"\n📈 IMPROVEMENT METRICS:")
    print(f"   - Time saved: {time_saved:.1f} seconds")
    print(f"   - Performance improvement: {improvement:.1f}%")
    print(f"   - Overall speedup: {total_with / total_without:.1f}x faster")

# Recommendations
print("\n" + "="*70)
print("💡 RECOMMENDATIONS")
print("="*70)

if total_without < 5:
    print("\n🎉 PERFECT! Your Dashboard is now performing great!")
    print("   ✅ No further optimizations needed for basic functionality")
    print("   💡 Consider Cloudinary migration for long-term scalability")
elif total_without < 10:
    print("\n✅ GOOD! Dashboard is functional, but could be faster:")
    print("   1. Migrate to Cloudinary (99% storage reduction)")
    print("   2. Add Redis caching for frequently accessed data")
    print("   3. Implement request caching with TTL")
else:
    print("\n⚠️  Dashboard is still slow. Additional optimizations needed:")
    print("   1. ⚠️  URGENT: Migrate to Cloudinary")
    print("   2. Add Redis caching")
    print("   3. Consider upgrading MongoDB Atlas tier")
    print("   4. Implement lazy loading for widgets")

print("\n" + "="*70)
print("✅ TEST COMPLETE")
print("="*70)
print(f"Finished: {datetime.now().strftime('%H:%M:%S')}")
print("\n💡 NEXT STEPS:")
print("   1. Restart your backend server")
print("   2. Refresh your Dashboard (Ctrl+Shift+R)")
print("   3. Dashboard should load in ~{:.0f} seconds!".format(total_without))
print("="*70)

