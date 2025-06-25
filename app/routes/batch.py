from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from app.models.batch import EmailBatch, BatchApplication
from app.utils.email_service import EmailService
from app import db
from datetime import datetime
import json
import logging
from app.models.batch import EmailBatch, BatchApplication
logger = logging.getLogger(__name__)


batch_bp = Blueprint('batch', __name__)

@batch_bp.route('/batch/create', methods=['GET', 'POST'])
@login_required
def create_batch():
    try:
        print(f"DEBUG: Request method: {request.method}")
        print(f"DEBUG: Form data: {request.form}")
        
        if request.method == 'POST':
            # Check if this is the initial creation or final submission
            action = request.form.get('action', '')
            print(f"DEBUG: Action: {action}")
            
            if action == 'create_batch':
                # Initial batch creation - show preview
                learnership_data_json = request.form.get('learnership_data', '[]')
                print(f"DEBUG: Learnership data JSON: {learnership_data_json}")
                
                try:
                    selected_learnerships = json.loads(learnership_data_json)
                except json.JSONDecodeError:
                    flash('Invalid data format', 'error')
                    return redirect(url_for('learnership.list_learnerships'))
                
                if not selected_learnerships:
                    flash('No learnerships selected', 'warning')
                    return redirect(url_for('learnership.list_learnerships'))
                
                # Ensure all learnerships have required fields
                for learnership in selected_learnerships:
                    learnership.setdefault('category', 'General')
                    learnership.setdefault('description', 'Join our comprehensive training program.')
                
                # Create user data dictionary matching your User model
                user_data = {
                    'id': current_user.id,
                    'email': current_user.email,
                    'name': current_user.name,
                    'username': current_user.name,
                    'resume_filename': current_user.resume_file,
                    'phone': current_user.phone,
                    'is_complete': current_user.is_complete
                }
                
                print(f"DEBUG: Rendering template with {len(selected_learnerships)} learnerships")
                return render_template('batch/create.html', 
                                     learnerships=selected_learnerships,
                                     user=user_data)
            
            else:
                # This is the final submission from the create.html form
                learnership_data = request.form.get('learnerships')
                send_immediately = request.form.get('send_immediately', 'false') == 'true'
                
                print(f"DEBUG: Final submission - learnership data: {learnership_data}")
                print(f"DEBUG: Send immediately: {send_immediately}")
                
                if not learnership_data:
                    flash('No learnership data provided', 'error')
                    return redirect(url_for('learnership.list_learnerships'))
                
                try:
                    learnerships = json.loads(learnership_data)
                    print(f"DEBUG: Parsed {len(learnerships)} learnerships")
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON decode error: {e}")
                    flash('Invalid learnership data', 'error')
                    return redirect(url_for('learnership.list_learnerships'))
                
                # Check if user has uploaded resume
                if not current_user.resume_file:
                    print("DEBUG: User has no resume file")
                    flash('Please upload your resume before creating a batch', 'warning')
                    return redirect(url_for('profile.view_profile'))
                
                print(f"DEBUG: Creating batch for user {current_user.id}")
                
                # Create batch
                batch = EmailBatch(user_id=current_user.id, status='pending')
                db.session.add(batch)
                db.session.flush()  # This assigns the ID
                
                print(f"DEBUG: Batch created with ID: {batch.id}")
                
                # Create batch applications
                for learnership in learnerships:
                    learnership_id = int(learnership.get('id', 0))
                    print(f"DEBUG: Creating application for learnership ID: {learnership_id}")
                    
                    application = BatchApplication(
                        batch_id=batch.id,
                        learnership_id=learnership_id,
                        status='pending'
                    )
                    db.session.add(application)
                
                db.session.commit()
                print(f"DEBUG: Batch committed successfully")
                
                # Update user statistics
                current_user.update_stats()
                
                if send_immediately:
                    print(f"DEBUG: Redirecting to send emails for batch {batch.id}")
                    flash('Batch created! Sending emails...', 'info')
                    return redirect(url_for('batch.send_batch_emails', batch_id=batch.id))
                else:
                    print(f"DEBUG: Redirecting to batch detail for batch {batch.id}")
                    flash(f'Batch created successfully with {len(learnerships)} applications!', 'success')
                    return redirect(url_for('batch.batch_detail', batch_id=batch.id))
        
        else:
            # GET request - not supported for initial creation
            flash('Please select learnerships from the list', 'info')
            return redirect(url_for('learnership.list_learnerships'))
    
    except Exception as e:
        print(f"ERROR in create_batch: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        flash('An error occurred while creating the batch', 'error')
        return redirect(url_for('learnership.list_learnerships'))


@batch_bp.route('/batch/<int:batch_id>')
@login_required
def batch_detail(batch_id):
    batch = EmailBatch.query.get_or_404(batch_id)
    
    # Check ownership
    if batch.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    # Load learnership data from JSON
    from app.routes.learnership import load_learnerships
    data = load_learnerships()
    all_learnerships = data.get('learnerships', [])
    
    # Map learnership data to applications
    applications = []
    for app in batch.applications:
        learnership_data = next((l for l in all_learnerships if l.get('id') == app.learnership_id), None)
        if learnership_data:
            applications.append({
                'id': app.id,
                'status': app.status,
                'sent_at': app.sent_at,
                'error_message': app.error_message,
                'learnership': learnership_data
            })
    
    return render_template('batch/detail.html', 
                         batch=batch, 
                         applications=applications)

# In bulk_email_app/app/routes/batch.py
# REPLACE your existing send_batch_emails function with this:

@batch_bp.route('/batch/<int:batch_id>/send-all', methods=['GET', 'POST'])
@login_required
def send_batch_emails(batch_id):
    batch = EmailBatch.query.get_or_404(batch_id)
    
    # Check ownership
    if batch.user_id != current_user.id and not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('main.dashboard'))
    
    # Initialize email service
    email_service = EmailService()
    
    # Check if user has resume (using resume_file instead of resume_filename)
    if not current_user.resume_file:
        if request.method == 'GET':
            flash('Please upload your resume before sending applications', 'warning')
            return redirect(url_for('batch.batch_detail', batch_id=batch_id))
        else:
            return jsonify({
                'error': 'Please upload your resume before sending applications'
            }), 400
    
    # Load learnership data
    from app.routes.learnership import load_learnerships
    data = load_learnerships()
    all_learnerships = data.get('learnerships', [])
    
    success_count = 0
    failed_count = 0
    results = []
    
    for app in batch.applications:
        if app.status == 'sent':
            continue  # Skip already sent applications
        
        # Get learnership data
        learnership = next((l for l in all_learnerships if l.get('id') == app.learnership_id), None)
        
        if not learnership:
            app.status = 'failed'
            app.error_message = 'Learnership not found'
            failed_count += 1
            results.append({
                'learnership': 'Unknown',
                'status': 'failed',
                'message': 'Learnership not found'
            })
            continue
        
        # Send email
        try:
            result = email_service.send_application_email(
                to_email=learnership['email'],
                learnership=learnership,
                user=current_user
            )
            
            if result:
                app.status = 'sent'
                app.sent_at = datetime.utcnow()
                success_count += 1
                results.append({
                    'learnership': learnership['program'],
                    'company': learnership['company'],
                    'status': 'success',
                    'message': 'Sent successfully'
                })
            else:
                app.status = 'failed'
                app.error_message = 'Failed to send email'
                failed_count += 1
                results.append({
                    'learnership': learnership['program'],
                    'company': learnership['company'],
                    'status': 'failed',
                    'message': 'Failed to send email'
                })
                
        except Exception as e:
            app.status = 'failed'
            app.error_message = str(e)
            failed_count += 1
            results.append({
                'learnership': learnership['program'],
                'company': learnership['company'],
                'status': 'failed',
                'message': str(e)
            })
    
    # Update batch status
    if success_count > 0 and failed_count == 0:
        batch.status = 'completed'
    elif success_count == 0:
        batch.status = 'failed'
    else:
        batch.status = 'partial'
    
    db.session.commit()
    
    # Handle response based on request method
    if request.method == 'GET':
        flash(f'Sent {success_count} applications successfully!', 'success')
        return redirect(url_for('batch.batch_detail', batch_id=batch_id))
    else:
        return jsonify({
            'success': True,
            'sent': success_count,
            'failed': failed_count,
            'results': results,
            'message': f'Sent {success_count} applications successfully'
        })
    

