from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

customer = Blueprint('customer', __name__)

@customer.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return render_template('customer/dashboard.html')

@customer.route('/whatsapp')
@login_required
def whatsapp():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return render_template('whatsapp.html', 
                         user=current_user,
                         is_customer=True)

@customer.route('/sms')
@login_required
def sms():
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    return render_template('sms.html', 
                         user=current_user,
                         is_customer=True) 