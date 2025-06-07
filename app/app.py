from flask import Flask, render_template, request, jsonify, url_for, redirect, Response, session
from flask_login import LoginManager, login_required, current_user
import pandas as pd
import os
from werkzeug.utils import secure_filename
import urllib.parse
import logging
import traceback
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from functools import wraps
import re
import sys
import secrets
from .config import Config
from .models.user import db, User
from .auth.routes import auth

# Security headers
def security_headers(response: Response) -> Response:
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' cdn.jsdelivr.net; img-src 'self' data:;"
    response.headers['Referrer-Policy'] = 'strict-origin-origin-when-cross-origin'
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    return response

# Create logs directory if it doesn't exist
logs_dir = os.path.join('app', 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Configure logging with sensitive data masking
class SensitiveDataFilter(logging.Filter):
    def filter(self, record):
        if hasattr(record, 'msg'):
            record.msg = str(record.msg)
            # Mask phone numbers in log messages
            record.msg = re.sub(r'(\d{2})\d+(\d{4})', r'\1****\2', record.msg)
        return True

# Configure detailed formatter
detailed_formatter = logging.Formatter(
    '\n%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]:\n'
    'Message: %(message)s\n'
    'Function: %(funcName)s\n'
    '%(separator)s'
)

# Add separator to formatter context
class DebugLogRecord(logging.LogRecord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.separator = '-' * 80

logging.setLogRecordFactory(DebugLogRecord)

# Configure file handler for all logs
file_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'app.log'),
    maxBytes=1024 * 1024,
    backupCount=10
)
file_handler.setFormatter(detailed_formatter)
file_handler.setLevel(logging.DEBUG)
file_handler.addFilter(SensitiveDataFilter())

# Configure debug file handler for real-time monitoring
debug_handler = RotatingFileHandler(
    os.path.join(logs_dir, 'debug.log'),
    maxBytes=1024 * 1024,
    backupCount=5
)
debug_handler.setFormatter(detailed_formatter)
debug_handler.setLevel(logging.DEBUG)

# Configure console handler for immediate output
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(detailed_formatter)
console_handler.setLevel(logging.DEBUG)

# Setup logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set to DEBUG level to capture all logs
logger.addHandler(file_handler)
logger.addHandler(debug_handler)
logger.addHandler(console_handler)

# Function to log detailed debug information
def log_debug_info(message, extra_info=None):
    """
    Log detailed debug information with context
    """
    debug_message = [message]
    if extra_info:
        debug_message.extend([f"{k}: {v}" for k, v in extra_info.items()])
    logger.debug('\n'.join(debug_message))

app = Flask(__name__)
app.debug = True  # Enable Flask debug mode

# Load configuration
app.config.from_object(Config)

# Initialize SQLAlchemy
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access MessagePilot.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Register blueprints
app.register_blueprint(auth, url_prefix='/auth')

# Apply security headers to all responses
app.after_request(security_headers)

# Create database tables
with app.app_context():
    db.create_all()

# Protect all routes with login_required
@app.before_request
def require_login():
    public_endpoints = [
        'auth.login',
        'auth.register',
        'static',
        'auth.reset_password_request',
        'auth.reset_password'
    ]
    
    if not current_user.is_authenticated:
        if request.endpoint and \
           request.endpoint not in public_endpoints and \
           not request.endpoint.startswith('static.'):
            return redirect(url_for('auth.login'))

# Main routes
@app.route('/')
@login_required
def index():
    """Render the homepage"""
    return render_template('index.html')

@app.route('/whatsapp')
@login_required
def whatsapp():
    """Render the WhatsApp platform page"""
    return render_template('whatsapp.html')