@batch_bp.route('/api/send-single', methods=['POST'])
@login_required
def send_single_application():
    """Send application to a single learnership"""
    data = request.get_json()
    learnership_id = data.get('learnership_id')
    
    if not current_user.resume_filename:
        return jsonify({
            'success': False,
            'message': 'Please upload your resume first'
        }), 400
    
    # Load learnership data
    from app.routes.learnership import load_learnerships
    learnerships_data = load_learnerships()
    all_learnerships = learnerships_data.get('learnerships', [])
    
    # Find the specific learnership
    learnership = next((l for l in all_learnerships if l.get('id') == int(learnership_id)), None)
    
    if not learnership:
        return jsonify({'error': 'Learnership not found'}), 404
    
    # Send email
    email_service = EmailService()
    try:
        result = email_service.send_application_email(
            to_email=learnership['email'],
            learnership=learnership,
            user=current_user
        )
        
        if result:
            # Record the application
            batch = EmailBatch(user_id=current_user.id, status='completed')
            db.session.add(batch)
            db.session.flush()
            
            application = BatchApplication(
                batch_id=batch.id,
                learnership_id=int(learnership_id),
                status='sent',
                sent_at=datetime.utcnow()
            )
            db.session.add(application)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Application sent successfully to {learnership["company"]}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to send application'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@batch_bp.route('/batches')
@login_required
def list_batches():
    """List all batches for the current user"""
    batches = EmailBatch.query.filter_by(user_id=current_user.id)\
        .order_by(EmailBatch.created_at.desc()).all()
    return render_template('batch/list.html', batches=batches)

@batch_bp.route('/batch/status')
@login_required
def batch_status():
    batches = EmailBatch.query.filter_by(user_id=current_user.id)\
        .order_by(EmailBatch.created_at.desc()).all()
    return render_template('batch/status.html', batches=batches)

@batch_bp.route('/debug/user')
@login_required
def debug_user():
    """Debug endpoint to check user attributes"""
    user_attrs = {
        'id': current_user.id,
        'attributes': [attr for attr in dir(current_user) if not attr.startswith('_')]
    }
    return jsonify(user_attrs)


@batch_bp.route('/batch/<int:batch_id>/details')
@login_required
def batch_details(batch_id):
    """Return batch details for modal display"""
    batch = EmailBatch.query.filter_by(id=batch_id, user_id=current_user.id).first_or_404()  # ✅ CORRECT    
    # Return just the details part (not a full page)
    return render_template('batch/details_modal.html', batch=batch)