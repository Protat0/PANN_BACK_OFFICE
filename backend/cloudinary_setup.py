"""
Cloudinary Setup and Configuration
Helps you set up Cloudinary for image storage
"""
import os

print("=" * 70)
print("☁️  CLOUDINARY SETUP GUIDE")
print("=" * 70)

print("""
Cloudinary is a cloud service for storing and managing images.
It's FREE for up to 25GB storage and 25GB bandwidth per month!

STEP 1: Create Free Cloudinary Account
---------------------------------------
1. Go to: https://cloudinary.com/users/register/free
2. Sign up with your email
3. Verify your email
4. You'll be taken to your dashboard

STEP 2: Get Your Credentials
-----------------------------
On your Cloudinary dashboard, you'll see:
- Cloud Name: (e.g., "dxxxxx")
- API Key: (e.g., "123456789012345")
- API Secret: (e.g., "ABCdefGHI...")

STEP 3: Add to Your .env File
------------------------------
Add these lines to your backend/.env file:

CLOUDINARY_CLOUD_NAME=your_cloud_name_here
CLOUDINARY_API_KEY=your_api_key_here
CLOUDINARY_API_SECRET=your_api_secret_here

STEP 4: Install Cloudinary Package
-----------------------------------
Run this command in your backend directory:

    pip install cloudinary

Or add to requirements.txt:
    
    cloudinary==1.40.0

STEP 5: Run Migration Script
-----------------------------
Once configured, run:

    python migrate_images_to_cloudinary.py

This will:
- Upload all base64 images to Cloudinary
- Update MongoDB with Cloudinary URLs
- Keep backups of original data

BENEFITS:
---------
✅ 99% faster product queries
✅ Reduced MongoDB storage costs
✅ CDN delivery of images (global, fast)
✅ Automatic image optimization
✅ Free tier is generous (25GB)
✅ No more 250KB per product!

AFTER MIGRATION:
----------------
- Products will be ~2KB each (instead of 250KB!)
- Dashboard will load in 1-2 seconds (instead of 30s+)
- All optimizations will finally work!

""")

print("=" * 70)
print("📝 NEXT STEPS:")
print("=" * 70)
print("1. Sign up at: https://cloudinary.com/users/register/free")
print("2. Get your credentials from dashboard")
print("3. Add to backend/.env file")
print("4. Run: pip install cloudinary")
print("5. Run: python migrate_images_to_cloudinary.py")
print("=" * 70)

# Check if .env exists
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print("\n✅ Found .env file at:", env_path)
    print("   Add your Cloudinary credentials there!")
else:
    print("\n⚠️  No .env file found!")
    print("   Create one in the backend directory")

