from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from .utils.sms_handler import SMSHandler
from .utils.validator import validate_phone_numbers
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create Blueprint
sms = Blueprint('sms', __name__, url_prefix='/sms')

# Require consent for all SMS routes
def consent_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('sms_consent_given'):
            return redirect(url_for('sms.consent'))
        return f(*args, **kwargs)
    return decorated_function

@sms.route('/consent')
@login_required
def consent():
    return render_template('consent.html')

@sms.route('/set-consent', methods=['POST'])
@login_required
def set_consent():
    session['sms_consent_given'] = True
    return jsonify({'success': True})

@sms.route('/')
@login_required
@consent_required
def index():
    """Render the SMS platform homepage"""
    return render_template('sms/index.html')

@sms.route('/send', methods=['POST'])
@login_required
@consent_required
def send_sms():
    """Handle SMS sending requests"""
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'recipients' not in data or 'message' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: recipients and message'
            }), 400
            
        # Validate phone numbers
        recipients = data['recipients']
        message = data['message']
        
        valid_numbers, invalid_numbers = validate_phone_numbers(recipients)
        
        if not valid_numbers:
            return jsonify({
                'success': False,
                'error': 'No valid phone numbers provided',
                'invalid_numbers': invalid_numbers
            }), 400
            
        # Initialize SMS handler
        sms_handler = SMSHandler()
        
        # Send messages
        results = sms_handler.send_bulk_sms(valid_numbers, message)
        
        return jsonify({
            'success': True,
            'results': results,
            'invalid_numbers': invalid_numbers
        })
        
    except Exception as e:
        logger.error(f"Error in send_sms: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@sms.route('/status/<message_id>')
def message_status(message_id):
    """Get the status of a sent message"""
    try:
        sms_handler = SMSHandler()
        status = sms_handler.get_message_status(message_id)
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"Error in message_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@sms.route('/validate-number', methods=['POST'])
@login_required
@consent_required
def validate_number():
    # Number validation logic will be implemented here
    pass 