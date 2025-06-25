from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
import json
import os

learnership_bp = Blueprint('learnership', __name__)

def load_learnerships():
    """Load learnerships from JSON file"""
    json_path = os.path.join(current_app.root_path, 'data', 'learnerships.json')
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    
    # If file doesn't exist, create it with sample data
    if not os.path.exists(json_path):
        sample_data = {
            "categories": [
                "IT & Technology",
                "Business & Finance", 
                "Engineering",
                "Education"
            ],
            "learnerships": [
                {
                    "id": 1,
                    "company": "Tech Innovators",
                    "program": "Software Development Learnership",
                    "email": "careers@techinnovators.com",
                    "category": "IT & Technology",
                    "description": "Join our 12-month software development learnership program. You'll learn modern web development technologies including HTML, CSS, JavaScript, React, Node.js, and cloud deployment. Work on real projects with experienced mentors.",
                    "requirements": "• Matric certificate with Mathematics\n• Basic computer literacy\n• Strong problem-solving skills\n• Passion for technology\n• Good communication skills in English",
                    "duration": "12 months",
                    "location": "Johannesburg, Gauteng",
                    "stipend": "R5,000 per month",
                    "icon": "tech.png"
                }
            ]
        }
        with open(json_path, 'w') as f:
            json.dump(sample_data, f, indent=4)
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except Exception as e:
        print(f"Error loading JSON: {str(e)}")
        return {"categories": [], "learnerships": []}

@learnership_bp.route('/learnerships')
@login_required
def list_learnerships():
    category_filter = request.args.get('category')
    search = request.args.get('search')
    
    # Load data from JSON
    data = load_learnerships()
    learnerships = data.get('learnerships', [])
    categories = data.get('categories', [])
    
    # Ensure each learnership has an ID
    for idx, learnership in enumerate(learnerships):
        if 'id' not in learnership:
            learnership['id'] = idx + 1
    
    # Apply filters
    filtered_learnerships = learnerships
    
    if category_filter:
        filtered_learnerships = [l for l in filtered_learnerships if l.get('category') == category_filter]
    
    if search:
        search_lower = search.lower()
        filtered_learnerships = [l for l in filtered_learnerships 
                               if search_lower in l.get('company', '').lower() 
                               or search_lower in l.get('program', '').lower()
                               or search_lower in l.get('description', '').lower()]
    
    return render_template('learnership/list.html', 
                         learnerships=filtered_learnerships,
                         categories=categories,
                         selected_category=category_filter,
                         search_query=search)

@learnership_bp.route('/api/learnerships/<int:id>')
@login_required
def api_get_learnership(id):
    """Get single learnership details"""
    data = load_learnerships()
    learnerships = data.get('learnerships', [])
    
    # Find learnership by ID
    for idx, learnership in enumerate(learnerships):
        # Check both explicit ID and index-based ID
        learnership_id = learnership.get('id', idx + 1)
        if learnership_id == id:
            # Ensure all fields are present
            learnership['id'] = learnership_id
            
            # Add default values for missing fields
            if 'description' not in learnership:
                learnership['description'] = f"Join the {learnership.get('program', 'training program')} at {learnership.get('company', 'our company')}. This is an excellent opportunity to develop your skills and kickstart your career."
            
            if 'requirements' not in learnership:
                learnership['requirements'] = "• Matric certificate\n• Good communication skills\n• Willingness to learn\n• Team player\n• Basic computer literacy"
            
            if 'duration' not in learnership:
                learnership['duration'] = "12 months"
            
            if 'location' not in learnership:
                learnership['location'] = "Various locations"
            
            if 'stipend' not in learnership:
                learnership['stipend'] = "Competitive stipend"
            
            return jsonify(learnership)
    
    return jsonify({'error': 'Learnership not found'}), 404

@learnership_bp.route('/learnerships/<int:id>')
@login_required
def view_learnership(id):
    """View single learnership details page"""
    data = load_learnerships()
    learnerships = data.get('learnerships', [])
    
    # Find learnership by ID
    for idx, learnership in enumerate(learnerships):
        learnership_id = learnership.get('id', idx + 1)
        if learnership_id == id:
            learnership['id'] = learnership_id
            return render_template('learnership/view.html', learnership=learnership)
    
    flash('Learnership not found', 'error')
    return redirect(url_for('learnership.list_learnerships'))


@learnership_bp.route('/api/debug/learnerships')
@login_required
def debug_learnerships():
    """Debug endpoint to check learnership data"""
    data = load_learnerships()
    learnerships = data.get('learnerships', [])
    
    # Get first 3 learnerships for debugging
    sample = []
    for i, l in enumerate(learnerships[:3]):
        sample.append({
            'index': i,
            'id': l.get('id'),
            'id_type': type(l.get('id')).__name__,
            'program': l.get('program'),
            'company': l.get('company')
        })
    
    return jsonify({
        'total_count': len(learnerships),
        'sample_data': sample
    })