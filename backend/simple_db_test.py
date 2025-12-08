"""Simple database connectivity and performance test"""
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from app.database import db_manager
from datetime import datetime, timedelta

print("Starting database performance tests...")
print("="*70)

# Test 1: Connection
print("\n1. Testing MongoDB connection...")
try:
    start = time.time()
    db = db_manager.get_database()
    db.client.admin.command('ping')
    elapsed = (time.time() - start) * 1000
    print(f"   ✅ Connected! Ping: {elapsed:.2f}ms")
except Exception as e:
    print(f"   ❌ Connection failed: {e}")
    sys.exit(1)

# Test 2: Collection counts
print("\n2. Checking collection sizes...")
try:
    for coll_name in ['products', 'sales_log', 'sales', 'customers']:
        if coll_name in db.list_collection_names():
            count = db[coll_name].count_documents({})
            print(f"   {coll_name}: {count:,} documents")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Products query (this is the slow one based on logs)
print("\n3. Testing products query (all documents)...")
try:
    start = time.time()
    products = list(db.products.find({}))
    elapsed = time.time() - start
    size_bytes = sys.getsizeof(str(products))
    size_mb = size_bytes / 1024 / 1024
    print(f"   Found: {len(products)} products")
    print(f"   Size: {size_mb:.2f} MB")
    print(f"   Time: {elapsed:.3f} seconds")
    if elapsed > 10:
        print(f"   ❌ CRITICAL: Query took > 10 seconds!")
    elif elapsed > 5:
        print(f"   ⚠️  WARNING: Query took > 5 seconds")
    else:
        print(f"   ✅ Performance acceptable")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Products query with limit
print("\n4. Testing products query (limited to 100)...")
try:
    start = time.time()
    products = list(db.products.find({}).limit(100))
    elapsed = time.time() - start
    print(f"   Found: {len(products)} products")
    print(f"   Time: {elapsed:.3f} seconds")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Sales aggregation
print("\n5. Testing sales aggregation (last 30 days)...")
try:
    coll_name = 'sales_log' if 'sales_log' in db.list_collection_names() else 'sales'
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    start = time.time()
    pipeline = [
        {
            '$match': {
                'transaction_date': {'$gte': start_date, '$lte': end_date},
                'status': {'$ne': 'voided'}
            }
        },
        {
            '$group': {
                '_id': None,
                'total': {'$sum': '$total_amount'},
                'count': {'$sum': 1}
            }
        }
    ]
    result = list(db[coll_name].aggregate(pipeline))
    elapsed = time.time() - start
    
    print(f"   Collection: {coll_name}")
    print(f"   Time: {elapsed:.3f} seconds")
    if result:
        print(f"   Transactions: {result[0].get('count', 0)}")
        print(f"   Total: ₱{result[0].get('total', 0):,.2f}")
    
    if elapsed > 10:
        print(f"   ❌ CRITICAL: Aggregation took > 10 seconds!")
    elif elapsed > 5:
        print(f"   ⚠️  WARNING: Aggregation took > 5 seconds")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Check indexes
print("\n6. Checking database indexes...")
try:
    for coll_name in ['products', 'sales_log', 'sales']:
        if coll_name in db.list_collection_names():
            indexes = list(db[coll_name].list_indexes())
            print(f"\n   {coll_name} indexes:")
            for idx in indexes:
                print(f"      - {idx['name']}: {idx['key']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*70)
print("Tests completed!")
print("\nKEY FINDINGS:")
print("- If products query takes > 10s, that's your bottleneck")
print("- If network ping is > 200ms, network latency is an issue")
print("- Check if important collections have proper indexes")
