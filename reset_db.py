import os
from app import create_app, db
from app.models.user import User

def reset_database():
    """Reset database completely"""
    print("🔄 Resetting database...")
    
    # Delete old database
    if os.path.exists('app.db'):
        os.remove('app.db')
        print("✅ Deleted old database")
    
    # Create app and new database
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Created new database")
        
        # Create admin user
        admin = User(
            username='admin',
            email='admin@bulkemail.com',
            name='Administrator',
            is_admin=True,
            is_active=True
        )
        admin.set_password('admin123')
        
        # Create demo client
        client = User(
            email='demo@example.com',
            name='Demo Client',
            google_id='demo@example.com',
            is_admin=False,
            is_active=True
        )
        
        db.session.add(admin)
        db.session.add(client)
        db.session.commit()
        
        print("✅ Created users:")
        print("   Admin: admin/admin123")
        print("   Client: demo@example.com")

if __name__ == '__main__':
    reset_database()