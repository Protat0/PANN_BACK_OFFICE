"""
Test Performance With and Without Images
Compare fetch times to see the dramatic improvement
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import db_manager

print("=" * 70)
print("📊 TESTING: Products WITH vs WITHOUT Images")
print("=" * 70)

try:
    db = db_manager.get_database()
    
    # Test 1: Fetch 10 products WITH images (old way)
    print("\n1. Fetching 10 products WITH images (old way)...")
    start = time.time()
    products_with_images = list(db.products.find({}).limit(10))
    elapsed_with = time.time() - start
    
    # Calculate size
    import sys as sys_module
    size_with = sys_module.getsizeof(str(products_with_images))
    size_with_mb = size_with / (1024 * 1024)
    
    print(f"   ✅ Fetched: {len(products_with_images)} products")
    print(f"   📦 Data size: {size_with_mb:.2f} MB")
    print(f"   ⏱️  Time: {elapsed_with:.3f}s")
    
    # Test 2: Fetch 10 products WITHOUT images (new way)
    print("\n2. Fetching 10 products WITHOUT images (optimized)...")
    projection = {
        'image_url': 0,
        'image_filename': 0,
        'image_type': 0,
        'image_size': 0
    }
    
    start = time.time()
    products_without_images = list(db.products.find({}, projection).limit(10))
    elapsed_without = time.time() - start
    
    # Calculate size
    size_without = sys_module.getsizeof(str(products_without_images))
    size_without_kb = size_without / 1024
    
    print(f"   ✅ Fetched: {len(products_without_images)} products")
    print(f"   📦 Data size: {size_without_kb:.2f} KB")
    print(f"   ⏱️  Time: {elapsed_without:.3f}s")
    
    # Test 3: Fetch 100 products WITH images
    print("\n3. Fetching 100 products WITH images...")
    start = time.time()
    products_100_with = list(db.products.find({}).limit(100))
    elapsed_100_with = time.time() - start
    print(f"   ✅ Fetched: {len(products_100_with)} products")
    print(f"   ⏱️  Time: {elapsed_100_with:.3f}s")
    
    # Test 4: Fetch 100 products WITHOUT images
    print("\n4. Fetching 100 products WITHOUT images...")
    start = time.time()
    products_100_without = list(db.products.find({}, projection).limit(100))
    elapsed_100_without = time.time() - start
    print(f"   ✅ Fetched: {len(products_100_without)} products")
    print(f"   ⏱️  Time: {elapsed_100_without:.3f}s")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 PERFORMANCE COMPARISON")
    print("=" * 70)
    
    print(f"\n10 Products:")
    print(f"  WITH images:    {elapsed_with:.3f}s ({size_with_mb:.2f} MB)")
    print(f"  WITHOUT images: {elapsed_without:.3f}s ({size_without_kb:.2f} KB)")
    speedup_10 = elapsed_with / elapsed_without if elapsed_without > 0 else 0
    size_reduction_10 = ((size_with - size_without) / size_with * 100) if size_with > 0 else 0
    print(f"  ⚡ Speedup: {speedup_10:.1f}x faster")
    print(f"  📉 Size reduction: {size_reduction_10:.1f}%")
    
    print(f"\n100 Products:")
    print(f"  WITH images:    {elapsed_100_with:.3f}s")
    print(f"  WITHOUT images: {elapsed_100_without:.3f}s")
    speedup_100 = elapsed_100_with / elapsed_100_without if elapsed_100_without > 0 else 0
    print(f"  ⚡ Speedup: {speedup_100:.1f}x faster")
    
    print("\n" + "=" * 70)
    print("✅ CONCLUSION")
    print("=" * 70)
    
    if speedup_10 > 5:
        print(f"\n🎉 EXCELLENT! Excluding images gives {speedup_10:.0f}x performance boost!")
        print("   This will make your Dashboard load MUCH faster!")
    elif speedup_10 > 2:
        print(f"\n✅ GOOD! Excluding images gives {speedup_10:.1f}x performance boost!")
    else:
        print(f"\n⚠️  Modest improvement: {speedup_10:.1f}x faster")
        print("   Note: Network latency may still be a factor with cloud DB")
    
    print(f"\n💡 Data transfer reduction: {size_reduction_10:.0f}%")
    print("   This means less bandwidth usage and faster API responses!")
    
    print("\n" + "=" * 70)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

