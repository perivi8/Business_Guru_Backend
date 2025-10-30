"""
Security-hardened Flask application for TMIS Business Guru
Implements all critical security fixes
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_talisman import Talisman
import bcrypt
from pymongo import MongoClient
from bson import ObjectId
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys

# Import secure logger
from secure_logger import secure_logger, security_event
from secure_config import SecureConfig, get_allowed_origins, is_production

# Load environment variables
load_dotenv()

# Validate configuration before starting
try:
    SecureConfig.validate_config()
    secure_logger.info("Configuration validation successful")
except ValueError as e:
    secure_logger.critical(f"Configuration validation failed: {e}")
    sys.exit(1)

app = Flask(__name__)

# Apply secure configuration
app.config.from_object(SecureConfig)

# Initialize security middleware
# Flask-Talisman for security headers
if is_production():
    Talisman(app, **SecureConfig.TALISMAN_CONFIG)
    secure_logger.info("Security headers enabled (Flask-Talisman)")
else:
    secure_logger.warning("Running in development mode - security headers disabled")

# Initialize Rate Limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[SecureConfig.RATE_LIMITS['default']],
    storage_uri=SecureConfig.RATELIMIT_STORAGE_URL,
    strategy=SecureConfig.RATELIMIT_STRATEGY,
    headers_enabled=SecureConfig.RATELIMIT_HEADERS_ENABLED
)
secure_logger.info("Rate limiting initialized")

# Configure CORS with specific origins only
cors = CORS(app, 
    origins=get_allowed_origins(),
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
    supports_credentials=True,
    expose_headers=["Content-Disposition", "Authorization"],
    send_wildcard=False,
    automatic_options=True,
    max_age=3600
)
secure_logger.info(f"CORS configured for origins: {get_allowed_origins()}")

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
    cors_allowed_origins=get_allowed_origins(),  # Specific origins only
    async_mode='threading',
    logger=False,
    engineio_logger=False,
    transports=['polling', 'websocket'],
    allow_upgrades=True,
    ping_timeout=60,
    ping_interval=25
)
secure_logger.info("SocketIO initialized with restricted CORS")

# MongoDB connection
secure_logger.info("Connecting to MongoDB...")
try:
    client = MongoClient(SecureConfig.MONGODB_URI)
    db = client.tmis_business_guru
    db.command("ping")
    secure_logger.info("MongoDB connection successful")
    
    # Initialize collections
    users_collection = db.users
    clients_collection = db.clients
    pending_registrations_collection = db.pending_registrations
    
    # Log collection stats (without sensitive data)
    user_count = users_collection.count_documents({})
    client_count = clients_collection.count_documents({})
    secure_logger.info(f"Database initialized: {user_count} users, {client_count} clients")
    
except Exception as e:
    secure_logger.critical(f"MongoDB connection failed: {str(e)}")
    db = None
    users_collection = None
    clients_collection = None
    pending_registrations_collection = None

# JWT Error Handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    security_event('token_expired', {'user_id': jwt_payload.get('sub')})
    return jsonify({
        'msg': 'Token has expired',
        'error': 'expired_token'
    }), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    security_event('invalid_token', {'error': str(error)})
    return jsonify({
        'msg': 'Invalid token format or signature',
        'error': 'invalid_token'
    }), 422

@jwt.unauthorized_loader
def missing_token_callback(error):
    security_event('missing_token', {'path': request.path})
    return jsonify({
        'msg': 'Authorization token is required',
        'error': 'missing_token'
    }), 401

# Health check endpoints (no authentication required)
@app.route('/', methods=['GET'])
@limiter.exempt
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'TMIS Business Guru Backend is running',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '2.0.0-secure'
    }), 200

@app.route('/api/health', methods=['GET'])
@limiter.exempt
def api_health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# Protected status endpoint (admin only)
@app.route('/api/status', methods=['GET'])
@jwt_required()
@limiter.limit("10 per minute")
def comprehensive_status():
    """Comprehensive status endpoint - admin only"""
    try:
        # Verify admin role
        current_user_id = get_jwt_identity()
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        
        if not user or user.get('role') != 'admin':
            security_event('unauthorized_status_access', {'user_id': current_user_id})
            return jsonify({'error': 'Admin access required'}), 403
        
        # Test database connection
        db_status = "Connected" if db else "Not connected"
        
        # Return sanitized status (no sensitive data)
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': {
                'status': db_status,
                'collections': ['users', 'clients', 'pending_registrations']
            },
            'environment': {
                'flask_env': os.getenv('FLASK_ENV', 'Not set'),
                'debug_mode': app.debug
            }
        }), 200
        
    except Exception as e:
        secure_logger.error(f"Status check failed: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Status check failed'
        }), 500

# Login endpoint with rate limiting
@app.route('/api/login', methods=['POST'])
@limiter.limit(SecureConfig.RATE_LIMITS['login'])
def login():
    """User login with rate limiting and security logging"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            security_event('login_missing_credentials', {'email': email})
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = users_collection.find_one({'email': email})
        
        if not user:
            security_event('login_user_not_found', {'email': email})
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password']):
            security_event('login_invalid_password', {'email': email})
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Check user status
        user_status = user.get('status', 'active')
        if user_status == 'pending':
            security_event('login_pending_approval', {'email': email})
            return jsonify({'error': 'Account pending approval'}), 403
        elif user_status == 'paused':
            security_event('login_account_paused', {'email': email})
            return jsonify({'error': 'Account is paused'}), 403
        
        # Create JWT token
        access_token = create_access_token(
            identity=str(user['_id']),
            additional_claims={'role': user.get('role', 'user')}
        )
        
        secure_logger.info(f"User logged in successfully: {email}")
        
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

