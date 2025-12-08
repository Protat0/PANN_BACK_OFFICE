"""
MongoDB Atlas Performance Test
Tests various product-related queries and measures response times
"""
import sys
import os
import time
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import db_manager

def format_time(seconds):
    """Format time in a readable way"""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    return f"{seconds:.2f}s"

def test_connection():
    """Test basic MongoDB connection"""
    print("\n" + "="*70)
    print("🔌 TEST 1: MongoDB Connection")
    print("="*70)
    
    start = time.time()
    try:
        db = db_manager.get_database()
        elapsed = time.time() - start
        print(f"✅ Connected to database: {db.name}")
        print(f"⏱️  Connection time: {format_time(elapsed)}")
        return db
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Connection failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return None

def test_count_products(db):
    """Test counting all products"""
    print("\n" + "="*70)
    print("📊 TEST 2: Count All Products")
    print("="*70)
    
    start = time.time()
    try:
        count = db.products.count_documents({})
        elapsed = time.time() - start
        print(f"✅ Total products: {count}")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return count
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return 0

def test_fetch_all_products(db):
    """Test fetching ALL products (the old way)"""
    print("\n" + "="*70)
    print("🚨 TEST 3: Fetch ALL Products (Old Method - SLOW)")
    print("="*70)
    
    start = time.time()
    try:
        products = list(db.products.find({}))
        elapsed = time.time() - start
        
        # Calculate approximate size
        import sys
        size_bytes = sys.getsizeof(str(products))
        size_mb = size_bytes / (1024 * 1024)
        
        print(f"✅ Fetched {len(products)} products")
        print(f"📦 Approximate data size: {size_mb:.2f}MB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        print(f"⚠️  THIS IS THE OLD SLOW METHOD!")
        return products
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_fetch_limited_products(db, limit=10):
    """Test fetching limited products (optimized)"""
    print("\n" + "="*70)
    print(f"✅ TEST 4: Fetch {limit} Products (Optimized - WITH LIMIT)")
    print("="*70)
    
    start = time.time()
    try:
        products = list(db.products.find({}).limit(limit))
        elapsed = time.time() - start
        
        import sys
        size_bytes = sys.getsizeof(str(products))
        size_kb = size_bytes / 1024
        
        print(f"✅ Fetched {len(products)} products")
        print(f"📦 Approximate data size: {size_kb:.2f}KB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return products
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_fetch_specific_products(db, product_ids):
    """Test fetching specific products by ID (Sales Display optimization)"""
    print("\n" + "="*70)
    print(f"✅ TEST 5: Fetch Specific Products by ID ($in query)")
    print("="*70)
    
    start = time.time()
    try:
        products = list(db.products.find({
            '$or': [
                {'_id': {'$in': product_ids}},
                {'product_id': {'$in': product_ids}}
            ]
        }))
        elapsed = time.time() - start
        
        import sys
        size_bytes = sys.getsizeof(str(products))
        size_kb = size_bytes / 1024
        
        print(f"✅ Requested {len(product_ids)} product IDs")
        print(f"✅ Fetched {len(products)} products")
        print(f"📦 Approximate data size: {size_kb:.2f}KB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return products
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_fetch_with_filter(db):
    """Test fetching products with filters (common query pattern)"""
    print("\n" + "="*70)
    print("🔍 TEST 6: Fetch Products with Filters (isDeleted=False)")
    print("="*70)
    
    start = time.time()
    try:
        products = list(db.products.find({'isDeleted': False}).limit(50))
        elapsed = time.time() - start
        
        import sys
        size_bytes = sys.getsizeof(str(products))
        size_kb = size_bytes / 1024
        
        print(f"✅ Fetched {len(products)} non-deleted products")
        print(f"📦 Approximate data size: {size_kb:.2f}KB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return products
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_fetch_categories(db):
    """Test fetching categories (small dataset)"""
    print("\n" + "="*70)
    print("📂 TEST 7: Fetch All Categories")
    print("="*70)
    
    start = time.time()
    try:
        categories = list(db.category.find({}))
        elapsed = time.time() - start
        
        import sys
        size_bytes = sys.getsizeof(str(categories))
        size_kb = size_bytes / 1024
        
        print(f"✅ Fetched {len(categories)} categories")
        print(f"📦 Approximate data size: {size_kb:.2f}KB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return categories
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_fetch_batches(db, product_ids):
    """Test fetching batches for specific products"""
    print("\n" + "="*70)
    print("📦 TEST 8: Fetch Batches for Specific Products")
    print("="*70)
    
    start = time.time()
    try:
        batches = list(db.batches.find({'product_id': {'$in': product_ids}}))
        elapsed = time.time() - start
        
        import sys
        size_bytes = sys.getsizeof(str(batches))
        size_kb = size_bytes / 1024
        
        print(f"✅ Requested batches for {len(product_ids)} products")
        print(f"✅ Fetched {len(batches)} batches")
        print(f"📦 Approximate data size: {size_kb:.2f}KB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return batches
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_sales_query(db):
    """Test querying sales (simulating Dashboard query)"""
    print("\n" + "="*70)
    print("💰 TEST 9: Fetch Recent Sales (Last 30 Days)")
    print("="*70)
    
    from datetime import timedelta
    
    start = time.time()
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        query_filter = {
            'transaction_date': {
                '$gte': start_date,
                '$lte': end_date
            },
            'status': {'$ne': 'voided'}
        }
        
        sales = list(db.sales.find(query_filter))
        elapsed = time.time() - start
        
        import sys
        size_bytes = sys.getsizeof(str(sales))
        size_kb = size_bytes / 1024
        
        print(f"✅ Fetched {len(sales)} sales records")
        print(f"📦 Approximate data size: {size_kb:.2f}KB")
        print(f"⏱️  Query time: {format_time(elapsed)}")
        return sales
    except Exception as e:
        elapsed = time.time() - start
        print(f"❌ Query failed: {e}")
        print(f"⏱️  Failed after: {format_time(elapsed)}")
        return []

def test_index_usage(db):
    """Test if indexes are being used"""
    print("\n" + "="*70)
    print("🔍 TEST 10: Check Index Usage")
    print("="*70)
    
    try:
        # Check products indexes
        print("\n📊 Products Collection Indexes:")
        product_indexes = list(db.products.list_indexes())
        for idx in product_indexes:
            print(f"  - {idx['name']}")
        
        # Check sales indexes
        print("\n💰 Sales Collection Indexes:")
        sales_indexes = list(db.sales.list_indexes())
        for idx in sales_indexes:
            print(f"  - {idx['name']}")
        
        # Check batches indexes
        print("\n📦 Batches Collection Indexes:")
        batches_indexes = list(db.batches.list_indexes())
        for idx in batches_indexes:
            print(f"  - {idx['name']}")
            
    except Exception as e:
        print(f"❌ Failed to check indexes: {e}")

def main():
    """Run all performance tests"""
    print("\n" + "="*70)
    print("🚀 MongoDB Atlas Performance Test Suite")
    print("="*70)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    total_start = time.time()
    
    # Test 1: Connection
    db = test_connection()
    if db is None:
        print("\n❌ Cannot proceed without database connection!")
        return
    
    # Test 2: Count products
    total_products = test_count_products(db)
    
    # Test 3: Fetch ALL products (THE SLOW OLD WAY)
    print("\n⚠️  WARNING: The next test will fetch ALL products - this will be SLOW!")
    time.sleep(2)  # Give user time to read
    all_products = test_fetch_all_products(db)
    
    # Test 4: Fetch limited products
    test_fetch_limited_products(db, limit=10)
    test_fetch_limited_products(db, limit=50)
    test_fetch_limited_products(db, limit=100)
    
    # Test 5: Fetch specific products (simulate Sales Display Service)
    if all_products:
        # Get first 10 product IDs
        product_ids = [p.get('product_id') or p.get('_id') for p in all_products[:10]]
        test_fetch_specific_products(db, product_ids)
    
    # Test 6: Fetch with filters
    test_fetch_with_filter(db)
    
    # Test 7: Fetch categories
    test_fetch_categories(db)
    
    # Test 8: Fetch batches
    if all_products:
        product_ids = [p.get('product_id') or p.get('_id') for p in all_products[:20]]
        test_fetch_batches(db, product_ids)
    
    # Test 9: Sales query
    test_sales_query(db)
    
    # Test 10: Check indexes
    test_index_usage(db)
    
    # Summary
    total_elapsed = time.time() - total_start
    print("\n" + "="*70)
    print("📊 PERFORMANCE TEST SUMMARY")
    print("="*70)
    print(f"✅ All tests completed!")
    print(f"⏱️  Total test duration: {format_time(total_elapsed)}")
    print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n💡 KEY FINDINGS:")
    print("   - Check the response times above")
    print("   - Compare 'Fetch ALL Products' vs 'Fetch Limited Products'")
    print("   - Note which queries are slowest")
    print("   - Anything over 1-2 seconds indicates a bottleneck")
    print("\n" + "="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

