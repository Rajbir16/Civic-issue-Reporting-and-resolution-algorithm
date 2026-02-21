import os

class Config:
    """Application configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'civic-voice-secret-key-2024'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///civic_issues.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Department mapping for auto-routing
DEPARTMENTS = {
    'roads': 'Public Works Department',
    'water': 'Water Supply Department',
    'electricity': 'Electricity Department',
    'drainage': 'Drainage Department',
    'sanitation': 'Sanitation Department',
    'parks': 'Parks & Gardens Department',
    'traffic': 'Traffic Police Department',
    'other': 'General Administration'
}

# Priority levels
PRIORITY_LEVELS = {
    'low': 1,
    'medium': 2,
    'high': 3,
    'critical': 4
}

# Issue categories
ISSUE_CATEGORIES = [
    ('roads', 'Potholes & Road Damage'),
    ('water', 'Water Leakage'),
    ('electricity', 'Broken Streetlights'),
    ('drainage', 'Blocked Drains'),
    ('sanitation', 'Garbage & Waste'),
    ('parks', 'Park Maintenance'),
    ('traffic', 'Traffic Signal Issues'),
    ('other', 'Other Issues')
]

# Status options
STATUS_OPTIONS = ['Pending', 'In Progress', 'Resolved', 'Rejected']
