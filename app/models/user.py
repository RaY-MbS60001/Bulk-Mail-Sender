from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import event

class User(UserMixin, db.Model):
    """User model for storing user account information and statistics"""
    
    __tablename__ = 'users'

    # Core fields
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    google_id = db.Column(db.String(120), unique=True, nullable=False, index=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Profile fields
    phone = db.Column(db.String(20))
    resume_file = db.Column(db.String(255))
    cover_letter_template = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))
    preferences = db.Column(db.JSON, default=lambda: {})
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Statistics
    total_applications = db.Column(db.Integer, default=0)
    successful_applications = db.Column(db.Integer, default=0)
    
    # Fix the relationship - use foreign_keys to specify which column to use
    email_batches = db.relationship(
        'EmailBatch', 
        back_populates='user',
        lazy='dynamic',
        foreign_keys='EmailBatch.user_id'  # Explicitly specify which foreign key to use
    )
    
    # Add a relationship for batches approved by this user
    approved_batches = db.relationship(
        'EmailBatch',
        back_populates='approver',
        lazy='dynamic',
        foreign_keys='EmailBatch.approved_by'  # Explicitly specify the foreign key
    )
    
    @hybrid_property
    def success_rate(self):
        """Calculate success rate of applications"""
        if self.total_applications == 0:
            return 0
        return round((self.successful_applications / self.total_applications) * 100, 2)
    
    @hybrid_property
    def is_complete(self):
        """Check if user profile is complete"""
        required_fields = [self.phone, self.resume_file, self.cover_letter_template]
        return all(field is not None for field in required_fields)

    def update_stats(self):
        """Update user application statistics"""
        from app.models.batch import EmailBatch, BatchApplication
        try:
            total = BatchApplication.query.join(EmailBatch)\
                .filter(EmailBatch.user_id == self.id).count()
            successful = BatchApplication.query.join(EmailBatch)\
                .filter(EmailBatch.user_id == self.id, 
                       BatchApplication.status == 'sent').count()
            
            self.total_applications = total
            self.successful_applications = successful
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Error updating stats: {str(e)}")
            return False

    def update_last_login(self):
        """Update user's last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()

    def set_preference(self, key, value):
        """Set user preference"""
        if self.preferences is None:
            self.preferences = {}
        self.preferences[key] = value
        db.session.commit()

    def get_preference(self, key, default=None):
        """Get user preference"""
        return self.preferences.get(key, default) if self.preferences else default

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'phone': self.phone,
            'is_admin': self.is_admin,
            'total_applications': self.total_applications,
            'successful_applications': self.successful_applications,
            'success_rate': self.success_rate,
            'is_complete': self.is_complete,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

    def __repr__(self):
        return f'<User {self.email}>'

# SQLAlchemy event listeners
@event.listens_for(User, 'before_insert')
def set_created_at(mapper, connection, target):
    target.created_at = datetime.utcnow()

@event.listens_for(User, 'before_update')
def set_updated_at(mapper, connection, target):
    target.updated_at = datetime.utcnow()  # Fixed - removed the comma