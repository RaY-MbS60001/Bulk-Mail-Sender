from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_dance.contrib.google import make_google_blueprint
from flask_dance.consumer.storage import session as session_storage
from flask_wtf.csrf import CSRFProtect
import os

# Create extensions instances first, but don't initialize them yet
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    from app.config import Config
    app.config.from_object(Config)
    
    # For development only - allows OAuth without HTTPS
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # Initialize CSRF protection
    login_manager.login_view = 'auth.login'
    
    # Setup user_loader
    @login_manager.user_loader
    def load_user(user_id):
        # Import User model inside the function to avoid circular imports
        from app.models.user import User
        return User.query.get(int(user_id))

    # Setup Google OAuth with explicit session storage
    google_bp = make_google_blueprint(
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
        redirect_url="/google/authorized",  # This should match your route path
        storage=session_storage.SessionStorage()  # Add explicit storage
    )
    
    # Register the Google blueprint first
    app.register_blueprint(google_bp, url_prefix="/login")

    # Register application blueprints
    # Import them here to avoid circular imports
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.learnership import learnership_bp
    from app.routes.batch import batch_bp
    from app.routes.profile import profile_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(learnership_bp)
    app.register_blueprint(batch_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(analytics_bp)
    
    # Initialize database tables
    with app.app_context():
        db.create_all()
    
    return app