@app.route('/privacy')
def privacy():
    """Render the privacy policy page"""
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    """Render the terms of service page"""
    return render_template('terms.html')

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file uploads"""
    try:
        # Validate file presence
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file uploaded'
            }), 400
            
        file = request.files['file']
        
        # Validate filename
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected'
            }), 400
            
        if not allowed_file(file.filename):
            return jsonify({
                'success': False,
                'error': 'Invalid file type'
            }), 400
            
        # Secure the filename and save
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Process the file
        results = process_uploaded_file(filepath)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@app.route('/generate_links', methods=['POST'])
@login_required
def generate_links():
    """Generate WhatsApp links from uploaded data"""
    try:
        data = request.get_json()
        
        if not data or 'rows' not in data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
            
        results = []
        for row in data['rows']:
            try:
                # Create message for this contact
                message = create_message(row)
                
                # Format phone number
                phone = process_phone_number(row.get('Phone', ''))
                if not phone:
                    phone = process_phone_number(row.get('Mobile', ''))
                if not phone:
                    phone = process_phone_number(row.get('Work Phone', ''))
                    
                if not phone:
                    results.append({
                        'success': False,
                        'error': 'No valid phone number found',
                        'row': row
                    })
                    continue
                    
                # Generate WhatsApp link
                whatsapp_link = f"https://wa.me/{phone}?text={urllib.parse.quote(message)}"
                
                results.append({
                    'success': True,
                    'phone': phone,
                    'message': message,
                    'link': whatsapp_link,
                    'row': row
                })
                
            except Exception as e:
                logger.error(f"Error processing row: {str(e)}\n{traceback.format_exc()}")
                results.append({
                    'success': False,
                    'error': str(e),
                    'row': row
                })
                
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"Error in generate_links: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# Load configuration from Config class
app.config.from_object(Config)

# All session configuration is now handled in Config class

# Secure configuration
app.config['UPLOAD_FOLDER'] = os.path.join('app', 'uploads')
app.config['SOURCE_FOLDER'] = os.path.join('data', 'source')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'xlsx', 'xls', 'csv'}

# Ensure upload and source directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SOURCE_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def clean_dataframe(df):
    """Clean and standardize the dataframe data"""
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # Replace various forms of empty/null values with NaN
    df = df.replace(['', 'nan', 'none', 'null', 'N/A', 'NA'], pd.NA)
    
    # Strip whitespace from string columns
    for col in df.select_dtypes(include=['object']):
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
        # Convert empty strings to NaN
        df[col] = df[col].replace(r'^\s*$', pd.NA, regex=True)
    
    # Clean phone numbers - remove non-numeric characters
    phone_columns = ['Phone', 'Mobile', 'Work Phone']
    for col in phone_columns:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: ''.join(filter(str.isdigit, str(x))) if pd.notna(x) else pd.NA)
            # Convert empty strings to NaN
            df[col] = df[col].replace('', pd.NA)
    
    return df

def validate_file_content(df):
    """Validate the content of the uploaded file and return detailed error messages"""
    errors = []
    warnings = []
    
    # Check for empty dataframe
    if df.empty:
        errors.append("The file contains no data")
        return errors, warnings
    
    # Check required columns
    required_columns = ['First Name', 'Last Name', 'Phone', 'Location', 
                       'Newest Engagement Date', 'Personal Volunteering Site URL',
                       'Mobile', 'Work Phone']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
        return errors, warnings
    
    # Add row index to DataFrame for error reporting
    df['Row_Number'] = df.index + 2  # Adding 2 because: 1 for 1-based indexing, 1 for header row
    
    # Check empty names
    empty_names = df[df[['First Name', 'Last Name']].isna().any(axis=1)]
    if not empty_names.empty:
        for _, row in empty_names.iterrows():
            missing_fields = []
            if pd.isna(row['First Name']):
                missing_fields.append('First Name')
            if pd.isna(row['Last Name']):
                missing_fields.append('Last Name')
            warnings.append(f"Row {row['Row_Number']}: Missing fields: {', '.join(missing_fields)}. This contact will be skipped.")
    
    # Check for missing phone numbers
    no_phone = df[df[['Phone', 'Mobile', 'Work Phone']].isna().all(axis=1)]
    if not no_phone.empty:
        for _, row in no_phone.iterrows():
            contact_name = f"{row['First Name'] if pd.notna(row['First Name']) else '[No First Name]'} {row['Last Name'] if pd.notna(row['Last Name']) else '[No Last Name]'}"
            warnings.append(f"Row {row['Row_Number']}: No phone number found for contact: {contact_name}. This contact will be skipped.")
    
    # Remove the temporary row number column
    df.drop('Row_Number', axis=1, inplace=True)
    
    return errors, warnings

def format_uk_phone(phone):
    """Format phone number to UK international format"""
    # Clean the phone number to only digits
    cleaned = ''.join(filter(str.isdigit, str(phone)))
    
    # If empty after cleaning, return empty string
    if not cleaned:
        return ''
    
    # Handle UK numbers
    if cleaned.startswith('0'):
        # Remove leading 0 and add 44
        cleaned = '44' + cleaned[1:]
    elif not cleaned.startswith('44') and len(cleaned) > 7:
        # If it doesn't start with 44 or 0, assume it needs 44
        cleaned = '44' + cleaned
    
    return cleaned

def create_message(contact):
    """
    Create a personalized message for a contact using their information.
    Args:
        contact: Dictionary or Series containing contact information
    Returns:
        str: Formatted message with contact details
    """
    try:
        # Get name components
        first_name = str(contact.get('First Name', '')).strip()
        last_name = str(contact.get('Last Name', '')).strip()
        full_name = f"{first_name} {last_name}".strip()
        
        # Get other details
        location = str(contact.get('Location', '')).strip()
        engagement_date = str(contact.get('Newest Engagement Date', '')).strip()
        volunteer_url = str(contact.get('Personal Volunteering Site URL', '')).strip()
        
        # Build the message
        message_parts = []
        
        # Add greeting
        if first_name:
            message_parts.append(f"Hi {first_name},")
        else:
            message_parts.append("Hi,")
            
        # Add main message
        message_parts.append("I hope this message finds you well.")
        
        # Add location context if available
        if location:
            message_parts.append(f"I noticed you're in {location}.")
            
        # Add engagement date context if available
        if engagement_date:
            message_parts.append(f"Your last engagement was on {engagement_date}.")
            
        # Add volunteer URL if available
        if volunteer_url:
            message_parts.append(f"You can check your volunteering details here: {volunteer_url}")
            
        # Add closing
        message_parts.append("Best regards,")
        message_parts.append("[Your Name]")
        
        # Join all parts with proper spacing
        return "\n\n".join(message_parts)
        
    except Exception as e:
        logger.error(f"Error creating message for contact: {str(e)}")
        return "Error creating personalized message."

def safe_get_value(row, column, default='N/A'):
    """
    Safely get a value from a pandas row, handling NaN and missing values.
    Returns JSON-safe values (no NaN).
    """
    try:
        value = row.get(column, default)
        # Check if it's pandas NaN or numpy NaN
        if pd.isna(value) or (hasattr(value, '__class__') and 'nan' in str(value).lower()):
            return default
        # Convert to string and strip if it's a string-like object
        if isinstance(value, str):
            return value.strip()
        return str(value) if value is not None else default
    except Exception:
        return default

def process_uploaded_file(filepath):
    """
    Process the uploaded file and extract contact information.
    Returns:
        tuple: (dict with results or error, HTTP status code)
    """
    # Initialize warnings list at function scope
    warnings = []
    
    try:
        log_debug_info("ENTERING process_uploaded_file", {
            "filepath": filepath,
            "file_exists": os.path.exists(filepath),
            "warnings_initialized": len(warnings)
        })
        
        log_debug_info("Starting file processing", {
            "filepath": filepath,
            "file_size": os.path.getsize(filepath),
            "file_type": os.path.splitext(filepath)[1]
        })

        # Validate file exists
        if not os.path.exists(filepath):
            return {'error': 'File not found'}, 400

        # Read the file
        try:
            if filepath.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(filepath)
                log_debug_info("Read Excel file", {"shape": df.shape, "columns": list(df.columns)})
            else:
                df = pd.read_csv(filepath)
                log_debug_info("Read CSV file", {"shape": df.shape, "columns": list(df.columns)})
        except pd.errors.EmptyDataError:
            return {'error': 'The uploaded file is empty'}, 400
        except pd.errors.ParserError as e:
            return {'error': f'Failed to parse file: {str(e)}'}, 400
        except Exception as e:
            return {'error': f'Failed to read file: {str(e)}'}, 400

        # Clean and validate the dataframe
        try:
            df = clean_dataframe(df)
            errors, validation_warnings = validate_file_content(df)
            warnings.extend(validation_warnings)  # Add validation warnings to main warnings list
            
            if errors:
                log_debug_info("Validation errors found", {"errors": errors})
                return {'error': errors[0], 'warnings': warnings}, 400
        except Exception as e:
            return {'error': f'Data validation failed: {str(e)}'}, 400
        
        results = []
        for idx, row in df.iterrows():
            try:
                log_debug_info(f"Processing row {idx + 2}", {
                    "row_data": {k: str(v) for k, v in row.items()}
                })

                # Get best available phone number
                phone = None
                for col in ['Mobile', 'Phone', 'Work Phone']:
                    if col in row and not pd.isna(row[col]):
                        original_phone = str(row[col])
                        phone = process_phone_number(row[col])
                        if phone:
                            log_debug_info(f"Found valid phone in column {col}", {
                                "original": original_phone,
                                "processed": phone,
                                "length": len(phone)
                            })
                            break
                
                if not phone:
                    log_debug_info(f"No valid phone number found in row {idx + 2}")
                    continue

                # Create result object with masked phone for display
                # Use safe_get_value to ensure no NaN values in JSON
                first_name = safe_get_value(row, 'First Name', '')
                last_name = safe_get_value(row, 'Last Name', '')
                location = safe_get_value(row, 'Location', 'N/A')
                engagement_date = safe_get_value(row, 'Newest Engagement Date', 'N/A')
                volunteer_url = safe_get_value(row, 'Personal Volunteering Site URL', '')
                
                result = {
                    'id': idx,  # Add unique ID for frontend
                    'full_name': f"{first_name} {last_name}".strip(),
                    'First Name': first_name,
                    'Last Name': last_name,
                    'Location': location,
                    'phone': f"****-****-{phone[-4:]}",  # Consistent display format
                    'best_phone': phone,  # Clean international format for WhatsApp
                    'phone_display': f"****-****-{phone[-4:]}",  # Explicit display version
                    'phone_whatsapp': phone,  # Explicit WhatsApp version
                    'Newest Engagement Date': engagement_date,
                    'Personal Volunteering Site URL': volunteer_url if volunteer_url else None,
                    'selected': True  # Default to selected
                }
                
                log_debug_info(f"Created result for row {idx + 2}", {
                    "result": {k: v if k != 'best_phone' else '****' for k, v in result.items()}
                })
                results.append(result)
                
            except Exception as e:
                error_msg = f"Error processing row {idx + 2}: {str(e)}"
                log_debug_info(error_msg, {
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                # Continue processing other rows instead of failing completely
                warnings.append(error_msg)
                continue

        if not results:
            log_debug_info("No valid results generated")
            return {'error': 'No valid contacts found in the file', 'warnings': warnings}, 400

        log_debug_info("File processing completed", {
            "total_rows": len(df),
            "processed_results": len(results)
        })
        
        # Define available merge fields
        merge_fields = [
            {'field': '{first_name}', 'description': 'Contact\'s first name'},
            {'field': '{last_name}', 'description': 'Contact\'s last name'},
            {'field': '{full_name}', 'description': 'Contact\'s full name'},
            {'field': '{location}', 'description': 'Contact\'s location'},
            {'field': '{engagement_date}', 'description': 'Last engagement date'},
            {'field': '{volunteer_url}', 'description': 'Volunteering site URL'}
        ]
        
        log_debug_info("ABOUT TO RETURN SUCCESS from process_uploaded_file", {
            "results_count": len(results),
            "warnings_count": len(warnings),
            "merge_fields_count": len(merge_fields)
        })
        
        return {
            'results': results,
            'warnings': warnings,
            'merge_fields': merge_fields
        }, 200
        
    except Exception as e:
        error_msg = f"File processing failed: {str(e)}"
        log_debug_info("EXCEPTION in process_uploaded_file", {
            "error": str(e),
            "traceback": traceback.format_exc(),
            "warnings_length": len(warnings) if 'warnings' in locals() else "undefined"
        })
        log_debug_info(error_msg, {
            "error": str(e),
            "traceback": traceback.format_exc()
        })
        return {'error': error_msg}, 500

def format_error_message(error):
    """Format error message to be more user-friendly and detailed"""
    try:
        if isinstance(error, pd.errors.ParserError):
            return f"Failed to parse the file. Please ensure it's a valid spreadsheet format. Details: {str(error)}"
        elif isinstance(error, pd.errors.EmptyDataError):
            return "The uploaded file is empty or contains no data"
        elif isinstance(error, ValueError):
            return str(error)
        elif isinstance(error, KeyError):
            missing_column = str(error).strip("'")
            return f"Required column '{missing_column}' is missing from the spreadsheet"
        elif isinstance(error, Exception):
            error_type = type(error).__name__
            error_msg = str(error)
            if error_msg:
                return f"Error ({error_type}): {error_msg}"
            else:
                return f"An error occurred: {error_type}"
        else:
            return str(error)
    except Exception as e:
        logger.error(f"Error in format_error_message: {str(e)}")
        return str(error)

def sanitize_filename(filename):
    """Additional filename sanitization beyond secure_filename"""
    # Remove any potentially dangerous characters
    filename = secure_filename(filename)
    # Additional sanitization if needed
    return filename

def validate_file_size(file):
    """Validate file size before processing"""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    if size > app.config['MAX_CONTENT_LENGTH']:
        raise ValueError(f"File size exceeds maximum limit of {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)}MB")
    return True

def process_phone_number(phone):
    if not phone or pd.isna(phone):
        return None
        
    # Convert to string and clean
    phone_str = str(phone).strip()
    
    # Remove common formatting characters but preserve + at start
    # Keep + at beginning for international format detection
    if phone_str.startswith('+'):
        # International format: +44 7946 220153 → +447946220153
        phone = '+' + re.sub(r'[^\d]', '', phone_str[1:])
    else:
        # Remove all non-numeric characters
        phone = re.sub(r'[^\d]', '', phone_str)
    
    # Handle different number formats
    if phone.startswith('+'):
        # Already international format, remove + for WhatsApp
        phone = phone[1:]
        # Basic validation for international numbers
        if not (7 <= len(phone) <= 15):
            return None
    elif phone.startswith('0'):
        # UK national format: 07946220153 → 447946220153
        phone = '44' + phone[1:]
    elif phone.startswith('44'):
        # Already UK international format
        pass
    elif len(phone) == 10 and phone.startswith('7'):
        # UK mobile without leading 0: 7946220153 → 447946220153
        phone = '44' + phone
    else:
        # Unknown format - could be international without +
        # Only convert to UK if it looks like a UK number (10-11 digits starting with certain patterns)
        if len(phone) in [10, 11] and phone[0] in ['7', '8', '1', '2']:
            # Likely UK number, add 44
            if phone.startswith('0'):
                phone = '44' + phone[1:]
            else:
                phone = '44' + phone
        else:
            # Assume it's already in correct international format
            pass
    
    # Final validation
    if not (7 <= len(phone) <= 15):
        return None
        
    # Ensure it's all digits at this point
    if not phone.isdigit():
        return None
        
    return phone

@app.route('/process', methods=['POST'])
def process_file_endpoint():
    """Handle the /process endpoint"""
    try:
        data = request.get_json()
        # Process the data as needed
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Process endpoint error: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 