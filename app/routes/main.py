from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page route"""
    # If already logged in, redirect to dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    # Otherwise show the landing page
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard page route"""
    print(f"Dashboard accessed by: {current_user.name} (authenticated: {current_user.is_authenticated}")
    return render_template('dashboard.html')