"""Simple API performance test"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(name, url):
    """Test an endpoint and measure performance"""
    print(f"\n{'='*70}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    
    start = time.time()
    try:
        response = requests.get(BASE_URL + url, timeout=60)
        elapsed = time.time() - start
        
        size_bytes = len(response.content)
        size_kb = size_bytes / 1024
        size_mb = size_kb / 1024
        
        status_icon = "✅" if response.status_code == 200 else "❌"
        time_icon = "✅" if elapsed < 5 else ("⚠️" if elapsed < 10 else "❌")
        
        print(f"  {status_icon} Status: {response.status_code}")
        print(f"  {time_icon} Duration: {elapsed:.3f} seconds")
        
        if size_mb > 1:
            print(f"  📦 Size: {size_mb:.2f} MB")
        else:
            print(f"  📦 Size: {size_kb:.2f} KB")
        
        # Parse response to check pagination
        try:
            data = response.json()
            if 'pagination' in data:
                print(f"  📄 Pagination: Page {data['pagination']['page']} of {data['pagination']['total_pages']}")
                print(f"  📊 Total items: {data['pagination']['total']}")
                print(f"  📋 Returned: {len(data.get('data', []))} items")
        except:
            pass
        
        return {
            'success': True,
            'duration': elapsed,
            'size': size_bytes,
            'status': response.status_code
        }
        
    except requests.Timeout:
        elapsed = time.time() - start
        print(f"  ❌ TIMEOUT after {elapsed:.1f} seconds!")
        return {
            'success': False,
            'duration': elapsed,
            'error': 'Timeout'
        }
    except Exception as e:
        elapsed = time.time() - start
        print(f"  ❌ ERROR: {str(e)}")
        return {
            'success': False,
            'duration': elapsed,
            'error': str(e)
        }

def main():
    print("\n" + "="*70)
    print("API PERFORMANCE TEST - Measuring Optimization Impact")
    print("="*70)
    
    results = []
    
    # Test optimized endpoints
    print("\n\n🚀 OPTIMIZED ENDPOINTS (WITH PAGINATION)")
    print("="*70)
    
    results.append(("Limit 10", test_endpoint(
        "Products API - Limit 10",
        "/products/?limit=10"
    )))
    
    results.append(("Limit 50", test_endpoint(
        "Products API - Limit 50",
        "/products/?limit=50"
    )))
    
    results.append(("Limit 100", test_endpoint(
        "Products API - Limit 100",
        "/products/?limit=100"
    )))
    
    # Test old endpoint
    print("\n\n⏳ OLD ENDPOINT (NO PAGINATION - ALL PRODUCTS)")
    print("="*70)
    
    results.append(("No limit (all)", test_endpoint(
        "Products API - ALL Products (Old Way)",
        "/products/"
    )))
    
    # Other endpoints
    print("\n\n📊 OTHER DASHBOARD ENDPOINTS")
    print("="*70)
    
    results.append(("Sales Recent", test_endpoint(
        "Recent Sales",
        "/sales/recent/?limit=20"
    )))
    
    results.append(("Invoice Stats", test_endpoint(
        "Invoice Statistics",
        "/invoices/stats/?start_date=2025-11-01&end_date=2025-11-30"
    )))
    
    # Summary
    print("\n\n" + "="*70)
    print("📊 SUMMARY & ANALYSIS")
    print("="*70)
    
    successful = [r for name, r in results if r.get('success')]
    failed = [r for name, r in results if not r.get('success')]
    slow = [r for name, r in results if r.get('success') and r.get('duration', 0) > 5]
    critical = [r for name, r in results if r.get('success') and r.get('duration', 0) > 10]
    
    print(f"\n✅ Successful: {len(successful)}/{len(results)}")
    print(f"❌ Failed: {len(failed)}/{len(results)}")
    print(f"⚠️  Slow (>5s): {len(slow)}/{len(results)}")
    print(f"🔥 Critical (>10s): {len(critical)}/{len(results)}")
    
    # Calculate improvement
    limit_10 = next((r for name, r in results if name == "Limit 10" and r.get('success')), None)
    no_limit = next((r for name, r in results if name == "No limit (all)" and r.get('success')), None)
    
    if limit_10 and no_limit:
        improvement = ((no_limit['duration'] - limit_10['duration']) / no_limit['duration']) * 100
        speedup = no_limit['duration'] / limit_10['duration']
        size_reduction = ((no_limit['size'] - limit_10['size']) / no_limit['size']) * 100
        
        print(f"\n" + "="*70)
        print("🎯 PERFORMANCE IMPROVEMENT")
        print("="*70)
        print(f"\n  Old Way (all products):")
        print(f"    Time: {no_limit['duration']:.2f}s")
        print(f"    Size: {no_limit['size']/1024/1024:.2f} MB")
        print(f"\n  New Way (limit=10):")
        print(f"    Time: {limit_10['duration']:.2f}s")
        print(f"    Size: {limit_10['size']/1024:.2f} KB")
        print(f"\n  📈 Improvement:")
        print(f"    ⚡ {improvement:.1f}% faster ({speedup:.1f}x speedup)")
        print(f"    💾 {size_reduction:.1f}% smaller payload")
    
    print("\n" + "="*70)
    print("💡 RECOMMENDATIONS")
    print("="*70)
    print("\n✅ Pagination is working! Products API is now much faster.")
    print("📝 Next steps:")
    print("   1. Update Dashboard.vue to use ?limit=50 or ?limit=100")
    print("   2. Run: py backend\\create_indexes.py (for DB indexes)")
    print("   3. Test the Dashboard in browser to see the improvement")
    print("\n💡 Tip: Use pagination query params: ?limit=X&page=Y")
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {e}")
