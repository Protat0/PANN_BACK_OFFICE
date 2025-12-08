"""
Analyze Product Document Size
Identifies which fields are making products so large
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import db_manager
import json

print("=" * 70)
print("📦 ANALYZING PRODUCT DOCUMENT SIZE")
print("=" * 70)

try:
    db = db_manager.get_database()
    
    # Fetch one product
    print("\n1. Fetching a sample product...")
    product = db.products.find_one({})
    
    if not product:
        print("❌ No products found!")
        exit(1)
    
    print(f"✅ Found product: {product.get('product_name', 'Unknown')}")
    print(f"   Product ID: {product.get('product_id', product.get('_id'))}")
    
    # Analyze field sizes
    print("\n2. Analyzing field sizes...")
    print("=" * 70)
    
    field_sizes = {}
    total_size = 0
    
    for field, value in product.items():
        # Convert to string to measure size
        field_str = str(value)
        size_bytes = len(field_str.encode('utf-8'))
        field_sizes[field] = size_bytes
        total_size += size_bytes
    
    # Sort by size (largest first)
    sorted_fields = sorted(field_sizes.items(), key=lambda x: x[1], reverse=True)
    
    print(f"\n{'Field Name':<30} {'Size':<15} {'% of Total':<10}")
    print("-" * 70)
    
    for field, size in sorted_fields:
        size_mb = size / (1024 * 1024)
        size_kb = size / 1024
        percent = (size / total_size) * 100
        
        # Format size nicely
        if size_mb >= 1:
            size_str = f"{size_mb:.2f} MB"
        elif size_kb >= 1:
            size_str = f"{size_kb:.2f} KB"
        else:
            size_str = f"{size} bytes"
        
        # Mark large fields
        marker = "⚠️" if size_mb > 0.1 else ""
        
        print(f"{field:<30} {size_str:<15} {percent:>6.2f}% {marker}")
    
    print("-" * 70)
    total_mb = total_size / (1024 * 1024)
    print(f"{'TOTAL SIZE':<30} {total_mb:.2f} MB")
    
    # Show sample of largest fields
    print("\n" + "=" * 70)
    print("3. SAMPLE OF LARGEST FIELDS")
    print("=" * 70)
    
    for field, size in sorted_fields[:5]:  # Top 5 largest
        value = product.get(field)
        size_mb = size / (1024 * 1024)
        
        if size_mb < 0.01:  # Skip if less than 10KB
            continue
            
        print(f"\n📦 Field: {field}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Type: {type(value).__name__}")
        
        # Show preview
        if isinstance(value, str):
            if len(value) > 200:
                print(f"   Preview: {value[:200]}...")
                
                # Check if it's base64 image
                if value.startswith('data:image'):
                    print("   ⚠️  WARNING: This appears to be an embedded base64 image!")
                    print("   ⚠️  Images should be stored externally, not in MongoDB!")
            else:
                print(f"   Value: {value}")
        elif isinstance(value, (list, dict)):
            print(f"   Items: {len(value) if isinstance(value, list) else len(value.keys())}")
            try:
                preview = json.dumps(value, indent=2)[:500]
                print(f"   Preview: {preview}...")
            except:
                print(f"   Value: {str(value)[:500]}...")
        else:
            print(f"   Value: {value}")
    
    # Analysis summary
    print("\n" + "=" * 70)
    print("4. ANALYSIS SUMMARY")
    print("=" * 70)
    
    # Find image fields
    image_fields = []
    for field, value in product.items():
        if isinstance(value, str) and (
            value.startswith('data:image') or 
            'base64' in value.lower() or
            len(value) > 100000
        ):
            image_fields.append((field, len(value)))
    
    if image_fields:
        print("\n⚠️  FOUND EMBEDDED IMAGES:")
        for field, size in image_fields:
            size_mb = size / (1024 * 1024)
            print(f"   - {field}: {size_mb:.2f} MB")
        print("\n💡 RECOMMENDATION:")
        print("   Move these images to external storage (Cloudinary, AWS S3, etc.)")
        print("   Store only image URLs in MongoDB")
        print("   This will reduce document size by 95-99%!")
    
    # Check for large arrays
    array_fields = []
    for field, value in product.items():
        if isinstance(value, list) and len(value) > 10:
            array_fields.append((field, len(value)))
    
    if array_fields:
        print("\n📊 LARGE ARRAYS FOUND:")
        for field, count in array_fields:
            print(f"   - {field}: {count} items")
    
    # Overall assessment
    print("\n" + "=" * 70)
    print("5. OVERALL ASSESSMENT")
    print("=" * 70)
    
    if total_mb > 1:
        print(f"\n❌ CRITICAL: Each product is {total_mb:.2f} MB!")
        print("   This is EXTREMELY LARGE for a product document.")
        print("   Recommended max size: 100KB per document")
        print(f"   Your documents are {(total_mb / 0.1):.0f}x too large!")
    elif total_mb > 0.1:
        print(f"\n⚠️  WARNING: Each product is {total_mb:.2f} MB")
        print("   This is larger than recommended.")
        print("   Consider optimizing large fields.")
    else:
        print(f"\n✅ Product size is acceptable: {total_mb:.2f} MB")
    
    print("\n" + "=" * 70)
    
    # Save detailed report
    with open('product_size_analysis.txt', 'w', encoding='utf-8') as f:
        f.write(f"Product Size Analysis\n")
        f.write(f"=" * 70 + "\n\n")
        f.write(f"Product: {product.get('product_name', 'Unknown')}\n")
        f.write(f"Total Size: {total_mb:.2f} MB\n\n")
        f.write(f"Field Breakdown:\n")
        for field, size in sorted_fields:
            size_mb = size / (1024 * 1024)
            percent = (size / total_size) * 100
            f.write(f"  {field}: {size_mb:.4f} MB ({percent:.2f}%)\n")
    
    print("\n📝 Detailed report saved to: product_size_analysis.txt")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

