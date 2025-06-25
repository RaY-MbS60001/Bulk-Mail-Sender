from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app.utils.file_handler import FileHandler
from app import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def view_profile():
    return render_template('profile/view.html')

@profile_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        current_user.phone = request.form.get('phone')
        current_user.cover_letter_template = request.form.get('cover_letter_template')
        
        if 'resume' in request.files:
            resume_file = request.files['resume']
            filename = FileHandler.save_file(resume_file, 'resumes')
            if filename:
                current_user.resume_file = filename
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile.view_profile'))
    
    return render_template('profile/edit.html')