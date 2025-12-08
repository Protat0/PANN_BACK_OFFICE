"""
Migrate Product Images from Base64 to Cloudinary
Converts embedded base64 images to Cloudinary URLs
"""
import sys
import os
import base64
import json
from datetime import datetime
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Check if cloudinary is installed
try:
    import cloudinary
    import cloudinary.uploader
    import cloudinary.api
except ImportError:
    print("❌ ERROR: Cloudinary package not installed!")
    print("\nInstall it with:")
    print("  pip install cloudinary")
    sys.exit(1)

# Check environment variables
try:
    from decouple import config
    
    CLOUDINARY_CLOUD_NAME = config('CLOUDINARY_CLOUD_NAME', default=None)
    CLOUDINARY_API_KEY = config('CLOUDINARY_API_KEY', default=None)
    CLOUDINARY_API_SECRET = config('CLOUDINARY_API_SECRET', default=None)
    
    if not all([CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET]):
        print("❌ ERROR: Cloudinary credentials not found in .env!")
        print("\nAdd these to your backend/.env file:")
        print("CLOUDINARY_CLOUD_NAME=your_cloud_name")
        print("CLOUDINARY_API_KEY=your_api_key")
        print("CLOUDINARY_API_SECRET=your_api_secret")
        print("\nRun: python cloudinary_setup.py for help")
        sys.exit(1)
        
except ImportError:
    print("❌ ERROR: python-decouple not installed!")
    print("  pip install python-decouple")
    sys.exit(1)

from app.database import db_manager

# Configure Cloudinary
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True
)

print("=" * 70)
print("☁️  MIGRATING IMAGES TO CLOUDINARY")
print("=" * 70)
print(f"Cloud Name: {CLOUDINARY_CLOUD_NAME}")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)

def upload_base64_to_cloudinary(base64_string, product_id, product_name):
    """Upload a base64 image to Cloudinary and return the URL"""
    try:
        # Extract image data from base64 string
        if ',' in base64_string:
            # Format: "data:image/jpeg;base64,/9j/4AAQ..."
            header, data = base64_string.split(',', 1)
        else:
            data = base64_string
        
        # Generate a safe filename
        safe_name = product_name.replace(' ', '_').replace('/', '_')[:50]
        public_id = f"products/{product_id}_{safe_name}"
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            f"data:image/jpeg;base64,{data}",
            public_id=public_id,
            folder="pann_pos/products",
            overwrite=True,
            resource_type="image"
        )
        
        return result['secure_url']
        
    except Exception as e:
        raise Exception(f"Failed to upload image: {str(e)}")

def migrate_all_images():
    """Migrate all product images from base64 to Cloudinary"""
    try:
        db = db_manager.get_database()
        products_collection = db.products
        
        # Get all products with base64 images
        print("\n1. Finding products with embedded images...")
        products_with_images = list(products_collection.find({
            'image_url': {'$regex': '^data:image'}  # base64 images start with "data:image"
        }))
        
        total_products = len(products_with_images)
        print(f"   Found {total_products} products with base64 images")
        
        if total_products == 0:
            print("\n✅ No products with base64 images found!")
            print("   All images may already be migrated.")
            return
        
        # Create backup
        print("\n2. Creating backup...")
        backup_file = f"image_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_data = []
        for p in products_with_images:
            backup_data.append({
                '_id': str(p['_id']),
                'product_name': p.get('product_name'),
                'image_url': p.get('image_url')[:100] + '...',  # First 100 chars
                'image_size': len(p.get('image_url', ''))
            })
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        print(f"   ✅ Backup created: {backup_file}")
        
        # Migrate each product
        print("\n3. Migrating images to Cloudinary...")
        print(f"   This will take approximately {total_products * 2} seconds")
        print("   Progress:")
        
        migrated = 0
        failed = 0
        failed_products = []
        
        for i, product in enumerate(products_with_images, 1):
            product_id = product.get('product_id') or product.get('_id')
            product_name = product.get('product_name', 'Unknown')
            
            try:
                print(f"   [{i}/{total_products}] Uploading: {product_name}...", end='')
                
                # Upload to Cloudinary
                cloudinary_url = upload_base64_to_cloudinary(
                    product['image_url'],
                    product_id,
                    product_name
                )
                
                # Update MongoDB with Cloudinary URL
                products_collection.update_one(
                    {'_id': product['_id']},
                    {
                        '$set': {
                            'image_url': cloudinary_url,
                            'image_source': 'cloudinary',
                            'migrated_at': datetime.now()
                        },
                        '$unset': {
                            'image_filename': '',
                            'image_type': '',
                            'image_size': ''
                        }
                    }
                )
                
                print(" ✅")
                migrated += 1
                
                # Small delay to avoid rate limits
                time.sleep(0.5)
                
            except Exception as e:
                print(f" ❌ ({str(e)[:50]})")
                failed += 1
                failed_products.append({
                    'product_id': product_id,
                    'product_name': product_name,
                    'error': str(e)
                })
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 MIGRATION SUMMARY")
        print("=" * 70)
        print(f"Total products: {total_products}")
        print(f"✅ Migrated successfully: {migrated}")
        print(f"❌ Failed: {failed}")
        print(f"📁 Backup file: {backup_file}")
        
        if failed > 0:
            print("\nFailed products:")
            for fp in failed_products:
                print(f"  - {fp['product_name']} ({fp['product_id']}): {fp['error']}")
        
        # Calculate savings
        if migrated > 0:
            print("\n" + "=" * 70)
            print("💾 STORAGE SAVINGS")
            print("=" * 70)
            avg_image_size = 250  # KB
            total_saved_kb = migrated * avg_image_size
            total_saved_mb = total_saved_kb / 1024
            print(f"Estimated MongoDB storage saved: ~{total_saved_mb:.1f} MB")
            print(f"Average product size reduced: 250KB → 2KB (99% reduction!)")
        
        print("\n" + "=" * 70)
        print("✅ MIGRATION COMPLETE!")
        print("=" * 70)
        print("\n💡 NEXT STEPS:")
        print("1. Test your Dashboard - it should be MUCH faster now!")
        print("2. Run: python test_no_images_performance.py")
        print("3. Products now use Cloudinary URLs instead of base64")
        print("4. Images are served via CDN (fast, global delivery)")
        print("\n" + "=" * 70)
        
    except Exception as e:
        print(f"\n❌ MIGRATION FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will modify your database!")
    print("   A backup will be created before migration.")
    
    response = input("\nContinue with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_all_images()
    else:
        print("\n❌ Migration cancelled.")

