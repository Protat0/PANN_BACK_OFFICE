"""
Database Performance Diagnostic Tool
Tests connection latency, query performance, and identifies bottlenecks
"""
import time
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path to import Django settings
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from app.database import db_manager
from decouple import config

class DatabasePerformanceTest:
    def __init__(self):
        self.db = db_manager.get_database()
        self.results = []
    
    def test(self, name, func):
        """Run a test and measure time"""
        print(f"\n{'='*60}")
        print(f"Testing: {name}")
        print(f"{'='*60}")
        start = time.time()
        try:
            result = func()
            elapsed = time.time() - start
            status = "✅ PASS"
            print(f"{status} - Time: {elapsed:.3f}s")
            self.results.append({
                'test': name,
                'status': 'PASS',
                'time': elapsed,
                'result': result
            })
            return result, elapsed
        except Exception as e:
            elapsed = time.time() - start
            status = "❌ FAIL"
            print(f"{status} - Time: {elapsed:.3f}s")
            print(f"Error: {str(e)}")
            self.results.append({
                'test': name,
                'status': 'FAIL',
                'time': elapsed,
                'error': str(e)
            })
            return None, elapsed
    
    def test_connection_latency(self):
        """Test basic connection ping"""
        def ping():
            start = time.time()
            self.db.client.admin.command('ping')
            latency = (time.time() - start) * 1000  # Convert to ms
            print(f"   Ping latency: {latency:.2f}ms")
            return latency
        return ping()
    
    def test_collection_counts(self):
        """Get document counts for all collections"""
        def count_all():
            collections = self.db.list_collection_names()
            counts = {}
            for coll_name in collections:
                count = self.db[coll_name].count_documents({})
                counts[coll_name] = count
                print(f"   {coll_name}: {count:,} documents")
            return counts
        return count_all()
    
    def test_products_query(self):
        """Test products collection query"""
        def query_products():
            start = time.time()
            products = list(self.db.products.find({}))
            elapsed = time.time() - start
            size = sys.getsizeof(str(products))
            print(f"   Found {len(products)} products")
            print(f"   Data size: {size / 1024 / 1024:.2f} MB")
            print(f"   Query time: {elapsed:.3f}s")
            return len(products)
        return query_products()
    
    def test_products_with_limit(self):
        """Test products query with limit"""
        def query_limited():
            start = time.time()
            products = list(self.db.products.find({}).limit(100))
            elapsed = time.time() - start
            print(f"   Found {len(products)} products (limited)")
            print(f"   Query time: {elapsed:.3f}s")
            return len(products)
        return query_limited()
    
    def test_sales_query(self):
        """Test sales/sales_log query"""
        def query_sales():
            # Try both possible collection names
            coll_name = 'sales_log' if 'sales_log' in self.db.list_collection_names() else 'sales'
            start = time.time()
            sales = list(self.db[coll_name].find({}).limit(100))
            elapsed = time.time() - start
            print(f"   Found {len(sales)} sales records (limited)")
            print(f"   Collection: {coll_name}")
            print(f"   Query time: {elapsed:.3f}s")
            return len(sales)
        return query_sales()
    
    def test_sales_aggregation(self):
        """Test sales aggregation query (like what Dashboard does)"""
        def aggregate_sales():
            coll_name = 'sales_log' if 'sales_log' in self.db.list_collection_names() else 'sales'
            start_date = datetime.now() - timedelta(days=30)
            end_date = datetime.now()
            
            start = time.time()
            pipeline = [
                {
                    '$match': {
                        'transaction_date': {
                            '$gte': start_date,
                            '$lte': end_date
                        },
                        'status': {'$ne': 'voided'}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_revenue': {'$sum': '$total_amount'},
                        'total_transactions': {'$sum': 1}
                    }
                }
            ]
            
            result = list(self.db[coll_name].aggregate(pipeline))
            elapsed = time.time() - start
            print(f"   Aggregation time: {elapsed:.3f}s")
            if result:
                print(f"   Total revenue: ₱{result[0].get('total_revenue', 0):,.2f}")
                print(f"   Total transactions: {result[0].get('total_transactions', 0)}")
            return result
        return aggregate_sales()
    
    def test_indexes(self):
        """Check for indexes on collections"""
        def check_indexes():
            important_collections = ['products', 'sales', 'sales_log', 'customers', 'users']
            indexes_info = {}
            
            for coll_name in important_collections:
                if coll_name in self.db.list_collection_names():
                    indexes = list(self.db[coll_name].list_indexes())
                    indexes_info[coll_name] = [idx['key'] for idx in indexes]
                    print(f"\n   {coll_name} indexes:")
                    for idx in indexes:
                        print(f"      {idx['name']}: {idx['key']}")
            
            return indexes_info
        return check_indexes()
    
    def test_connection_string_info(self):
        """Display connection info (without credentials)"""
        def show_info():
            uri = config('MONGODB_URI', default='NOT_SET')
            db_name = config('MONGODB_DATABASE', default='pos_system')
            
            # Parse connection type
            if uri.startswith('mongodb+srv://'):
                conn_type = "MongoDB Atlas (Cloud)"
                # Extract cluster info without credentials
                cluster_info = uri.split('@')[1].split('/')[0] if '@' in uri else 'Unknown'
            elif uri.startswith('mongodb://localhost'):
                conn_type = "Local MongoDB"
                cluster_info = "localhost:27017"
            else:
                conn_type = "Custom MongoDB"
                cluster_info = "Custom server"
            
            info = {
                'connection_type': conn_type,
                'cluster': cluster_info,
                'database': db_name
            }
            
            print(f"   Connection Type: {conn_type}")
            print(f"   Cluster: {cluster_info}")
            print(f"   Database: {db_name}")
            
            return info
        return show_info()
    
    def print_summary(self):
        """Print test summary"""
        print(f"\n{'='*60}")
        print("TEST SUMMARY")
        print(f"{'='*60}\n")
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r['status'] == 'PASS')
        failed = total_tests - passed
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        # Identify slow queries
        print(f"\n{'='*60}")
        print("PERFORMANCE ANALYSIS")
        print(f"{'='*60}\n")
        
        slow_threshold = 1.0  # 1 second
        timeout_threshold = 30.0  # 30 seconds (frontend timeout)
        
        slow_tests = [r for r in self.results if r.get('time', 0) > slow_threshold]
        critical_tests = [r for r in self.results if r.get('time', 0) > timeout_threshold]
        
        if critical_tests:
            print(f"❌ CRITICAL - Queries exceeding 30s timeout:")
            for test in critical_tests:
                print(f"   {test['test']}: {test['time']:.3f}s")
        
        if slow_tests:
            print(f"\n⚠️  SLOW - Queries taking > 1s:")
            for test in slow_tests:
                if test not in critical_tests:
                    print(f"   {test['test']}: {test['time']:.3f}s")
        
        if not slow_tests:
            print("✅ All queries completed in < 1s")
        
        # Recommendations
        print(f"\n{'='*60}")
        print("RECOMMENDATIONS")
        print(f"{'='*60}\n")
        
        recommendations = []
        
        for test in self.results:
            if test['test'] == 'Products Query (All)' and test.get('time', 0) > 5:
                recommendations.append(
                    "🔧 Products table is slow. Consider:\n"
                    "   - Adding pagination (limit/skip)\n"
                    "   - Creating indexes on frequently queried fields\n"
                    "   - Reducing payload size (select only needed fields)"
                )
            
            if test['test'] == 'Sales Aggregation' and test.get('time', 0) > 5:
                recommendations.append(
                    "🔧 Sales aggregation is slow. Consider:\n"
                    "   - Adding index on 'transaction_date' field\n"
                    "   - Adding index on 'status' field\n"
                    "   - Using compound index: {transaction_date: 1, status: 1}"
                )
        
        # Check for missing indexes
        for test in self.results:
            if test['test'] == 'Check Indexes':
                result = test.get('result', {})
                for coll, indexes in result.items():
                    index_fields = [list(idx.keys()) for idx in indexes]
                    
                    if coll == 'sales_log' or coll == 'sales':
                        if not any('transaction_date' in fields for fields in index_fields):
                            recommendations.append(
                                f"🔧 Missing index on {coll}.transaction_date - this will slow down date range queries"
                            )
                    
                    if coll == 'products':
                        if not any('product_id' in fields or 'sku' in fields for fields in index_fields):
                            recommendations.append(
                                f"🔧 Consider adding index on {coll}.product_id or sku for faster lookups"
                            )
        
        if recommendations:
            for rec in recommendations:
                print(rec)
                print()
        else:
            print("✅ No major issues detected!")
        
        # Network vs Database analysis
        print(f"{'='*60}")
        print("BOTTLENECK ANALYSIS")
        print(f"{'='*60}\n")
        
        ping_test = next((r for r in self.results if r['test'] == 'Connection Latency'), None)
        if ping_test and ping_test.get('result'):
            ping_ms = ping_test['result']
            print(f"Network latency: {ping_ms:.2f}ms")
            
            if ping_ms > 200:
                print("⚠️  HIGH NETWORK LATENCY detected!")
                print("   This suggests the database is geographically distant.")
                print("   Consider:")
                print("   - Using a closer MongoDB Atlas region")
                print("   - Implementing caching layer (Redis)")
                print("   - Reducing number of database calls")
            elif ping_ms > 100:
                print("⚠️  MODERATE NETWORK LATENCY")
                print("   Network adds noticeable delay but is acceptable.")
            else:
                print("✅ Network latency is good")

def main():
    print("="*60)
    print("DATABASE PERFORMANCE DIAGNOSTIC TOOL")
    print("="*60)
    
    tester = DatabasePerformanceTest()
    
    # Run all tests
    tester.test('Connection String Info', tester.test_connection_string_info)
    tester.test('Connection Latency', tester.test_connection_latency)
    tester.test('Collection Document Counts', tester.test_collection_counts)
    tester.test('Products Query (Limited 100)', tester.test_products_with_limit)
    tester.test('Products Query (All)', tester.test_products_query)
    tester.test('Sales Query (Limited)', tester.test_sales_query)
    tester.test('Sales Aggregation', tester.test_sales_aggregation)
    tester.test('Check Indexes', tester.test_indexes)
    
    # Print summary
    tester.print_summary()

if __name__ == '__main__':
    main()