# Register endpoint with rate limiting
@app.route('/api/register', methods=['POST'])
@limiter.limit(SecureConfig.RATE_LIMITS['register'])
def register():
    """User registration with rate limiting"""
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        confirm_password = data.get('confirmPassword', '')
        
        # Validation
        if not all([username, email, password, confirm_password]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        if len(password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
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
        secure_logger.info(f"New registration pending approval: {email}")
        
        return jsonify({
            'message': 'Registration submitted for approval',
            'registration_id': str(result.inserted_id)
        }), 201
        
    except Exception as e:
        secure_logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

# Token validation endpoint
@app.route('/api/validate-token', methods=['GET'])
@jwt_required()
@limiter.limit("30 per minute")
def validate_token():
    """Validate JWT token"""
    try:
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        return jsonify({
            'valid': True,
            'user_id': current_user_id,
            'role': claims.get('role', 'user'),
            'message': 'Token is valid'
        }), 200
        
    except Exception as e:
        secure_logger.error(f"Token validation error: {str(e)}")
        return jsonify({'valid': False, 'error': 'Token validation failed'}), 401

# User status check endpoint
@app.route('/api/user-status', methods=['GET'])
@jwt_required()
@limiter.limit("60 per minute")
def user_status():
    """Check if user account still exists and is active"""
    try:
        current_user_id = get_jwt_identity()
        user = users_collection.find_one({'_id': ObjectId(current_user_id)})
        
        if not user:
            security_event('user_deleted_check', {'user_id': current_user_id})
            return jsonify({'error': 'user_deleted', 'message': 'User account no longer exists'}), 401
        
        if user.get('status') == 'paused':
            return jsonify({'error': 'user_paused', 'message': 'User account is paused'}), 403
        
        return jsonify({'status': 'active', 'message': 'User account is active'}), 200
        
    except Exception as e:
        secure_logger.error(f"User status check error: {str(e)}")
        return jsonify({'error': 'Status check failed'}), 500

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

@app.errorhandler(500)
def internal_error(e):
    secure_logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

# Import and register blueprints
try:
    from client_routes import client_bp
    app.register_blueprint(client_bp, url_prefix='/api')
    secure_logger.info("Client routes registered")
except ImportError as e:
    secure_logger.warning(f"Could not import client_routes: {e}")

try:
    from enquiry_routes import enquiry_bp
    app.register_blueprint(enquiry_bp, url_prefix='/api')
    secure_logger.info("Enquiry routes registered")
except ImportError as e:
    secure_logger.warning(f"Could not import enquiry_routes: {e}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    if is_production():
        secure_logger.info(f"Starting production server on port {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=False)
    else:
        secure_logger.warning(f"Starting development server on port {port}")
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
