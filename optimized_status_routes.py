"""
Optimized Status Update Routes for TMIS Business Guru
Fast, lightweight endpoints for payment gateway and loan status updates
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from bson import ObjectId
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint for optimized status updates
status_bp = Blueprint('status', __name__)

def get_database_collections():
    """Get database collections - import from main app"""
    try:
        from client_routes import db, clients_collection, users_collection
        # Check if collections are properly initialized
        if db is None or clients_collection is None or users_collection is None:
            logger.error("Database collections not properly initialized")
            return None, None, None
        return db, clients_collection, users_collection
    except ImportError:
        logger.error("Failed to import database collections")
        return None, None, None
    except Exception as e:
        logger.error(f"Unexpected error importing database collections: {str(e)}")
        return None, None, None

def get_email_service():
    """Get email service - import from main app with production support"""
    try:
        # First try to import from email_service directly (production-ready)
        from email_service import email_service
        # EMAIL_SERVICE_AVAILABLE is not exported from email_service, so we assume it's available if import succeeds
        return True, email_service
    except ImportError:
        try:
            # Fallback to client_routes import
            from client_routes import EMAIL_SERVICE_AVAILABLE, email_service
            return EMAIL_SERVICE_AVAILABLE, email_service
        except ImportError:
            logger.warning("Email service not available")
            return False, None

def get_whatsapp_service():
    """Get WhatsApp service - import from main app"""
    try:
        from client_routes import WHATSAPP_SERVICE_AVAILABLE, client_whatsapp_service
        return WHATSAPP_SERVICE_AVAILABLE, client_whatsapp_service
    except ImportError:
        logger.warning("WhatsApp service not available")
        return False, None

def get_admin_name(admin_id):
    """Get admin name from user ID"""
    try:
        db, clients_collection, users_collection = get_database_collections()
        if users_collection is not None:
            admin = users_collection.find_one({'_id': ObjectId(admin_id)})
            if admin:
                return admin.get('username', admin.get('email', 'Admin'))
        return 'Admin'
    except Exception as e:
        logger.error(f"Error getting admin name: {str(e)}")
        return 'Admin'

def get_tmis_users():
    """Get all users with tmis.* email addresses"""
    try:
        db, clients_collection, users_collection = get_database_collections()
        if users_collection is not None:
            tmis_users = list(users_collection.find({
                'email': {'$regex': '^tmis\\.', '$options': 'i'}
            }))
            return tmis_users
        return []
    except Exception as e:
        logger.error(f"Error getting TMIS users: {str(e)}")
        return []

@status_bp.route('/clients/<client_id>/status/payment-gateway', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_payment_gateway_status(client_id):
    """
    OPTIMIZED: Update payment gateway status with minimal processing
    Fast endpoint for instant UI updates
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return response
    
    try:
        logger.info(f"🚀 Fast payment gateway update for client: {client_id}")
        
        # Get database collections
        db, clients_collection, users_collection = get_database_collections()
        if clients_collection is None:
            return jsonify({'error': 'Database not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        gateway = data.get('gateway')
        status = data.get('status')
        
        if not gateway or not status:
            return jsonify({'error': 'Gateway and status required'}), 400
        
        if status not in ['approved', 'not_approved', 'pending']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Get current user
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        user_role = claims.get('role')
        
        logger.info(f"👤 User: {current_user_id}, Role: {user_role}")
        logger.info(f"💳 Gateway: {gateway}, Status: {status}")
        
        # Find client
        client = clients_collection.find_one({'_id': ObjectId(client_id)})
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Prepare update data
        current_gateway_status = client.get('payment_gateways_status', {})
        updated_gateway_status = {**current_gateway_status, gateway: status}
        
        # FAST UPDATE: Minimal database operation
        update_result = clients_collection.update_one(
            {'_id': ObjectId(client_id)},
            {
                '$set': {
                    'payment_gateways_status': updated_gateway_status,
                    'updated_at': datetime.utcnow(),
                    'updated_by': current_user_id
                }
            }
        )
        
        if update_result.matched_count == 0:
            return jsonify({'error': 'Client not found'}), 404
        
        logger.info(f"✅ Payment gateway status updated successfully")
        
        # ASYNC NOTIFICATIONS: Send notifications in background (non-blocking)
        # This prevents the UI from waiting for email/WhatsApp processing
        import threading
        
        def send_notifications_async():
            """Send notifications in background thread"""
            try:
                # Get updated client data
                updated_client = clients_collection.find_one({'_id': ObjectId(client_id)})
                if not updated_client:
                    return
                
                # Send email notifications - SKIP for payment gateway updates
                # Email notifications are not needed for payment gateway status changes
                logger.info("📧 Skipping email notification for payment gateway update (as requested)")
                # NOTE: If email notifications are needed for payment gateway updates, uncomment the following code:
                # EMAIL_SERVICE_AVAILABLE, email_service = get_email_service()
                # logger.info(f"📧 Email service availability: {EMAIL_SERVICE_AVAILABLE}")
                # if EMAIL_SERVICE_AVAILABLE and email_service:
                #     try:
                #         admin_name = get_admin_name(current_user_id)
                #         tmis_users = get_tmis_users()
                #         
                #         email_sent = email_service.send_client_update_notification(
                #             client_data=updated_client,
                #             admin_name=admin_name,
                #             tmis_users=tmis_users,
                #             update_type=f"payment gateway {gateway} {status}"
                #         )
                #         
                #         if email_sent:
                #             logger.info(f"📧 Email notification sent successfully for payment gateway update")
                #         else:
                #             logger.error(f"📧 Email notification failed to send")
                #     except Exception as e:
                #         logger.error(f"📧 Email notification failed: {str(e)}")
                #         import traceback
                #         logger.error(f"📧 Email error traceback: {traceback.format_exc()}")
                
                # Send WhatsApp notifications using available method
                WHATSAPP_SERVICE_AVAILABLE, client_whatsapp_service = get_whatsapp_service()
                if WHATSAPP_SERVICE_AVAILABLE and client_whatsapp_service is not None:
                    try:
                        # Use the available method to send client update message with specific update type
                        # This will trigger the appropriate template based on the status
                        if hasattr(client_whatsapp_service, 'send_client_update_message'):
                            # Create a mock old client data to trigger the status change detection
                            old_client_data = client.copy()
                            old_client_data['payment_gateways_status'] = current_gateway_status
                            
                            whatsapp_result = client_whatsapp_service.send_client_update_message(
                                updated_client, "payment_gateway_approval", [], old_client_data
                            )
                            logger.info(f"📱 WhatsApp notification result: {whatsapp_result}")
                        else:
                            logger.warning("WhatsApp service does not have send_client_update_message method")
                    except Exception as e:
                        logger.error(f"📱 WhatsApp notification failed: {str(e)}")
                        
            except Exception as e:
                logger.error(f"💥 Async notification error: {str(e)}")
        
        # Start background notifications
        notification_thread = threading.Thread(target=send_notifications_async)
        notification_thread.daemon = True
        notification_thread.start()
        
        # Return immediate success response
        return jsonify({
            'success': True,
            'message': f'Payment gateway {gateway} status updated to {status}',
            'gateway': gateway,
            'status': status,
            'notifications_sent_async': True
        }), 200
        
    except Exception as e:
        logger.error(f"💥 Error updating payment gateway status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/clients/<client_id>/status/loan', methods=['PUT', 'OPTIONS'])
@jwt_required()
def update_loan_status(client_id):
    """
    OPTIMIZED: Update loan status with minimal processing
    Fast endpoint for instant UI updates
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return response
    
    try:
        logger.info(f"🚀 Fast loan status update for client: {client_id}")
        
        # Get database collections
        db, clients_collection, users_collection = get_database_collections()
        if clients_collection is None:
            return jsonify({'error': 'Database not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        loan_status = data.get('loan_status')
        
        if not loan_status:
            return jsonify({'error': 'Loan status required'}), 400
        
        if loan_status not in ['approved', 'hold', 'processing', 'rejected', 'soon']:
            return jsonify({'error': 'Invalid loan status'}), 400
        
        # Get current user
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        user_role = claims.get('role')
        
        logger.info(f"👤 User: {current_user_id}, Role: {user_role}")
        logger.info(f"💰 Loan Status: {loan_status}")
        
        # Find client
        client = clients_collection.find_one({'_id': ObjectId(client_id)})
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # FAST UPDATE: Minimal database operation
        update_result = clients_collection.update_one(
            {'_id': ObjectId(client_id)},
            {
                '$set': {
                    'loan_status': loan_status,
                    'updated_at': datetime.utcnow(),
                    'updated_by': current_user_id
                }
            }
        )
        
        if update_result.matched_count == 0:
            return jsonify({'error': 'Client not found'}), 404
        
        logger.info(f"✅ Loan status updated successfully")
        
        # ASYNC NOTIFICATIONS: Send notifications in background (non-blocking)
        import threading
        
        def send_notifications_async():
            """Send notifications in background thread"""
            try:
                # Get updated client data
                updated_client = clients_collection.find_one({'_id': ObjectId(client_id)})
                if not updated_client:
                    return
                
                # Send email notifications
                EMAIL_SERVICE_AVAILABLE, email_service = get_email_service()
                logger.info(f"📧 Email service availability: {EMAIL_SERVICE_AVAILABLE}")
                if EMAIL_SERVICE_AVAILABLE and email_service:
                    try:
                        admin_name = get_admin_name(current_user_id)
                        tmis_users = get_tmis_users()
                        
                        logger.info(f"📧 Sending email notification for loan status update:")
                        logger.info(f"   Admin: {admin_name}")
                        logger.info(f"   TMIS Users: {len(tmis_users)}")
                        logger.info(f"   Loan Status: {loan_status}")
                        
                        email_sent = email_service.send_client_update_notification(
                            client_data=updated_client,
                            admin_name=admin_name,
                            tmis_users=tmis_users,
                            update_type=f"loan status {loan_status}",
                            loan_status=loan_status
                        )
                        
                        if email_sent:
                            logger.info(f"📧 Email notification sent successfully for loan status update")
                        else:
                            logger.error(f"📧 Email notification failed to send")
                    except Exception as e:
                        logger.error(f"📧 Email notification failed: {str(e)}")
                        import traceback
                        logger.error(f"📧 Email error traceback: {traceback.format_exc()}")
                
                # Send WhatsApp notifications using the new loan status update method
                WHATSAPP_SERVICE_AVAILABLE, client_whatsapp_service = get_whatsapp_service()
                if WHATSAPP_SERVICE_AVAILABLE and client_whatsapp_service is not None:
                    try:
                        # Use the new loan status update message method
                        if hasattr(client_whatsapp_service, 'send_loan_status_update_message'):
                            whatsapp_result = client_whatsapp_service.send_loan_status_update_message(
                                updated_client, loan_status
                            )
                            logger.info(f"📱 Loan status WhatsApp notification result: {whatsapp_result}")
                        # Fallback to generic method if new method not available
                        elif hasattr(client_whatsapp_service, 'send_client_update_message'):
                            whatsapp_result = client_whatsapp_service.send_client_update_message(
                                updated_client, f"loan status {loan_status}", []
                            )
                            logger.info(f"📱 WhatsApp notification result (fallback): {whatsapp_result}")
                        else:
                            logger.warning("WhatsApp service does not have loan status update methods")
                    except Exception as e:
                        logger.error(f"📱 WhatsApp notification failed: {str(e)}")
                        
            except Exception as e:
                logger.error(f"💥 Async notification error: {str(e)}")
        
        # Start background notifications
        notification_thread = threading.Thread(target=send_notifications_async)
        notification_thread.daemon = True
        notification_thread.start()
        
        # Return immediate success response
        return jsonify({
            'success': True,
            'message': f'Loan status updated to {loan_status}',
            'loan_status': loan_status,
            'notifications_sent_async': True
        }), 200
        
    except Exception as e:
        logger.error(f"💥 Error updating loan status: {str(e)}")
        return jsonify({'error': str(e)}), 500

@status_bp.route('/clients/<client_id>/status/batch', methods=['PUT', 'OPTIONS'])
@jwt_required()
def batch_update_statuses(client_id):
    """
    OPTIMIZED: Batch update multiple statuses in one request
    Efficient for bulk operations
    """
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        return response
    
    try:
        logger.info(f"🚀 Batch status update for client: {client_id}")
        
        # Get database collections
        db, clients_collection, users_collection = get_database_collections()
        if clients_collection is None:
            return jsonify({'error': 'Database not available'}), 500
        
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get current user
        claims = get_jwt()
        current_user_id = get_jwt_identity()
        user_role = claims.get('role')
        
        # Find client
        client = clients_collection.find_one({'_id': ObjectId(client_id)})
        if not client:
            return jsonify({'error': 'Client not found'}), 404
        
        # Prepare update data
        update_data = {
            'updated_at': datetime.utcnow(),
            'updated_by': current_user_id
        }
        
        updates_made = []
        
        # Handle payment gateway updates
        if 'payment_gateways_status' in data:
            gateway_updates = data['payment_gateways_status']
            current_gateway_status = client.get('payment_gateways_status', {})
            updated_gateway_status = {**current_gateway_status, **gateway_updates}
            update_data['payment_gateways_status'] = updated_gateway_status
            updates_made.extend([f"gateway {k}: {v}" for k, v in gateway_updates.items()])
        
        # Handle loan status update
        if 'loan_status' in data:
            loan_status = data['loan_status']
            if loan_status in ['approved', 'hold', 'processing', 'rejected', 'soon']:
                update_data['loan_status'] = loan_status
                updates_made.append(f"loan status: {loan_status}")
        
        if not updates_made:
            return jsonify({'error': 'No valid updates provided'}), 400
        
        # FAST UPDATE: Single database operation
        update_result = clients_collection.update_one(
            {'_id': ObjectId(client_id)},
            {'$set': update_data}
        )
        
        if update_result.matched_count == 0:
            return jsonify({'error': 'Client not found'}), 404
        
        logger.info(f"✅ Batch status update completed: {updates_made}")
        
        # ASYNC NOTIFICATIONS: Send notifications in background
        import threading
        
        def send_notifications_async():
            """Send notifications in background thread"""
            try:
                updated_client = clients_collection.find_one({'_id': ObjectId(client_id)})
                if not updated_client:
                    return
                
                # Send consolidated email notification
                EMAIL_SERVICE_AVAILABLE, email_service = get_email_service()
                logger.info(f"📧 Email service availability: {EMAIL_SERVICE_AVAILABLE}")
                if EMAIL_SERVICE_AVAILABLE and email_service:
                    try:
                        admin_name = get_admin_name(current_user_id)
                        tmis_users = get_tmis_users()
                        
                        logger.info(f"📧 Sending batch email notification:")
                        logger.info(f"   Admin: {admin_name}")
                        logger.info(f"   TMIS Users: {len(tmis_users)}")
                        logger.info(f"   Updates: {updates_made}")
                        
                        email_sent = email_service.send_client_update_notification(
                            client_data=updated_client,
                            admin_name=admin_name,
                            tmis_users=tmis_users,
                            update_type=f"batch update: {', '.join(updates_made)}"
                        )
                        
                        if email_sent:
                            logger.info(f"📧 Batch email notification sent successfully")
                        else:
                            logger.error(f"📧 Batch email notification failed to send")
                    except Exception as e:
                        logger.error(f"📧 Batch email notification failed: {str(e)}")
                        import traceback
                        logger.error(f"📧 Batch email error traceback: {traceback.format_exc()}")
                        
            except Exception as e:
                logger.error(f"💥 Batch async notification error: {str(e)}")
        
        # Start background notifications
        notification_thread = threading.Thread(target=send_notifications_async)
        notification_thread.daemon = True
        notification_thread.start()
        
        # Return immediate success response
        return jsonify({
            'success': True,
            'message': f'Batch update completed: {", ".join(updates_made)}',
            'updates_made': updates_made,
            'notifications_sent_async': True
        }), 200
        
    except Exception as e:
        logger.error(f"💥 Error in batch status update: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Health check for optimized routes
@status_bp.route('/status/health', methods=['GET'])
def status_health_check():
    """Health check for optimized status routes"""
    return jsonify({
        'status': 'healthy',
        'message': 'Optimized status routes are working',
        'timestamp': datetime.utcnow().isoformat(),
        'features': [
            'fast_payment_gateway_updates',
            'fast_loan_status_updates',
            'batch_status_updates',
            'async_notifications'
        ]
    }), 200