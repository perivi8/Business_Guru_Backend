"""
Enhanced security-hardened Flask application for TMIS Business Guru
Includes all security improvements: rate limiting, account lockout, input validation, file security
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
import bcrypt
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys

# Import security modules
from secure_logger import secure_logger, security_event
from secure_config import SecureConfig, get_allowed_origins, is_production
from account_security import account_security
from input_validators import validate_login, validate_registration, ValidationError
from file_security import secure_file_handler

# Load environment variables
load_dotenv()

# Validate configuration before starting
try:
    SecureConfig.validate_config()
    secure_logger.info("✅ Configuration validation successful")
except ValueError as e:
    secure_logger.critical(f"❌ Configuration validation failed: {e}")
    sys.exit(1)

app = Flask(__name__)

# Apply secure configuration
app.config.from_object(SecureConfig)

# Initialize CSRF Protection
csrf = CSRFProtect(app)
secure_logger.info("✅ CSRF protection enabled")

# Initialize security middleware
if is_production():
    Talisman(app, **SecureConfig.TALISMAN_CONFIG)
    secure_logger.info("✅ Security headers enabled (Flask-Talisman)")
else:
    secure_logger.warning("⚠️  Running in development mode - some security features disabled")

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[SecureConfig.RATE_LIMITS['default']],
    storage_uri=SecureConfig.RATELIMIT_STORAGE_URL,
    strategy=SecureConfig.RATELIMIT_STRATEGY,
    headers_enabled=SecureConfig.RATELIMIT_HEADERS_ENABLED
)
secure_logger.info("✅ Rate limiting initialized")

# Configure CORS with specific origins only
cors = CORS(app, 
    origins=get_allowed_origins(),
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin", "X-CSRFToken"],
    supports_credentials=True,
    expose_headers=["Content-Disposition", "Authorization"],
    send_wildcard=False,
    automatic_options=True,
    max_age=3600
)
secure_logger.info(f"✅ CORS configured for {len(get_allowed_origins())} origins")

# Initialize JWT Manager
jwt = JWTManager(app)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Handle OPTIONS requests before JWT validation
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return

# Initialize SocketIO with restricted CORS
socketio = SocketIO(
    app,
    cors_allowed_origins=get_allowed_origins(),
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    transports=['polling', 'websocket'],
    allow_upgrades=True,
    ping_timeout=60,
    ping_interval=25
)
secure_logger.info("✅ SocketIO initialized with restricted CORS")

# MongoDB connection
secure_logger.info("🔄 Connecting to MongoDB...")
try:
    client = MongoClient(SecureConfig.MONGODB_URI)
    db = client.tmis_business_guru
    db.command("ping")
    secure_logger.info("✅ MongoDB connection successful")
    
    # Initialize collections
    users_collection = db.users
    clients_collection = db.clients
    pending_registrations_collection = db.pending_registrations
    
    user_count = users_collection.count_documents({})
    client_count = clients_collection.count_documents({})
    secure_logger.info(f"📊 Database: {user_count} users, {client_count} clients")
    
except Exception as e:
    secure_logger.critical(f"❌ MongoDB connection failed: {str(e)}")
    db = None
    users_collection = None
    clients_collection = None
    pending_registrations_collection = None

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    security_event('token_expired', {'user_id': jwt_payload.get('sub')})
    return jsonify({'msg': 'Token has expired', 'error': 'expired_token'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    security_event('invalid_token', {'error': str(error)})
    return jsonify({'msg': 'Invalid token', 'error': 'invalid_token'}), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    security_event('missing_token', {'path': request.path})
    return jsonify({'msg': 'Authorization required', 'error': 'missing_token'}), 401

# Health check endpoints
@app.route('/', methods=['GET'])
@limiter.exempt
@csrf.exempt
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'TMIS Business Guru Backend - Enhanced Security',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.1.0-enhanced'
    }), 200

@app.route('/api/health', methods=['GET'])
@limiter.exempt
@csrf.exempt
def api_health_check():
    return jsonify({
        'status': 'healthy',
        'security_features': [
            'rate_limiting',
            'account_lockout',
            'input_validation',
            'file_security',
            'csrf_protection',
            'security_headers'
        ],
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Login endpoint with account lockout
@app.route('/api/login', methods=['POST'])
@limiter.limit(SecureConfig.RATE_LIMITS['login'])
@csrf.exempt  # CSRF not needed for stateless JWT
def login():
    """Enhanced login with account lockout and input validation"""
    try:
        data = request.get_json()
        
        # Validate input
        try:
            validated = validate_login(data)
            email = validated['email']
            password = validated['password']
        except ValidationError as e:
            security_event('login_validation_failed', {'error': str(e)})
            return jsonify({'error': str(e)}), 400
        
        # Check if account is locked
        if account_security.is_locked(email):
            remaining = account_security.get_lockout_time_remaining(email)
            security_event('login_account_locked', {'email': email})
            return jsonify({
                'error': 'Account temporarily locked due to multiple failed attempts',
                'locked_until_seconds': remaining,
                'message': f'Please try again in {remaining // 60} minutes'
            }), 403
        
        # Find user
        user = users_collection.find_one({'email': email})
        
        if not user:
            # Record failed attempt
            lockout_info = account_security.record_failed_attempt(email)
            security_event('login_user_not_found', {'email': email})
            
            if lockout_info['locked']:
                return jsonify({
                    'error': 'Account locked due to multiple failed attempts',
                    'lockout_duration_minutes': lockout_info['lockout_duration_minutes']
                }), 403
            
            return jsonify({
                'error': 'Invalid credentials',
                'remaining_attempts': lockout_info.get('remaining_attempts')
            }), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            # Record failed attempt
            lockout_info = account_security.record_failed_attempt(email)
            security_event('login_invalid_password', {'email': email})
            
            if lockout_info['locked']:
                return jsonify({
                    'error': 'Account locked due to multiple failed attempts',
                    'lockout_duration_minutes': lockout_info['lockout_duration_minutes']
                }), 403
            
            return jsonify({
                'error': 'Invalid credentials',
                'remaining_attempts': lockout_info.get('remaining_attempts')
            }), 401
        
        # Check user status
        user_status = user.get('status', 'active')
        if user_status == 'pending':
            security_event('login_pending_approval', {'email': email})
            return jsonify({'error': 'Account pending approval'}), 403
        elif user_status == 'paused':
            security_event('login_account_paused', {'email': email})
            return jsonify({'error': 'Account is paused'}), 403
        
        # Successful login - clear failed attempts
        account_security.record_successful_login(email)
        
        # Create JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={'role': user.get('role', 'user')}
        )
        
        secure_logger.info(f"✅ User logged in: {email}")
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': str(user['_id']),
                'username': user.get('username'),
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        secure_logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

# Register endpoint with input validation
@app.route('/api/register', methods=['POST'])
@limiter.limit(SecureConfig.RATE_LIMITS['register'])
@csrf.exempt
def register():
    """Enhanced registration with input validation"""
    try:
        data = request.get_json()
        
        # Validate input
        try:
            validated = validate_registration(data)
        except ValidationError as e:
            security_event('registration_validation_failed', {'error': str(e)})
            return jsonify({'error': str(e)}), 400
        
        username = validated['username']
        email = validated['email']
        password = validated['password']
        
        # Check if user exists
        if users_collection.find_one({'email': email}):
            security_event('registration_duplicate_email', {'email': email})
            return jsonify({'error': 'Email already registered'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        # Create pending registration
        registration_data = {
            'username': username,
            'email': email,
            'password': hashed_password,
            'role': 'user',
            'status': 'pending',
            'created_at': datetime.utcnow()
        }
        
        result = pending_registrations_collection.insert_one(registration_data)
        secure_logger.info(f"✅ New registration pending: {email}")
        
        return jsonify({
            'message': 'Registration submitted for approval',
            'registration_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        secure_logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

# File upload endpoint with enhanced security
@app.route('/api/upload', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def upload_file():
    """Secure file upload with comprehensive validation"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Use secure file handler
        success, message, saved_filename = secure_file_handler.save_file(
            file, file.filename
        )
        
        if not success:
            security_event('file_upload_failed', {'reason': message})
            return jsonify({'error': message}), 400
        
        secure_logger.info(f"✅ File uploaded: {saved_filename}")
        
        return jsonify({
            'message': message,
            'filename': saved_filename
        }), 200
        
    except Exception as e:
        secure_logger.error(f"File upload error: {str(e)}")
        return jsonify({'error': 'File upload failed'}), 500

