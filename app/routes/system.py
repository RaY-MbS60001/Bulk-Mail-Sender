# app/routes/system.py
from flask import Blueprint, jsonify
from app import db
import psutil

system_bp = Blueprint('system', __name__)

@system_bp.route('/health')
def health_check():
    try:
        # Check database
        db.session.execute('SELECT 1')
        
        # Get system stats
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'cpu_usage': cpu,
            'memory_usage': memory
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500