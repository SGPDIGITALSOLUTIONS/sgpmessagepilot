from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User, db
from urllib.parse import urlparse

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('customer.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        # Check if it's the customer or review login
        is_customer = (email == current_app.config['CUSTOMER_EMAIL'] and 
                      password == current_app.config['CUSTOMER_PASSWORD'])
        is_review = (email == current_app.config['REVIEW_EMAIL'] and 
                    password == current_app.config['REVIEW_PASSWORD'])
        
        if is_customer or is_review:
            # Create or get user
            user = User.query.filter_by(email=email).first()
            if not user:
                user = User(
                    email=email,
                    first_name='Review' if is_review else 'Customer',
                    last_name='User',
                    is_admin=False
                )
                user.set_password(password)
                db.session.add(user)
            else:
                # Ensure user is not admin
                user.is_admin = False
                user.set_password(password)  # Update password in case it changed
            
            db.session.commit()
            login_user(user, remember=remember)
            user.update_login_info()
            db.session.commit()
            return redirect(url_for('customer.dashboard'))
            
        # Regular user login
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            user.update_login_info()
            db.session.commit()
            
            if user.is_admin:
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('customer.dashboard'))
            
        flash('Invalid email or password', 'error')
    return render_template('auth/login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('customer.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered', 'error')
            return render_template('auth/register.html')
            
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth.route('/profile')
@login_required
def profile():
    return render_template('auth/profile.html') 