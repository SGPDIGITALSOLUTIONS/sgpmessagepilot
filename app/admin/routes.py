from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from app.models.user import User, db
from datetime import datetime, timedelta

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/')
@login_required
@admin_required
def dashboard():
    # Get statistics
    total_users = User.query.count()
    active_sessions = User.query.filter(
        User.last_login > datetime.utcnow() - timedelta(hours=24)
    ).count()
    
    # Placeholder for messages count
    messages_today = 0  # This should be implemented based on your message tracking
    
    # Placeholder for recent activities
    recent_activities = [
        {
            'description': 'New user registration',
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'description': 'System backup completed',
            'timestamp': (datetime.utcnow() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         active_sessions=active_sessions,
                         messages_today=messages_today,
                         recent_activities=recent_activities)

@admin.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@admin.route('/settings')
@login_required
@admin_required
def settings():
    return render_template('admin/settings.html')

@admin.route('/logs')
@login_required
@admin_required
def logs():
    return render_template('admin/logs.html') 