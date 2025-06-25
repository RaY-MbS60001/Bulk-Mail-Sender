from app import db
from datetime import datetime

class Learnership(db.Model):
    __tablename__ = 'learnerships'  # Explicitly set table name to plural form
    
    # Rest of your model...
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    faculty = db.Column(db.String(100))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'company': self.company,
            'email': self.email,
            'faculty': self.faculty,
            'description': self.description,
            'requirements': self.requirements,
            'active': self.active
        }