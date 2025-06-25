from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models.batch import EmailBatch, BatchApplication
from app.models.learnership import Learnership
from sqlalchemy import func
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('main.dashboard'))
    
    # Get general statistics
    total_users = User.query.count()
    total_applications = BatchApplication.query.count()
    success_rate = BatchApplication.query\
        .filter_by(status='sent').count() / total_applications * 100 if total_applications > 0 else 0
    
    # Get daily statistics for the past week
    today = datetime.now()
    week_ago = today - timedelta(days=7)
    
    daily_stats = db.session.query(
        func.date(BatchApplication.sent_at).label('date'),
        func.count(BatchApplication.id).label('count')
    ).filter(
        BatchApplication.sent_at >= week_ago
    ).group_by(
        func.date(BatchApplication.sent_at)
    ).all()
    
    return render_template('analytics/dashboard.html',
                         total_users=total_users,
                         total_applications=total_applications,
                         success_rate=success_rate,
                         daily_stats=daily_stats)

@analytics_bp.route('/analytics/data')
@login_required
def get_analytics_data():
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get faculty distribution
    faculty_stats = db.session.query(
        Learnership.faculty,
        func.count(BatchApplication.id)
    ).join(BatchApplication).group_by(Learnership.faculty).all()
    
    # Get status distribution
    status_stats = db.session.query(
        BatchApplication.status,
        func.count(BatchApplication.id)
    ).group_by(BatchApplication.status).all()
    
    return jsonify({
        'faculty_stats': dict(faculty_stats),
        'status_stats': dict(status_stats)
    })