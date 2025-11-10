"""
Test script for email verification
Run this from the backend directory: python test_email_verification.py
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'posbackend.settings')
django.setup()

from notifications.email_verification_service import email_verification_service

def test_email_verification():
    """Test sending verification email"""
    from decouple import config
    from notifications.email_service import email_service
    
    test_email = "ngjameswinston@gmail.com"
    
    print(f"Testing email verification for: {test_email}")
    print("-" * 50)
    
    # Check configuration
    print("\nConfiguration Check:")
    api_key = config('SENDGRID_API_KEY', default='')
    from_email = config('SENDGRID_FROM_EMAIL', default='')
    from_name = config('SENDGRID_FROM_NAME', default='')
    
    print(f"  API Key: {'Set' if api_key else 'NOT SET'}")
    print(f"  From Email: {from_email}")
    print(f"  From Name: {from_name}")
    
    if not api_key:
        print("\n[ERROR] SENDGRID_API_KEY is not set in .env file!")
        return False
    
    if not from_email:
        print("\n[ERROR] SENDGRID_FROM_EMAIL is not set in .env file!")
        return False
    
    print("\nSending test email...")
    print("-" * 50)
    
    try:
        # Send verification email
        result = email_verification_service.send_verification_email(
            email=test_email,
            user_id=None,  # No user ID for test
            user_name="Test User"
        )
        
        if result.get('success'):
            print("\n[SUCCESS] Verification email sent successfully!")
            print(f"Status Code: {result.get('status_code', 'N/A')}")
            print(f"Message: {result.get('message', 'N/A')}")
            print("\nPlease check your email inbox (and spam folder) for the verification email.")
        else:
            print("\n[FAILED] Could not send verification email")
            print(f"Error: {result.get('error', 'Unknown error')}")
            if result.get('error_details'):
                print(f"Error Details: {result.get('error_details')}")
            print("\nTroubleshooting:")
            print("1. Make sure your Single Sender email is verified in SendGrid")
            print("2. Check that your API key has 'Mail Send' permissions")
            print("3. Verify the API key is correct in your .env file")
            return False
        
        return True
    
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Email Verification Test")
    print("=" * 50)
    print()
    
    success = test_email_verification()
    
    print()
    print("=" * 50)
    if success:
        print("Test completed successfully!")
    else:
        print("Test failed. Please check the error messages above.")
    print("=" * 50)

