import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Starting MongoDB Atlas Performance Test...")
print("=" * 70)

try:
    from app.database import db_manager
    
    # Test 1: Connection
    print("\n1. Testing connection...")
    start = time.time()
    db = db_manager.get_database()
    elapsed = time.time() - start
    
    if db is None:
        print("   ❌ Failed to connect!")
        raise Exception("Database connection failed")
    
    print(f"   ✅ Connected to: {db.name}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    
    # Test 2: Count products
    print("\n2. Counting products...")
    start = time.time()
    count = db.products.count_documents({})
    elapsed = time.time() - start
    print(f"   ✅ Total products: {count}")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    
    # Test 3: Fetch 10 products (fast)
    print("\n3. Fetching 10 products...")
    start = time.time()
    products_10 = list(db.products.find({}).limit(10))
    elapsed = time.time() - start
    print(f"   ✅ Fetched: {len(products_10)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    
    # Test 4: Fetch 100 products (moderate)
    print("\n4. Fetching 100 products...")
    start = time.time()
    products_100 = list(db.products.find({}).limit(100))
    elapsed = time.time() - start
    print(f"   ✅ Fetched: {len(products_100)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    
    # Test 5: Fetch ALL products (SLOW!)
    print("\n5. Fetching ALL products (THIS WILL BE SLOW!)...")
    start = time.time()
    all_products = list(db.products.find({}))
    elapsed = time.time() - start
    print(f"   ✅ Fetched: {len(all_products)} products")
    print(f"   ⏱️  Time: {elapsed:.3f}s ⚠️")
    
    # Test 6: Fetch categories
    print("\n6. Fetching all categories...")
    start = time.time()
    categories = list(db.category.find({}))
    elapsed = time.time() - start
    print(f"   ✅ Fetched: {len(categories)} categories")
    print(f"   ⏱️  Time: {elapsed:.3f}s")
    
    # Test 7: Check indexes
    print("\n7. Checking indexes...")
    product_indexes = list(db.products.list_indexes())
    print(f"   📊 Products indexes: {len(product_indexes)}")
    for idx in product_indexes:
        print(f"      - {idx['name']}")
    
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED!")
    print("=" * 70)
    
    # Write to file
    with open('test_results_quick.txt', 'w') as f:
        f.write(f"MongoDB Atlas Test - {datetime.now()}\n")
        f.write(f"Total Products: {count}\n")
        f.write("Test completed successfully\n")
    print("\n📝 Results also saved to: test_results_quick.txt")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    
    # Write error to file
    with open('test_results_quick.txt', 'w') as f:
        f.write(f"ERROR: {e}\n")
        f.write(traceback.format_exc())

