from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Complaint(db.Model):
    """Complaint model for storing civic issues"""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    original_description = db.Column(db.Text)
    translated_description = db.Column(db.Text)
    category = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    
    # Location details
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    address = db.Column(db.String(500))
    
    # Media evidence
    image_path = db.Column(db.String(500))
    
    # Status tracking
    status = db.Column(db.String(20), default='Pending')
    priority = db.Column(db.String(20), default='medium')
    
    # User info
    citizen_name = db.Column(db.String(100))
    citizen_phone = db.Column(db.String(20))
    citizen_email = db.Column(db.String(100))
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Admin comments
    admin_comments = db.Column(db.Text)
    assigned_to = db.Column(db.String(100))
    
    def to_dict(self):
        """Convert complaint to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'original_description': self.original_description,
            'translated_description': self.translated_description,
            'category': self.category,
            'department': self.department,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'address': self.address,
            'image_path': self.image_path,
            'status': self.status,
            'priority': self.priority,
            'citizen_name': self.citizen_name,
            'citizen_phone': self.citizen_phone,
            'citizen_email': self.citizen_email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            'resolved_at': self.resolved_at.strftime('%Y-%m-%d %H:%M:%S') if self.resolved_at else None,
            'admin_comments': self.admin_comments,
            'assigned_to': self.assigned_to
        }

class DepartmentStats(db.Model):
    """Department statistics for analytics"""
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), unique=True)
    total_complaints = db.Column(db.Integer, default=0)
    resolved_complaints = db.Column(db.Integer, default=0)
    pending_complaints = db.Column(db.Integer, default=0)
    in_progress_complaints = db.Column(db.Integer, default=0)
