from flask import Flask, render_template, request, jsonify, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from googletrans import Translator
from config import Config, DEPARTMENTS, ISSUE_CATEGORIES, STATUS_OPTIONS
from models import db, Complaint, DepartmentStats

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Create upload folder if not exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# Initialize translator
translator = Translator()

def translate_text(text):
    """
    Detect language and translate text.
    - If Hindi, translate to English.
    - If English, translate to Hindi.
    Returns translated text (English for priority detection).
    """
    try:
        # Detect language
        detected = translator.detect(text)
        lang_code = detected.lang
        
        if lang_code == 'hi':
            # Hindi detected - translate to English
            translated = translator.translate(text, src='hi', dest='en')
            return translated.text, lang_code
        elif lang_code == 'en':
            # English detected - translate to Hindi
            translated = translator.translate(text, src='en', dest='hi')
            return translated.text, lang_code
        else:
            # Other language - return as is with original lang
            return text, lang_code
    except Exception as e:
        print(f"Translation error: {e}")
        return text, 'en'  # Default to English on error

def get_department(category):
    """Get department based on category"""
    return DEPARTMENTS.get(category, DEPARTMENTS['other'])

def calculate_priority(category, description):
    """Calculate priority based on category and description"""
    critical_keywords = ['accident', 'danger', 'unsafe', 'emergency', 'flood', 'electrocution']
    high_keywords = ['broken', 'damage', 'leak', 'blocked', 'overflow']
    
    desc_lower = description.lower()
    
    if any(keyword in desc_lower for keyword in critical_keywords):
        return 'critical'
    elif any(keyword in desc_lower for keyword in high_keywords):
        return 'high'
    elif category in ['electricity', 'traffic']:
        return 'high'
    return 'medium'

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Home page - Report an issue"""
    return render_template('index.html', categories=ISSUE_CATEGORIES)

@app.route('/track')
def track():
    """Track complaint status"""
    return render_template('track.html')

@app.route('/admin')
def admin():
    """Admin dashboard"""
    complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    return render_template('admin.html', complaints=complaints, statuses=STATUS_OPTIONS, departments=DEPARTMENTS)

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    # Get statistics
    total_complaints = Complaint.query.count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    pending = Complaint.query.filter_by(status='Pending').count()
    in_progress = Complaint.query.filter_by(status='In Progress').count()
    
    # Category-wise statistics
    category_stats = {}
    for cat, _ in ISSUE_CATEGORIES:
        count = Complaint.query.filter_by(category=cat).count()
        category_stats[cat] = count
    
    # Recent complaints for map
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(50).all()
    
    return render_template('analytics.html', 
                         total=total_complaints,
                         resolved=resolved,
                         pending=pending,
                         in_progress=in_progress,
                         category_stats=category_stats,
                         categories=ISSUE_CATEGORIES,
                         recent_complaints=recent_complaints)

# ==================== API ENDPOINTS ====================

@app.route('/api/report', methods=['POST'])
def report_issue():
    """Submit a new complaint"""
    try:
        # Get form data
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        citizen_name = request.form.get('citizen_name')
        citizen_phone = request.form.get('citizen_phone')
        citizen_email = request.form.get('citizen_email')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        address = request.form.get('address')
        
        # Handle file upload
        image_path = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f"uploads/{filename}"
        
        # Translation: detect language and translate
        # Store original description
        original_description = description
        
        # Translate for priority detection (English text for keyword matching)
        translated_text, detected_lang = translate_text(description)
        
        # Get department and priority using translated English text
        department = get_department(category)
        priority = calculate_priority(category, translated_text)
        
        # Create complaint
        complaint = Complaint(
            title=title,
            description=description,
            original_description=original_description,
            translated_description=translated_text,
            category=category,
            department=department,
            latitude=float(latitude) if latitude else 0.0,
            longitude=float(longitude) if longitude else 0.0,
            address=address,
            image_path=image_path,
            priority=priority,
            citizen_name=citizen_name,
            citizen_phone=citizen_phone,
            citizen_email=citizen_email
        )
        
        db.session.add(complaint)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Complaint submitted successfully!',
            'complaint_id': complaint.id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_api():
    """
    Translate text between Hindi and English.
    - Detects language automatically
    - If Hindi: translate to English
    - If English: translate to Hindi
    Returns original_text and translated_text
    """
    try:
        data = request.get_json()
        text = data.get('text', '').strip()
        
        if not text:
            return jsonify({
                'success': False,
                'message': 'No text provided'
            }), 400
        
        # Use the translate_text function
        translated_text, detected_lang = translate_text(text)
        
        return jsonify({
            'success': True,
            'original_text': text,
            'translated_text': translated_text,
            'detected_language': detected_lang
        })
        
    except Exception as e:
        print(f"Translation API error: {e}")
        return jsonify({
            'success': False,
            'message': 'Translation failed. Please try again.'
        }), 500

@app.route('/api/track/<complaint_id>', methods=['GET'])
def track_complaint(complaint_id):
    """Track complaint status by ID"""
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    return jsonify({'success': True, 'complaint': complaint.to_dict()})

@app.route('/api/complaints', methods=['GET'])
def get_all_complaints():
    """Get all complaints (admin)"""
    status = request.args.get('status')
    category = request.args.get('category')
    
    query = Complaint.query
    if status:
        query = query.filter_by(status=status)
    if category:
        query = query.filter_by(category=category)
    
    complaints = query.order_by(Complaint.created_at.desc()).all()
    return jsonify({'success': True, 'complaints': [c.to_dict() for c in complaints]})

@app.route('/api/complaint/<int:complaint_id>', methods=['GET'])
def get_complaint(complaint_id):
    """Get single complaint details"""
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    return jsonify({'success': True, 'complaint': complaint.to_dict()})

@app.route('/api/complaint/<int:complaint_id>', methods=['PUT'])
def update_complaint(complaint_id):
    """Update complaint status (admin)"""
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        return jsonify({'success': False, 'message': 'Complaint not found'}), 404
    
    try:
        data = request.get_json()
        
        if 'status' in data:
            complaint.status = data['status']
            if data['status'] == 'Resolved':
                complaint.resolved_at = datetime.utcnow()
        
        if 'priority' in data:
            complaint.priority = data['priority']
        
        if 'admin_comments' in data:
            complaint.admin_comments = data['admin_comments']
        
        if 'assigned_to' in data:
            complaint.assigned_to = data['assigned_to']
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Complaint updated successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    # Total stats
    total = Complaint.query.count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    pending = Complaint.query.filter_by(status='Pending').count()
    in_progress = Complaint.query.filter_by(status='In Progress').count()
    
    # Category breakdown
    category_data = []
    for cat, label in ISSUE_CATEGORIES:
        count = Complaint.query.filter_by(category=cat).count()
        resolved_count = Complaint.query.filter_by(category=cat, status='Resolved').count()
        category_data.append({
            'category': cat,
            'label': label,
            'total': count,
            'resolved': resolved_count
        })
    
    # Priority breakdown
    priority_data = []
    for priority in ['critical', 'high', 'medium', 'low']:
        count = Complaint.query.filter_by(priority=priority).count()
        priority_data.append({'priority': priority, 'count': count})
    
    # Department breakdown
    department_data = {}
    for dept in DEPARTMENTS.values():
        count = Complaint.query.filter_by(department=dept).count()
        if count > 0:
            department_data[dept] = count
    
    # Recent activity
    recent = Complaint.query.order_by(Complaint.created_at.desc()).limit(10).all()
    
    return jsonify({
        'success': True,
        'stats': {
            'total': total,
            'resolved': resolved,
            'pending': pending,
            'in_progress': in_progress,
            'resolution_rate': round((resolved/total*100) if total > 0 else 0, 1)
        },
        'category_data': category_data,
        'priority_data': priority_data,
        'department_data': department_data,
        'recent': [c.to_dict() for c in recent]
    })

# ==================== INITIALIZE ====================

@app.cli.command("init-db")
def init_db():
    """Initialize the database"""
    db.create_all()
    print("Database initialized successfully!")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5000)
