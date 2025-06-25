import os
from dotenv import load_dotenv

load_dotenv()

# Enable OAuthlib insecure transport for development only (HTTP instead of HTTPS)
if os.getenv('FLASK_ENV') == 'development':
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'e1f8c81a1e6f0c6e3b23a7d94d72f1f519d6e8f7b6a9d68a23c5c6f27e8ab3f54'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///bulk_email.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth config
    GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
    
    # If you want to relax token scope validation (sometimes needed)
    OAUTHLIB_RELAX_TOKEN_SCOPE = True
    
    # Email settings
    MAIL_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('SMTP_PORT') or 587)
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_ADDRESS')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    
    # Upload settings
    UPLOAD_FOLDER = 'static/resumes'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
    
    # Disable CSRF for now
    WTF_CSRF_ENABLED = False