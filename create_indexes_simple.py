import sys
import os

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.local')

import django
django.setup()

from backend.app.database import db_manager

print("="*70)
print("CREATING DATABASE INDEXES")
print("="*70)

try:
    db = db_manager.get_database()
    print(f"\nConnected to database: {db.name}")
    
    # Create indexes
    print("\n1. Creating Products indexes...")
    try:
        idx1 = db.products.create_index([('isDeleted', 1), ('status', 1)], name='idx_isDeleted_status', background=True)
        print(f"   ✅ Created: {idx1}")
    except Exception as e:
        print(f"   ⚠️  {str(e)}")
    
    try:
        idx2 = db.products.create_index([('SKU', 1)], name='idx_SKU', background=True)
        print(f"   ✅ Created: {idx2}")
    except Exception as e:
        print(f"   ⚠️  {str(e)}")
    
    print("\n2. Creating Sales indexes...")
    try:
        idx3 = db.sales_log.create_index([('transaction_date', -1)], name='idx_transaction_date', background=True)
        print(f"   ✅ Created: {idx3}")
    except Exception as e:
        print(f"   ⚠️  {str(e)}")
    
    try:
        idx4 = db.sales_log.create_index([('transaction_date', -1), ('status', 1)], name='idx_transaction_date_status', background=True)
        print(f"   ✅ Created: {idx4}")
    except Exception as e:
        print(f"   ⚠️  {str(e)}")
    
    try:
        idx5 = db.sales_log.create_index([('status', 1)], name='idx_status', background=True)
        print(f"   ✅ Created: {idx5}")
    except Exception as e:
        print(f"   ⚠️  {str(e)}")
    
    print("\n3. Verifying indexes...")
    print("\nProducts indexes:")
    for idx in db.products.list_indexes():
        print(f"   - {idx['name']}: {idx['key']}")
    
    print("\nSales_log indexes:")
    for idx in db.sales_log.list_indexes():
        print(f"   - {idx['name']}: {idx['key']}")
    
    print("\n" + "="*70)
    print("✅ INDEX CREATION COMPLETED!")
    print("="*70)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

