"""
Create database indexes for performance optimization
Run this script to add indexes to MongoDB collections
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.local')

import django
django.setup()

from app.database import db_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_indexes():
    """Create indexes for all collections"""
    try:
        db = db_manager.get_database()
        logger.info("Connected to database: %s", db.name)
        
        # Products Collection Indexes
        logger.info("\n" + "="*70)
        logger.info("Creating indexes for 'products' collection...")
        logger.info("="*70)
        
        products_indexes = [
            # Single field indexes
            ('category_id', 1),
            ('subcategory_name', 1),
            ('status', 1),
            ('isDeleted', 1),
            ('SKU', 1),  # For SKU lookups
            
            # Compound indexes for common queries
            ([('isDeleted', 1), ('status', 1)], 'isDeleted_1_status_1'),
            ([('isDeleted', 1), ('category_id', 1)], 'isDeleted_1_category_id_1'),
            ([('stock', 1), ('isDeleted', 1)], 'stock_1_isDeleted_1'),  # For stock level queries
            
            # Text index for search
            ([('product_name', 'text'), ('SKU', 'text')], 'product_search_text'),
        ]
        
        for idx in products_indexes:
            try:
                if isinstance(idx, tuple) and len(idx) == 2 and isinstance(idx[0], list):
                    # Compound index with custom name
                    fields, name = idx
                    result = db.products.create_index(fields, name=name, background=True)
                    logger.info(f"  ✅ Created compound index: {name}")
                elif isinstance(idx, tuple):
                    # Single field index
                    field, direction = idx
                    result = db.products.create_index([(field, direction)], background=True)
                    logger.info(f"  ✅ Created index on: {field}")
            except Exception as e:
                if 'already exists' in str(e).lower():
                    logger.info(f"  ⚪ Index already exists: {idx}")
                else:
                    logger.error(f"  ❌ Error creating index {idx}: {e}")
        
        # Sales/Sales_Log Collection Indexes
        logger.info("\n" + "="*70)
        logger.info("Creating indexes for 'sales_log' collection...")
        logger.info("="*70)
        
        # Check which collection exists
        sales_collection_name = None
        if 'sales_log' in db.list_collection_names():
            sales_collection_name = 'sales_log'
        elif 'sales' in db.list_collection_names():
            sales_collection_name = 'sales'
        
        if sales_collection_name:
            sales_indexes = [
                # Single field indexes
                ('transaction_date', -1),  # Most recent first
                ('status', 1),
                ('customer_id', 1),
                
                # Compound indexes for common date range queries
                ([('transaction_date', -1), ('status', 1)], 'transaction_date_-1_status_1'),
                ([('status', 1), ('transaction_date', -1)], 'status_1_transaction_date_-1'),
            ]
            
            for idx in sales_indexes:
                try:
                    if isinstance(idx, tuple) and len(idx) == 2 and isinstance(idx[0], list):
                        fields, name = idx
                        result = db[sales_collection_name].create_index(fields, name=name, background=True)
                        logger.info(f"  ✅ Created compound index: {name}")
                    elif isinstance(idx, tuple):
                        field, direction = idx
                        result = db[sales_collection_name].create_index([(field, direction)], background=True)
                        logger.info(f"  ✅ Created index on: {field}")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        logger.info(f"  ⚪ Index already exists: {idx}")
                    else:
                        logger.error(f"  ❌ Error creating index {idx}: {e}")
        else:
            logger.warning("  ⚠️  No sales or sales_log collection found")
        
        # Customers Collection Indexes
        logger.info("\n" + "="*70)
        logger.info("Creating indexes for 'customers' collection...")
        logger.info("="*70)
        
        if 'customers' in db.list_collection_names():
            customer_indexes = [
                ('email', 1),
                ('phone', 1),
                ('customer_id', 1),
            ]
            
            for idx in customer_indexes:
                try:
                    if isinstance(idx, tuple):
                        field, direction = idx
                        result = db.customers.create_index([(field, direction)], background=True)
                        logger.info(f"  ✅ Created index on: {field}")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        logger.info(f"  ⚪ Index already exists: {idx}")
                    else:
                        logger.error(f"  ❌ Error creating index {idx}: {e}")
        
        # Users Collection Indexes
        logger.info("\n" + "="*70)
        logger.info("Creating indexes for 'users' collection...")
        logger.info("="*70)
        
        if 'users' in db.list_collection_names():
            user_indexes = [
                ('email', 1),
                ('username', 1),
                ('role', 1),
            ]
            
            for idx in user_indexes:
                try:
                    if isinstance(idx, tuple):
                        field, direction = idx
                        result = db.users.create_index([(field, direction)], background=True)
                        logger.info(f"  ✅ Created index on: {field}")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        logger.info(f"  ⚪ Index already exists: {idx}")
                    else:
                        logger.error(f"  ❌ Error creating index {idx}: {e}")
        
        # List all indexes for verification
        logger.info("\n" + "="*70)
        logger.info("VERIFICATION - Current indexes:")
        logger.info("="*70)
        
        for coll_name in ['products', sales_collection_name, 'customers', 'users']:
            if coll_name and coll_name in db.list_collection_names():
                indexes = list(db[coll_name].list_indexes())
                logger.info(f"\n{coll_name}:")
                for idx in indexes:
                    logger.info(f"  - {idx['name']}: {idx.get('key', {})}")
        
        logger.info("\n" + "="*70)
        logger.info("✅ Index creation completed!")
        logger.info("="*70)
        
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        raise

if __name__ == '__main__':
    create_indexes()
