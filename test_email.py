import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the bulk_email_app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'bulk_email_app'))

from app import create_app
from app.utils.email_service import EmailService

print("=== Bulk Email App - Email Configuration Test ===\n")

# Check environment variables
print("Checking environment variables...")
email_address = os.environ.get('EMAIL_ADDRESS')
email_password = os.environ.get('EMAIL_PASSWORD')

if not email_address or email_address == 'your_email@gmail.com':
    print("✗ EMAIL_ADDRESS not configured in .env file")
    print("Please set your email address in the .env file")
    sys.exit(1)

if not email_password or email_password == 'your_app_password':
    print("✗ EMAIL_PASSWORD not configured in .env file")
    print("Please set your email app password in the .env file")
    sys.exit(1)

print(f"✓ Email address: {email_address}")
print("✓ Email password: [HIDDEN]\n")

app = create_app()

with app.app_context():
    email_service = EmailService()
    
    # Test connection first
    print("Testing SMTP connection...")
    success, message = email_service.test_connection()
    
    if not success:
        print(f"✗ Connection failed: {message}")
        print("\nPossible issues:")
        print("1. Check your email and password in .env file")
        print("2. For Gmail, make sure you're using an App Password, not your regular password")
        print("3. Enable 'Less secure app access' or use App Passwords")
        sys.exit(1)
    
    print("✓ SMTP connection successful!\n")
    
    # Send test email
    test_email = input("Enter your email address to receive a test email: ")
    
    print(f"\nSending test email to {test_email}...")
    
    if email_service.send_test_email(test_email):
        print("✓ Test email sent successfully!")
        print("Check your inbox (and spam folder) for the test email.")
    else:
        print("✗ Failed to send test email")