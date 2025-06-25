from app import create_app, db
from app.models.user import User
from datetime import datetime

def create_admin():
    """Create an admin user"""
    app = create_app()
    with app.app_context():
        print("Creating admin user...")
        
        # Check if admin already exists
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print("Admin user already exists!")
            print(f"Username: {admin.username}")
            print(f"Email: {admin.email}")
            return
        
        # Get admin details
        username = input("Enter admin username (default: admin): ").strip() or "admin"
        email = input("Enter admin email (default: admin@bulkemail.com): ").strip() or "admin@bulkemail.com"
        name = input("Enter admin name (default: Administrator): ").strip() or "Administrator"
        
        # Get password
        import getpass
        password = getpass.getpass("Enter admin password: ")
        if not password:
            password = "admin123"
            print("Using default password: admin123")
        
        # Create admin user
        admin = User(
            username=username,
            email=email,
            name=name,
            is_admin=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        admin.set_password(password)
        
        try:
            db.session.add(admin)
            db.session.commit()
            
            print("\n✅ Admin user created successfully!")
            print(f"Username: {username}")
            print(f"Email: {email}")
            print(f"Password: {'admin123' if password == 'admin123' else '[Hidden]'}")
            print(f"Admin Status: {admin.is_admin}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating admin user: {str(e)}")

if __name__ == '__main__':
    create_admin()