# Admin endpoint to unlock account
@app.route('/api/admin/unlock-account', methods=['POST'])
@jwt_required()
@limiter.limit("20 per minute")
def unlock_account():
    """Admin endpoint to manually unlock an account"""
    try:
        # Verify admin role
        current_user_id = get_jwt_identity()
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        
        if not user or user.get('role') != 'admin':
            security_event('unauthorized_unlock_attempt', {'user_id': current_user_id})
            return jsonify({'error': 'Admin access required'}), 403
        
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        account_security.unlock_account(email)
        secure_logger.info(f"✅ Account unlocked by admin: {email}")
        
        return jsonify({'message': f'Account {email} unlocked successfully'}), 200
        
    except Exception as e:
        secure_logger.error(f"Account unlock error: {str(e)}")
        return jsonify({'error': 'Unlock failed'}), 500

# Error handlers
@app.errorhandler(429)
def ratelimit_handler(e):
    security_event('rate_limit_exceeded', {
        'ip': request.remote_addr,
        'path': request.path
    })
    return jsonify({
        'error': 'Rate limit exceeded',
        'message': 'Too many requests. Please try again later.'
    }), 429

@app.errorhandler(400)
def bad_request_handler(e):
    return jsonify({'error': 'Bad request', 'message': str(e)}), 400

@app.errorhandler(500)
def internal_error(e):
    secure_logger.error(f"Internal server error: {str(e)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    secure_logger.info("="*50)
    secure_logger.info("🚀 TMIS Business Guru Backend - Enhanced Security")
    secure_logger.info("="*50)
    secure_logger.info(f"Environment: {os.getenv('FLASK_ENV', 'development')}")
    secure_logger.info(f"Port: {port}")
    secure_logger.info(f"Security Features: Rate Limiting, Account Lockout, Input Validation, File Security, CSRF Protection")
    secure_logger.info("="*50)
    
    if is_production():
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
