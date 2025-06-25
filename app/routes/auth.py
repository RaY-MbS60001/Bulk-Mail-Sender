from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User
from app import db
import requests
import json
from datetime import datetime
import os

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Login page with options for admin and client"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

# ==================== ADMIN LOGIN ====================
@auth_bp.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login with username and password"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        if not username or not password:
            flash('Username and password are required', 'error')
            return render_template('auth/admin_login.html')
        
        # Find admin user by username
        user = User.query.filter_by(username=username, is_admin=True).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            user.update_last_login()
            flash(f'Welcome back, Admin {user.name}!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Invalid admin credentials', 'error')
    
    return render_template('auth/admin_login.html')

# ==================== CLIENT LOGIN (Google OAuth) ====================
@auth_bp.route('/client-login')
def client_login():
    """Client login page for Google OAuth"""
    return render_template('auth/client_login.html')

@auth_bp.route('/google-auth', methods=['GET', 'POST'])
def google_auth():
    """Handle Google authentication for clients"""
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            name = request.form.get('name', '').strip()
            
            if not email or not name:
                flash('Email and name are required', 'error')
                return render_template('auth/client_login.html')
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if not user:
                # Create new client user
                user = User(
                    email=email,
                    name=name,
                    google_id=email,  # Use email as google_id for demo
                    is_admin=False,
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
                db.session.commit()
                flash(f'Welcome {name}! Your account has been created.', 'success')
            else:
                # Update existing user
                user.name = name
                if not user.google_id:
                    user.google_id = email
                user.update_last_login()
                flash(f'Welcome back {name}!', 'success')
            
            # Log in the user
            login_user(user, remember=True)
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Login failed: {str(e)}', 'error')
            return render_template('auth/client_login.html')
    
    return render_template('auth/client_login.html')

# ==================== LOGOUT ====================
@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    user_name = current_user.name
    is_admin = current_user.is_admin
    logout_user()
    
    message = f'Goodbye {"Admin " if is_admin else ""}{user_name}! You have been logged out.'
    flash(message, 'info')
    return redirect(url_for('auth.login'))

# ==================== UTILITY ROUTES ====================
@auth_bp.route('/create-demo-client')
def create_demo_client():
    """Create a demo client for testing"""
    try:
        demo_email = 'demo.client@example.com'
        demo_user = User.query.filter_by(email=demo_email).first()
        
        if demo_user:
            flash('Demo client already exists', 'info')
        else:
            demo_user = User(
                email=demo_email,
                name='Demo Client',
                google_id=demo_email,
                is_admin=False,
                created_at=datetime.utcnow()
            )
            db.session.add(demo_user)
            db.session.commit()
            flash(f'Demo client created: {demo_email}', 'success')
        
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash(f'Error creating demo client: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/switch-user')
@login_required
def switch_user():
    """Development route to switch between admin and client view"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    return render_template('auth/switch_user.html')