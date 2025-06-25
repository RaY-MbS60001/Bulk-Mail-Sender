from app import db
from datetime import datetime

class EmailBatch(db.Model):
    __tablename__ = 'email_batches'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_at = db.Column(db.DateTime)
    
    # Update relationships to use back_populates instead of backref
    user = db.relationship(
        'User', 
        back_populates='email_batches',
        foreign_keys=[user_id]
    )
    
    approver = db.relationship(
        'User',
        back_populates='approved_batches',
        foreign_keys=[approved_by]
    )
    
    applications = db.relationship('BatchApplication', backref='batch', lazy='dynamic')
    
    def __repr__(self):
        return f'<EmailBatch {self.id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'application_count': self.applications.count(),
            'sent_count': self.applications.filter_by(status='sent').count()
        }


class BatchApplication(db.Model):
    __tablename__ = 'batch_applications'
    
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('email_batches.id'), nullable=False)
    learnership_id = db.Column(db.Integer, db.ForeignKey('learnerships.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    error_message = db.Column(db.Text)
    sent_at = db.Column(db.DateTime)
    
    # Relationship to Learnership
    learnership = db.relationship('Learnership')
    
    def __repr__(self):
        return f'<BatchApplication {self.id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'status': self.status,
            'error_message': self.error_message,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'learnership': self.learnership.to_dict() if self.learnership else None
        }