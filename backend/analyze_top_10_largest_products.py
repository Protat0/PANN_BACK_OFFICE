"""
Analyze Top 10 Largest Products
Find which products have the biggest document sizes
"""
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Force output to file
output_file = open('product_size_analysis_output.txt', 'w', encoding='utf-8')

def print_both(text=""):
    """Print to both console and file"""
    print(text)
    output_file.write(text + "\n")
    output_file.flush()

print_both("=" * 80)
print_both("📊 ANALYZING TOP 10 LARGEST PRODUCTS")
print_both("=" * 80)
print_both(f"Started: {datetime.now().strftime('%H:%M:%S')}")
print_both()

try:
    from app.database import db_manager
    import json
    
    # Connect to database
    print("1. Connecting to MongoDB...")
    db = db_manager.get_database()
    if db is None:
        raise Exception("Failed to connect to database")
    print(f"   ✅ Connected to: {db.name}\n")
    
    # Fetch all products
    print("2. Fetching all products...")
    products = list(db.products.find({}))
    print(f"   ✅ Found {len(products)} products\n")
    
    # Analyze each product's size
    print("3. Analyzing product sizes...\n")
    product_sizes = []
    
    for product in products:
        # Convert to JSON to measure size
        product_json = json.dumps(product, default=str)
        total_size = len(product_json.encode('utf-8'))
        
        # Analyze individual fields
        field_sizes = {}
        for field, value in product.items():
            if value is not None:
                field_json = json.dumps({field: value}, default=str)
                field_size = len(field_json.encode('utf-8'))
                field_sizes[field] = field_size
        
        # Get image size if present
        image_size = field_sizes.get('image_url', 0)
        
        product_sizes.append({
            'product_id': str(product.get('_id')),
            'product_name': product.get('product_name', 'Unknown'),
            'product_code': product.get('product_id', 'N/A'),
            'total_size': total_size,
            'image_size': image_size,
            'image_percentage': (image_size / total_size * 100) if total_size > 0 else 0,
            'field_sizes': field_sizes
        })
    
    # Sort by total size (descending)
    product_sizes.sort(key=lambda x: x['total_size'], reverse=True)
    
    # Get top 10
    top_10 = product_sizes[:10]
    
    print("=" * 80)
    print("🏆 TOP 10 LARGEST PRODUCTS")
    print("=" * 80)
    print()
    
    for i, prod in enumerate(top_10, 1):
        total_mb = prod['total_size'] / 1024 / 1024
        image_mb = prod['image_size'] / 1024 / 1024
        
        print(f"#{i} - {prod['product_name']}")
        print(f"   Product Code: {prod['product_code']}")
        print(f"   MongoDB ID: {prod['product_id']}")
        print(f"   📦 Total Size: {total_mb:.2f} MB ({prod['total_size']:,} bytes)")
        print(f"   🖼️  Image Size: {image_mb:.2f} MB ({prod['image_size']:,} bytes)")
        print(f"   📊 Image %: {prod['image_percentage']:.1f}%")
        
        # Show top 5 largest fields
        sorted_fields = sorted(prod['field_sizes'].items(), key=lambda x: x[1], reverse=True)[:5]
        print(f"   📋 Top 5 Fields:")
        for field, size in sorted_fields:
            size_kb = size / 1024
            field_percentage = (size / prod['total_size'] * 100) if prod['total_size'] > 0 else 0
            print(f"      - {field}: {size_kb:.1f} KB ({field_percentage:.1f}%)")
        print()
    
    # Summary statistics
    print("=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)
    
    total_all_products = sum(p['total_size'] for p in product_sizes)
    total_all_images = sum(p['image_size'] for p in product_sizes)
    total_top_10 = sum(p['total_size'] for p in top_10)
    total_top_10_images = sum(p['image_size'] for p in top_10)
    
    avg_product_size = total_all_products / len(product_sizes) if product_sizes else 0
    avg_image_size = total_all_images / len(product_sizes) if product_sizes else 0
    
    print(f"\nAll Products ({len(product_sizes)} total):")
    print(f"  • Total Size: {total_all_products / 1024 / 1024:.2f} MB")
    print(f"  • Total Image Size: {total_all_images / 1024 / 1024:.2f} MB")
    print(f"  • Average Product Size: {avg_product_size / 1024:.2f} KB")
    print(f"  • Average Image Size: {avg_image_size / 1024:.2f} KB")
    
    print(f"\nTop 10 Products:")
    print(f"  • Total Size: {total_top_10 / 1024 / 1024:.2f} MB")
    print(f"  • Total Image Size: {total_top_10_images / 1024 / 1024:.2f} MB")
    print(f"  • % of Total Database: {(total_top_10 / total_all_products * 100):.1f}%")
    
    # Estimate savings if images were excluded
    potential_savings = total_all_images / 1024 / 1024
    print(f"\n💡 Potential Savings:")
    print(f"  • If images excluded: {potential_savings:.2f} MB saved")
    print(f"  • Data reduction: {(total_all_images / total_all_products * 100):.1f}%")
    
    # Write detailed report to file
    report_file = 'top_10_largest_products_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("TOP 10 LARGEST PRODUCTS - DETAILED REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Products Analyzed: {len(product_sizes)}\n\n")
        
        for i, prod in enumerate(top_10, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"RANK #{i}: {prod['product_name']}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Product Code: {prod['product_code']}\n")
            f.write(f"MongoDB ID: {prod['product_id']}\n")
            f.write(f"Total Size: {prod['total_size'] / 1024 / 1024:.2f} MB\n")
            f.write(f"Image Size: {prod['image_size'] / 1024 / 1024:.2f} MB\n")
            f.write(f"Image Percentage: {prod['image_percentage']:.1f}%\n\n")
            
            f.write("All Fields (sorted by size):\n")
            sorted_all_fields = sorted(prod['field_sizes'].items(), key=lambda x: x[1], reverse=True)
            for field, size in sorted_all_fields:
                size_kb = size / 1024
                field_percentage = (size / prod['total_size'] * 100) if prod['total_size'] > 0 else 0
                f.write(f"  - {field}: {size_kb:.2f} KB ({field_percentage:.1f}%)\n")
        
        # Add summary
        f.write(f"\n{'=' * 80}\n")
        f.write("SUMMARY STATISTICS\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"Total Products: {len(product_sizes)}\n")
        f.write(f"Total Database Size: {total_all_products / 1024 / 1024:.2f} MB\n")
        f.write(f"Total Image Size: {total_all_images / 1024 / 1024:.2f} MB\n")
        f.write(f"Average Product Size: {avg_product_size / 1024:.2f} KB\n")
        f.write(f"Top 10 Total: {total_top_10 / 1024 / 1024:.2f} MB\n")
        f.write(f"Top 10 % of Total: {(total_top_10 / total_all_products * 100):.1f}%\n")
        f.write(f"\nPotential Savings (excluding images): {potential_savings:.2f} MB ({(total_all_images / total_all_products * 100):.1f}%)\n")
    
    print(f"\n📝 Detailed report saved to: {report_file}")
    
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"Finished: {datetime.now().strftime('%H:%M:%S')}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
