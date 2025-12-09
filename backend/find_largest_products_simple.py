"""
Simple script to find top 10 largest products
Writes output to file for easy viewing
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import db_manager
import json
from datetime import datetime

# Open output file
output = open('LARGEST_PRODUCTS_RESULT.txt', 'w', encoding='utf-8')

def write(text):
    print(text)
    output.write(text + "\n")
    output.flush()

try:
    write("="*80)
    write("FINDING TOP 10 LARGEST PRODUCTS")
    write("="*80)
    write(f"Time: {datetime.now()}\n")
    
    # Connect
    write("Connecting to MongoDB...")
    db = db_manager.get_database()
    write(f"Connected to: {db.name}\n")
    
    # Fetch products
    write("Fetching products...")
    products = list(db.products.find({}))
    write(f"Found {len(products)} products\n")
    
    # Analyze
    write("Analyzing sizes...\n")
    results = []
    
    for p in products:
        json_str = json.dumps(p, default=str)
        size = len(json_str.encode('utf-8'))
        
        # Get image size
        img_size = 0
        if 'image_url' in p and p['image_url']:
            img_json = json.dumps({'image_url': p['image_url']})
            img_size = len(img_json.encode('utf-8'))
        
        results.append({
            'name': p.get('product_name', 'Unknown'),
            'code': p.get('product_id', 'N/A'),
            'id': str(p.get('_id')),
            'size': size,
            'img_size': img_size,
            'img_pct': (img_size/size*100) if size > 0 else 0
        })
    
    # Sort by size
    results.sort(key=lambda x: x['size'], reverse=True)
    top_10 = results[:10]
    
    write("="*80)
    write("TOP 10 LARGEST PRODUCTS")
    write("="*80)
    write("")
    
    for i, r in enumerate(top_10, 1):
        write(f"#{i}: {r['name']}")
        write(f"    Code: {r['code']}")
        write(f"    ID: {r['id']}")
        write(f"    Total: {r['size']/1024/1024:.2f} MB ({r['size']:,} bytes)")
        write(f"    Image: {r['img_size']/1024/1024:.2f} MB ({r['img_pct']:.1f}%)")
        write("")
    
    # Summary
    total = sum(r['size'] for r in results)
    total_img = sum(r['img_size'] for r in results)
    avg = total / len(results)
    
    write("="*80)
    write("SUMMARY")
    write("="*80)
    write(f"Total products: {len(results)}")
    write(f"Total size: {total/1024/1024:.2f} MB")
    write(f"Total images: {total_img/1024/1024:.2f} MB")
    write(f"Average product: {avg/1024:.2f} KB")
    write(f"Images are: {(total_img/total*100):.1f}% of total size")
    write("")
    write(f"Savings if images excluded: {total_img/1024/1024:.2f} MB")
    write("="*80)
    write("DONE!")
    
    output.close()
    print("\n✅ Results written to: LARGEST_PRODUCTS_RESULT.txt")
    
except Exception as e:
    write(f"\nERROR: {e}")
    import traceback
    write(traceback.format_exc())
    output.close()
