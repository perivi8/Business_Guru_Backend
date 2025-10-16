import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging

# Enhanced production email fix import
try:
    from production_email_service_enhanced import EnhancedProductionEmailService
    ENHANCED_EMAIL_AVAILABLE = True
    print("✅ Enhanced production email service imported successfully")
except ImportError as e:
    print(f"⚠️ Enhanced production email service not available: {e}")
    try:
        from production_email_fix import ProductionEmailService
        PRODUCTION_EMAIL_AVAILABLE = True
        ENHANCED_EMAIL_AVAILABLE = False
        print("✅ Fallback production email service imported successfully")
    except ImportError as e2:
        print(f"⚠️ Production email service not available: {e2}")
        PRODUCTION_EMAIL_AVAILABLE = False
        ENHANCED_EMAIL_AVAILABLE = False

# Brevo email service import
try:
    import sib_api_v3_sdk
    from sib_api_v3_sdk.rest import ApiException
    BREVO_AVAILABLE = True
    print("✅ Brevo service imported successfully")
except ImportError as e:
    print(f"⚠️ Brevo service not available: {e}")
    BREVO_AVAILABLE = False
    sib_api_v3_sdk = None

class EmailService:
    def __init__(self):
        self.smtp_email = os.getenv('SMTP_EMAIL')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        # Detect production environment
        self.is_production = (
            os.getenv('FLASK_ENV') == 'production' or 
            os.getenv('RENDER') == 'true' or
            os.getenv('VERCEL') == '1'
        )
        
        # Initialize Brevo service for production
        self.brevo_service = None
        if BREVO_AVAILABLE:
            try:
                brevo_api_key = os.getenv('BREVO_API_KEY')
                if brevo_api_key:
                    print("🚀 Initializing Brevo API...")
                    configuration = sib_api_v3_sdk.Configuration()
                    configuration.api_key['api-key'] = brevo_api_key
                    self.brevo_service = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
                    
                    self.brevo_from_name = os.getenv('BREVO_FROM_NAME', 'TMIS Business Guru')
                    self.brevo_from_email = os.getenv('BREVO_FROM_EMAIL')
                    print(f"✅ Brevo initialized successfully")
                    print(f"📧 From: {self.brevo_from_name} <{self.brevo_from_email}>")
                else:
                    print("⚠️ Brevo API key missing")
                    print(f"   API Key: {'Set' if brevo_api_key else 'Missing'}")
            except Exception as e:
                print(f"❌ Brevo initialization failed: {str(e)}")
                print("   This might be due to invalid credentials or network issues")
                self.brevo_service = None
        
        # Use enhanced production email service if available and in production
        if self.is_production and ENHANCED_EMAIL_AVAILABLE:
            print("🚀 Using enhanced production email service")
            self.production_service = EnhancedProductionEmailService()
        elif self.is_production and PRODUCTION_EMAIL_AVAILABLE:
            print("🚀 Using fallback production email service")
            self.production_service = ProductionEmailService()
        else:
            print("🔧 Using standard email service")
            self.production_service = None
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        print(f"📧 Email Service Initialized:")
        print(f"   Environment: {'Production' if self.is_production else 'Development'}")
        print(f"   SMTP Server: {self.smtp_server}:{self.smtp_port}")
        print(f"   SMTP Email: {self.smtp_email}")
        print(f"   SMTP Password: {'Set' if self.smtp_password else 'Missing'}")
        print(f"   Brevo Service: {'Enabled' if hasattr(self, 'brevo_service') and self.brevo_service else 'Disabled'}")
        print(f"   Production Service: {'Enabled' if self.production_service else 'Disabled'}")
        print(f"   Email Priority: {'Brevo' if hasattr(self, 'brevo_service') and self.brevo_service else 'Production' if self.production_service else 'SMTP'}")
        
        # Enhanced production debugging
        if self.is_production:
            print(f"🔍 Production Environment Debug:")
            print(f"   FLASK_ENV: {os.getenv('FLASK_ENV')}")
            print(f"   RENDER: {os.getenv('RENDER')}")
            print(f"   VERCEL: {os.getenv('VERCEL')}")
            print(f"   SMTP Config Complete: {bool(self.smtp_email and self.smtp_password)}")
            
            # Validate critical environment variables
            missing_vars = []
            if not self.smtp_email:
                missing_vars.append('SMTP_EMAIL')
            if not self.smtp_password:
                missing_vars.append('SMTP_PASSWORD')
            
            if missing_vars:
                print(f"⚠️ Missing Environment Variables: {', '.join(missing_vars)}")
                print(f"💡 Email functionality will be limited without these variables")
            else:
                print(f"✅ All required SMTP environment variables are set")
    
    def send_client_update_notification(self, client_data, admin_name, tmis_users, update_type="updated", loan_status=None):
        """
        Send email notification when admin updates a client
        
        Args:
            client_data: Dictionary containing client information
            admin_name: Name of the admin who made the changes
            tmis_users: List of users with tmis.* email addresses
            update_type: Type of update (updated, status_changed, etc.)
        """
        try:
            print("\n" + "="*80)
            print(f"🚀 EMAIL NOTIFICATION TRIGGERED")
            print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"👥 Admin: {admin_name}")
            print(f"📋 Update Type: {update_type}")
            print(f"🏢 Client: {client_data.get('legal_name', 'Unknown')}")
            if loan_status:
                print(f"💰 Loan Status: {loan_status}")
            print(f"🌍 Environment: {'Production' if self.is_production else 'Development'}")
            print("="*80)
            
            print(f"🔧 SMTP Configuration - Email: {self.smtp_email}, Server: {self.smtp_server}, Port: {self.smtp_port}")
            
            print(f"🔍 EMAIL SERVICE SELECTION:")
            print(f"   SMTP Available: {bool(self.smtp_email and self.smtp_password)}")
            print(f"   Production Service Available: {self.production_service is not None}")
            print(f"   Brevo Available: {hasattr(self, 'brevo_service') and self.brevo_service is not None}")
            
            # Priority 1: Use Brevo SMTP service first (most reliable with Brevo)
            if self.smtp_email and self.smtp_password and self.smtp_server == 'smtp-relay.brevo.com':
                print(f"🎆 USING: Brevo SMTP Service (Priority 1 - Most Reliable)")
                smtp_success = self._send_via_smtp(client_data, admin_name, tmis_users, update_type, loan_status)
                if smtp_success:
                    print("✅ Brevo SMTP email sent successfully")
                    return True
                else:
                    print("❌ Brevo SMTP failed, trying Brevo API fallback...")
            
            # Priority 2: Use Brevo API service as fallback
            elif hasattr(self, 'brevo_service') and self.brevo_service:
                print(f"🎆 USING: Brevo API Service (Priority 2 - Fallback)")
                brevo_success = self._send_via_brevo(client_data, admin_name, tmis_users, update_type, loan_status)
                if brevo_success:
                    print("✅ Brevo API email sent successfully")
                    return True
                else:
                    print("❌ Brevo API failed, trying production service...")
            
            # Priority 3: Use standard SMTP if not using Brevo SMTP
            elif self.smtp_email and self.smtp_password:
                print(f"🎆 USING: Standard SMTP Service (Priority 3)")
                smtp_success = self._send_via_smtp(client_data, admin_name, tmis_users, update_type, loan_status)
                if smtp_success:
                    print("✅ Standard SMTP email sent successfully")
                    return True
                else:
                    print("❌ Standard SMTP failed, trying production service...")
            
            # Priority 4: Use production email service
            elif self.production_service:
                print(f"🎆 USING: Production Email Service (Priority 4)")
                return self.production_service.send_client_update_notification(
                    client_data, admin_name, tmis_users, update_type, loan_status
                )
            
            # No email service available
            else:
                print(f"❌ NO EMAIL SERVICE AVAILABLE")
                return False
            
            # Fallback to standard email service
            print("📧 Using standard email service...")
            
            # Validate SMTP configuration
            if not self.smtp_email or not self.smtp_password:
                self.logger.error("SMTP email or password not configured")
                print("ERROR: SMTP email or password not configured")
                return False
            
            # Prepare recipients - Client emails + TMIS staff assigned to this client
            tmis_recipients = []
            client_recipients = []
            
            print(f"📧 Admin Action: Sending emails to client + assigned TMIS staff only")
            
            # Add TMIS users who are assigned to this client
            client_assigned_staff = client_data.get('assigned_staff', [])
            print(f"📄 Client assigned staff: {client_assigned_staff}")
            
            for user in tmis_users:
                if user.get('email') and user['email'].startswith('tmis.'):
                    # Check if this TMIS user is assigned to this client
                    user_email = user['email']
                    user_name = user.get('name', user_email.split('@')[0])
                    
                    # If client has assigned staff, only send to those staff members
                    if client_assigned_staff:
                        if (user_email in client_assigned_staff or 
                            user_name in client_assigned_staff or
                            any(staff in user_email for staff in client_assigned_staff)):
                            tmis_recipients.append({
                                'name': user.get('name', 'TMIS Staff'),
                                'email': user_email
                            })
                            print(f"📧 Added assigned TMIS staff: {user_email}")
                        else:
                            print(f"⚠️ Skipped non-assigned TMIS user: {user_email}")
                    else:
                        # No assigned staff specified - skip all TMIS users for this client
                        print(f"⚠️ No assigned staff for client - skipping TMIS user: {user_email}")
            
            # Add client emails if available
            if client_data.get('user_email'):
                client_recipients.append(client_data['user_email'])
                print(f"Added client user email: {client_data['user_email']}")
            
            if client_data.get('company_email') and client_data['company_email'] != client_data.get('user_email'):
                client_recipients.append(client_data['company_email'])
                print(f"Added client company email: {client_data['company_email']}")
            
            # Add any staff emails if they exist in client data
            if client_data.get('staff_emails'):
                for staff_email in client_data['staff_emails']:
                    if staff_email and staff_email not in client_recipients:
                        client_recipients.append(staff_email)
                        print(f"Added client staff email: {staff_email}")
            
            # Add email of the staff member who originally created/added this client
            creator_email = None
            if client_data.get('staff_email') and client_data['staff_email'] != 'Unknown':
                creator_email = client_data['staff_email']
            elif client_data.get('created_by'):
                # Try to get creator email from created_by field
                try:
                    from app import users_collection
                    from bson import ObjectId
                    
                    # Check if users_collection is available
                    if users_collection is not None:
                        creator = users_collection.find_one({'_id': ObjectId(client_data['created_by'])})
                        if creator and creator.get('email'):
                            creator_email = creator['email']
                            print(f"Found creator email from created_by lookup: {creator_email}")
                        else:
                            print(f"Creator not found or no email for created_by: {client_data.get('created_by')}")
                    else:
                        print("Warning: users_collection is None - database connection issue")
                except ImportError as ie:
                    print(f"Import error for users_collection: {str(ie)}")
                    print("Tip: Check if app.py is properly configured with database connection")
                except Exception as e:
                    print(f"Error looking up creator email: {str(e)}")
                    print(f"Error type: {type(e).__name__}")
            
            if creator_email and creator_email not in client_recipients:
                client_recipients.append(creator_email)
                print(f"Added client creator staff email: {creator_email}")
            
            print(f"📧 Total recipients: {len(client_recipients)} - {client_recipients}")
            
            success = True
            
            # Send emails to TMIS users with internal template
            if tmis_recipients:
                subject = f"Client {update_type.title()}: {client_data.get('legal_name', 'Unknown Client')}"
                html_body = self._create_tmis_email_template(client_data, admin_name, update_type)
                
                tmis_success = self._send_email(tmis_recipients, subject, html_body)
                if tmis_success:
                    print(f"SUCCESS: TMIS email sent to {len(tmis_recipients)} recipients")
                else:
                    print("ERROR: Failed to send TMIS email")
                    success = False
            
            # Send emails to client with client-friendly template
            if client_recipients:
                subject = f"Your Business Application Status Update"
                html_body = self._create_client_email_template(client_data, update_type)
                
                client_success = self._send_email(client_recipients, subject, html_body)
                if client_success:
                    print(f"SUCCESS: Client email sent to {len(client_recipients)} recipients")
                else:
                    print("ERROR: Failed to send client email")
                    success = False
            
            if not tmis_recipients and not client_recipients:
                self.logger.warning("No recipients found for client update notification")
                print("WARNING: No recipients found for email notification")
                return False
            
            if success:
                self.logger.info(f"Client update notifications sent successfully")
                print(f"SUCCESS: All email notifications sent successfully")
            else:
                self.logger.error("Some email notifications failed")
                print("ERROR: Some email notifications failed")
            
            return success
            
        except Exception as e:
            print("\n" + "!"*80)
            print(f"💥 CRITICAL ERROR IN EMAIL NOTIFICATION")
            print(f"🔴 Admin Action: {admin_name} - {update_type}")
            print(f"🔴 Client: {client_data.get('legal_name', 'Unknown')}")
            print(f"🔴 Error Type: {type(e).__name__}")
            print(f"🔴 Error Message: {str(e)}")
            print("!"*80 + "\n")
            
            self.logger.error(f"Error sending client update notification: {str(e)}")
            return False
    
    def _get_status_color(self, status):
        """Get color for status badge based on status value"""
        status_colors = {
            'interested': "#28a745",  # Green
            'not_interested': "#dc3545",  # Red
            'pending': "#6f42c1",  # Purple
            'hold': "#ffc107",  # Yellow
            'processing': "#17a2b8",  # Sky blue
        }
        
        return status_colors.get(status.lower(), "#6c757d")  # Default gray
    
    def _get_loan_status_color(self, loan_status):
        """Get color for loan status badge based on loan status value"""
        loan_status_colors = {
            'approved': "#28a745",  # Green
            'processing': "#17a2b8",  # Blue
            'hold': "#ffc107",  # Orange
            'rejected': "#dc3545",  # Red
            'soon': "#6c757d",  # Gray
        }
        
        return loan_status_colors.get(loan_status.lower(), "#6c757d")  # Default gray
    
    def _create_tmis_email_template(self, client_data, admin_name, update_type):
        """Create HTML email template for TMIS users"""
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ line-height: 1.6; color: #333; }}
                .client-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                .info-label {{ font-weight: bold; color: #555; }}
                .info-value {{ color: #333; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }}
                .status-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Client {update_type.title()} Notification</h1>
                    <p>TMIS Business Guru</p>
                </div>
                
                <div class="content">
                    <p>Dear Team,</p>
                    
                    <p>A client has been <strong>{update_type}</strong> by <strong>{admin_name}</strong> in the TMIS Business Guru system.</p>
                    
                    <div class="client-info">
                        <h3 style="margin-top: 0; color: #333;">📋 Client Details</h3>
                        
                        <div class="info-row">
                            <span class="info-label">Legal Name:</span>
                            <span class="info-value">{client_data.get('legal_name', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Trade Name:</span>
                            <span class="info-value">{client_data.get('trade_name', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Registration Number:</span>
                            <span class="info-value">{client_data.get('registration_number', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Constitution Type:</span>
                            <span class="info-value">{client_data.get('constitution_type', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Mobile Number:</span>
                            <span class="info-value">{client_data.get('mobile_number', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Status:</span>
                            <span class="status-badge" style="background-color: {self._get_status_color(client_data.get('status', ''))};">{client_data.get('status', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Loan Status:</span>
                            <span class="status-badge" style="background-color: {self._get_loan_status_color(client_data.get('loan_status', 'soon'))};">{client_data.get('loan_status', 'soon').title()}</span>
                        </div>
                        
                        {f'''<div class="info-row">
                            <span class="info-label">User Email:</span>
                            <span class="info-value">{client_data.get('user_email', 'N/A')}</span>
                        </div>''' if client_data.get('user_email') else ''}
                        
                        {f'''<div class="info-row">
                            <span class="info-label">Company Email:</span>
                            <span class="info-value">{client_data.get('company_email', 'N/A')}</span>
                        </div>''' if client_data.get('company_email') else ''}
                    </div>
                    
                    <p><strong>Updated by:</strong> {admin_name}</p>
                    <p><strong>Updated on:</strong> {current_time}</p>
                    
                    <p>Please log in to the TMIS Business Guru system to view complete client details and take necessary actions.</p>
                    
                    <p>Best regards,<br>
                    <strong>TMIS Business Guru System</strong></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from TMIS Business Guru system.</p>
                    <p>&copy; 2024 TMIS Business Guru. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _create_client_email_template(self, client_data, update_type):
        """Create HTML email template for client emails"""
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ line-height: 1.6; color: #333; }}
                .client-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                .info-label {{ font-weight: bold; color: #555; }}
                .info-value {{ color: #333; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }}
                .status-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Your Business Application Status Update</h1>
                </div>
                
                <div class="content">
                    <p>Dear Client,</p>
                    
                    <p>Your business application has been <strong>{update_type}</strong>.</p>
                    
                    <div class="client-info">
                        <h3 style="margin-top: 0; color: #333;">📋 Application Details</h3>
                        
                        <div class="info-row">
                            <span class="info-label">Legal Name:</span>
                            <span class="info-value">{client_data.get('legal_name', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Trade Name:</span>
                            <span class="info-value">{client_data.get('trade_name', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Registration Number:</span>
                            <span class="info-value">{client_data.get('registration_number', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Constitution Type:</span>
                            <span class="info-value">{client_data.get('constitution_type', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Mobile Number:</span>
                            <span class="info-value">{client_data.get('mobile_number', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Status:</span>
                            <span class="status-badge" style="background-color: {self._get_status_color(client_data.get('status', ''))};">{client_data.get('status', 'N/A')}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Loan Status:</span>
                            <span class="status-badge" style="background-color: {self._get_loan_status_color(client_data.get('loan_status', 'soon'))};">{client_data.get('loan_status', 'soon').title()}</span>
                        </div>
                        
                        {f'''<div class="info-row">
                            <span class="info-label">User Email:</span>
                            <span class="info-value">{client_data.get('user_email', 'N/A')}</span>
                        </div>''' if client_data.get('user_email') else ''}
                        
                        {f'''<div class="info-row">
                            <span class="info-label">Company Email:</span>
                            <span class="info-value">{client_data.get('company_email', 'N/A')}</span>
                        </div>''' if client_data.get('company_email') else ''}
                    </div>
                    
                    <p><strong>Updated on:</strong> {current_time}</p>
                    
                    <p>If you have any questions or concerns about your application, please reply to this email or contact our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>Business Application Team</strong></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from the Business Application system.</p>
                    <p>&#169; 2024 Business Application. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _send_email(self, recipients, subject, html_body):
        """Send email using SMTP configuration"""
        try:
            print(f"📧 Attempting to send email to: {recipients}")
            print(f"📧 SMTP Email: {self.smtp_email}")
            print(f"📧 SMTP Server: {self.smtp_server}:{self.smtp_port}")
            print(f"📧 Subject: {subject}")
            
            # Validate recipients
            if not recipients or not any(recipients):
                print("❌ No valid recipients provided")
                return False
            
            # Add plain text version for better deliverability
            import re
            text_body = re.sub('<[^<]+?>', '', html_body)
            text_body = re.sub(r'\s+', ' ', text_body).strip()
            
            # Production environment debugging
            if self.is_production:
                print(f"🔍 Production SMTP Debug:")
                print(f"   Server: {self.smtp_server}:{self.smtp_port}")
                print(f"   Email: {self.smtp_email}")
                print(f"   Password: {'Set' if self.smtp_password else 'Missing'}")
                print(f"   Recipients: {len(recipients)} - {recipients}")
                
                # Test basic network connectivity
                try:
                    import socket
                    print(f"   🔍 Testing network connectivity...")
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(10)
                    result = sock.connect_ex((self.smtp_server, self.smtp_port))
                    sock.close()
                    if result == 0:
                        print(f"   ✅ Network connectivity to {self.smtp_server}:{self.smtp_port} - OK")
                    else:
                        print(f"   ❌ Network connectivity to {self.smtp_server}:{self.smtp_port} - FAILED (Error code: {result})")
                        print(f"   💡 This suggests a firewall or network routing issue")
                except Exception as net_error:
                    print(f"   ⚠️ Network test failed: {str(net_error)}")
                    print(f"   💡 Network connectivity test error - this may indicate DNS or routing issues")
            
            # Helper function for timeout-wrapped SMTP operations
            def smtp_with_timeout(func, timeout_seconds=30):
                import threading
                import queue
                
                result_queue = queue.Queue()
                exception_queue = queue.Queue()
                
                def target():
                    try:
                        result = func()
                        result_queue.put(result)
                    except Exception as e:
                        exception_queue.put(e)
                
                thread = threading.Thread(target=target)
                thread.daemon = True
                thread.start()
                thread.join(timeout=timeout_seconds)
                
                if thread.is_alive():
                    print(f"❌ SMTP operation timed out after {timeout_seconds} seconds")
                    return None, TimeoutError(f"SMTP operation timed out after {timeout_seconds} seconds")
                
                if not exception_queue.empty():
                    return None, exception_queue.get()
                
                if not result_queue.empty():
                    return result_queue.get(), None
                
                return None, Exception("Unknown error in SMTP operation")
            
            # Connect to SMTP server and send email with timeout and retry logic
            max_retries = 3
            retry_delay = 2
            
            for attempt in range(max_retries):
                try:
                    print(f"📧 Connecting to SMTP server... (Attempt {attempt + 1}/{max_retries})")
                    print(f"📧 Connection timeout: 30 seconds")
                    
                    # Create SMTP connection with thread-based timeout
                    def create_connection():
                        return smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                    
                    import time
                    start_time = time.time()
                    server, conn_error = smtp_with_timeout(create_connection, 30)
                    
                    if conn_error:
                        raise conn_error
                    
                    connect_time = time.time() - start_time
                    print(f"📧 Initial connection took {connect_time:.2f} seconds")
                    
                    try:
                        server.set_debuglevel(1 if self.is_production else 0)  # Enable debug in production
                        print("📧 Starting TLS...")
                        
                        # Use starttls without timeout parameter for better compatibility
                        import socket
                        old_timeout = server.sock.gettimeout()
                        server.sock.settimeout(30)  # Set socket timeout manually
                        server.starttls()
                        server.sock.settimeout(old_timeout)  # Restore original timeout
                        
                        print("📧 TLS established, logging in...")
                        server.login(self.smtp_email, self.smtp_password)
                        print("📧 SMTP login successful, sending email...")
                        
                        # Connection successful, break out of retry loop
                        break
                        
                    except Exception as conn_error:
                        server.quit()
                        raise conn_error
                        
                except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, ConnectionError, TimeoutError, OSError) as e:
                    print(f"❌ SMTP connection failed (attempt {attempt + 1}): {str(e)}")
                    if attempt < max_retries - 1:
                        print(f"🔄 Retrying in {retry_delay} seconds...")
                        import time
                        time.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        print("❌ All SMTP connection attempts failed")
                        return False
                except Exception as e:
                    print(f"❌ Unexpected SMTP error: {str(e)}")
                    return False
            
            # If we get here, connection was successful
            try:
                
                # Send to each recipient individually to avoid multiple To headers
                failed_recipients = []
                successful_recipients = []
                
                for recipient in recipients:
                    if recipient and recipient.strip():
                        try:
                            # Create individual message for each recipient to avoid RFC 5322 issues
                            individual_msg = MIMEMultipart('alternative')
                            individual_msg['From'] = f"TMIS Business Guru <{self.smtp_email}>"
                            individual_msg['To'] = recipient  # Single recipient per message
                            individual_msg['Subject'] = subject
                            individual_msg['Reply-To'] = self.smtp_email
                            
                            # Add plain text version
                            text_part = MIMEText(text_body, 'plain')
                            individual_msg.attach(text_part)
                            
                            # Add HTML content
                            html_part = MIMEText(html_body, 'html')
                            individual_msg.attach(html_part)
                            
                            # Send individual message
                            server.send_message(individual_msg)
                            successful_recipients.append(recipient)
                            print(f"✅ Email sent successfully to: {recipient}")
                        except Exception as send_error:
                            failed_recipients.append(recipient)
                            print(f"❌ Failed to send to {recipient}: {str(send_error)}")
                            print(f"� Send error type: {type(send_error).__name__}")
                
                print(f"📊 Email Summary:")
                print(f"   ✅ Successful: {len(successful_recipients)} - {successful_recipients}")
                print(f"   ❌ Failed: {len(failed_recipients)} - {failed_recipients}")
                
                # Return True if at least one email was sent successfully
                return len(successful_recipients) > 0
                
            except Exception as email_error:
                print(f"❌ Error during email sending: {str(email_error)}")
                try:
                    server.quit()
                except:
                    pass
                return False
            
        except smtplib.SMTPAuthenticationError as auth_error:
            error_msg = f"SMTP Authentication failed: {str(auth_error)}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("💡 Check SMTP credentials and app-specific password")
            return False
        except smtplib.SMTPRecipientsRefused as recip_error:
            error_msg = f"SMTP Recipients refused: {str(recip_error)}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("💡 Check recipient email addresses")
            return False
        except smtplib.SMTPServerDisconnected as disc_error:
            error_msg = f"SMTP Server disconnected: {str(disc_error)}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            print("💡 Check network connection and SMTP server status")
            return False
        except Exception as e:
            error_msg = f"SMTP Error: {str(e)}"
            self.logger.error(error_msg)
            print(f"❌ {error_msg}")
            print(f"💡 Error type: {type(e).__name__}")
            import traceback
            print(f"📋 Traceback: {traceback.format_exc()}")
            return False
    
    def _send_via_smtp(self, client_data, admin_name, tmis_users, update_type, loan_status=None):
        """
        Send email notification using SMTP
        """
        try:
            print(f"🚀 SMTP: Starting email process...")
            
            # Validate SMTP configuration
            if not self.smtp_email or not self.smtp_password:
                print("❌ SMTP email or password not configured")
                return False
            
            print(f"📧 SMTP: From {self.smtp_email} via {self.smtp_server}:{self.smtp_port}")
            
            # Prepare recipients - Client emails + TMIS staff assigned to this client
            tmis_recipients = []
            client_recipients = []
            
            print(f"📧 Admin Action: SMTP sending emails to client + assigned TMIS staff only")
            
            # Add TMIS users who are assigned to this client
            client_assigned_staff = client_data.get('assigned_staff', [])
            print(f"📄 Client assigned staff: {client_assigned_staff}")
            
            for user in tmis_users:
                if user.get('email') and user['email'].startswith('tmis.'):
                    # Check if this TMIS user is assigned to this client
                    user_email = user['email']
                    user_name = user.get('name', user_email.split('@')[0])
                    
                    # Only send to TMIS users who are assigned to this specific client
                    if client_assigned_staff:
                        if (user_email in client_assigned_staff or 
                            user_name in client_assigned_staff or
                            any(staff in user_email for staff in client_assigned_staff)):
                            tmis_recipients.append(user_email)
                            print(f"📧 Added assigned TMIS staff: {user_email}")
                        else:
                            print(f"⚠️ Skipped non-assigned TMIS user: {user_email}")
                    else:
                        # No assigned staff specified - skip all TMIS users for this client
                        print(f"⚠️ No assigned staff for client - skipping TMIS user: {user_email}")
            
            # Add client emails
            if client_data.get('user_email'):
                client_recipients.append(client_data['user_email'])
                print(f"📧 Added client user email: {client_data['user_email']}")
            
            if client_data.get('company_email') and client_data['company_email'] != client_data.get('user_email'):
                client_recipients.append(client_data['company_email'])
                print(f"📧 Added client company email: {client_data['company_email']}")
            
            # Add any staff emails if they exist in client data
            if client_data.get('staff_emails'):
                for staff_email in client_data['staff_emails']:
                    if staff_email and staff_email not in client_recipients:
                        client_recipients.append(staff_email)
                        print(f"📧 Added client staff email: {staff_email}")
            
            # Add email of the staff member who originally created/added this client
            creator_email = None
            if client_data.get('staff_email') and client_data['staff_email'] != 'Unknown':
                creator_email = client_data['staff_email']
            elif client_data.get('created_by'):
                # Try to get creator email from created_by field
                try:
                    from app import users_collection
                    from bson import ObjectId
                    
                    # Check if users_collection is available
                    if users_collection is not None:
                        creator = users_collection.find_one({'_id': ObjectId(client_data['created_by'])})
                        if creator and creator.get('email'):
                            creator_email = creator['email']
                            print(f"📧 Found creator email from created_by lookup: {creator_email}")
                        else:
                            print(f"📧 Creator not found or no email for created_by: {client_data.get('created_by')}")
                    else:
                        print("📧 Warning: users_collection is None - database connection issue")
                except ImportError as ie:
                    print(f"📧 Import error for users_collection: {str(ie)}")
                    print("📧 Tip: Check if app.py is properly configured with database connection")
                except Exception as e:
                    print(f"📧 Error looking up creator email: {str(e)}")
                    print(f"📧 Error type: {type(e).__name__}")
            
            if creator_email and creator_email not in client_recipients:
                client_recipients.append(creator_email)
                print(f"📧 Added client creator staff email: {creator_email}")
            
            if not tmis_recipients and not client_recipients:
                print("⚠️ No recipients found for SMTP email")
                return False
            
            success = True
            
            # Send to TMIS users (assigned staff only)
            if tmis_recipients:
                subject = f"Client {update_type.title()}: {client_data.get('legal_name', 'Unknown Client')}"
                html_body = self._create_tmis_email_template(client_data, admin_name, update_type)
                
                print(f"📤 SMTP: Sending TMIS email to {len(tmis_recipients)} assigned staff...")
                tmis_success = self._send_email(tmis_recipients, subject, html_body)
                if tmis_success:
                    print(f"✅ TMIS email sent via SMTP to {len(tmis_recipients)} assigned staff")
                else:
                    print("❌ Failed to send TMIS email via SMTP")
                    success = False
            
            # Send to client
            if client_recipients:
                if loan_status:
                    subject = f"Your Loan Status Update - TMIS Business Guru"
                    html_body = self._create_loan_status_client_email_template(client_data, loan_status, admin_name)
                else:
                    subject = "Your Business Application Status Update"
                    html_body = self._create_client_email_template(client_data, update_type)
                
                print(f"📤 SMTP: Sending client email to {len(client_recipients)} recipients...")
                client_success = self._send_email(client_recipients, subject, html_body)
                if client_success:
                    print(f"✅ Client email sent via SMTP to {len(client_recipients)} recipients")
                else:
                    print("❌ Failed to send client email via SMTP")
                    success = False
            
            print(f"🏁 SMTP: Overall success = {success}")
            return success
            
        except Exception as e:
            print(f"💥 SMTP email error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    def _send_via_brevo(self, client_data, admin_name, tmis_users, update_type, loan_status=None):
        """
        Send email notification using Brevo API
        """
        try:
            import re
            
            print(f"🚀 Brevo: Starting email process...")
            
            # Validate Brevo service
            if not self.brevo_service:
                print("❌ Brevo service not initialized")
                return False
            
            # Validate Brevo configuration
            if not hasattr(self, 'brevo_from_email') or not self.brevo_from_email:
                print("❌ Brevo from_email not configured")
                return False
            
            print(f"📧 Brevo: From {self.brevo_from_name} <{self.brevo_from_email}>")
            
            # Prepare recipients - Client emails + TMIS staff assigned to this client
            tmis_recipients = []
            client_recipients = []
            
            print(f"📧 Admin Action: Brevo sending emails to client + assigned TMIS staff only")
            
            # Add TMIS users who are assigned to this client
            client_assigned_staff = client_data.get('assigned_staff', [])
            print(f"📄 Client assigned staff: {client_assigned_staff}")
            
            for user in tmis_users:
                if user.get('email') and user['email'].startswith('tmis.'):
                    # Check if this TMIS user is assigned to this client
                    user_email = user['email']
                    user_name = user.get('name', user_email.split('@')[0])
                    
                    # If client has assigned staff, only send to those staff members
                    if client_assigned_staff:
                        if (user_email in client_assigned_staff or 
                            user_name in client_assigned_staff or
                            any(staff in user_email for staff in client_assigned_staff)):
                            tmis_recipients.append({
                                'name': user.get('name', 'TMIS Staff'),
                                'email': user_email
                            })
                            print(f"📧 Added assigned TMIS staff: {user_email}")
                        else:
                            print(f"⚠️ Skipped non-assigned TMIS user: {user_email}")
                    else:
                        # If no assigned staff specified, send to all TMIS users (fallback)
                        tmis_recipients.append({
                            'name': user.get('name', 'TMIS Staff'),
                            'email': user_email
                        })
                        print(f"📧 Added TMIS user (no assignment filter): {user_email}")
            
            # Add client emails
            if client_data.get('user_email'):
                client_recipients.append({
                    'name': client_data.get('legal_name', 'Client'),
                    'email': client_data['user_email']
                })
                print(f"📧 Added client user email: {client_data['user_email']}")
            
            if client_data.get('company_email') and client_data['company_email'] != client_data.get('user_email'):
                client_recipients.append({
                    'name': client_data.get('legal_name', 'Client'),
                    'email': client_data['company_email']
                })
                print(f"📧 Added client company email: {client_data['company_email']}")
            
            # Add any staff emails if they exist in client data
            if client_data.get('staff_emails'):
                for staff_email in client_data['staff_emails']:
                    if staff_email and not any(r['email'] == staff_email for r in client_recipients):
                        client_recipients.append({
                            'name': client_data.get('legal_name', 'Client Staff'),
                            'email': staff_email
                        })
                        print(f"📧 Added client staff email: {staff_email}")
            
            # Add email of the staff member who originally created/added this client
            creator_email = None
            creator_name = client_data.get('created_by_name', 'Creator Staff')
            if client_data.get('staff_email') and client_data['staff_email'] != 'Unknown':
                creator_email = client_data['staff_email']
            elif client_data.get('created_by'):
                # Try to get creator email from created_by field
                try:
                    from app import users_collection
                    from bson import ObjectId
                    
                    # Check if users_collection is available
                    if users_collection is not None:
                        creator = users_collection.find_one({'_id': ObjectId(client_data['created_by'])})
                        if creator and creator.get('email'):
                            creator_email = creator['email']
                            creator_name = creator.get('username', creator_name)
                            print(f"📧 Found creator email from created_by lookup: {creator_email}")
                        else:
                            print(f"📧 Creator not found or no email for created_by: {client_data.get('created_by')}")
                    else:
                        print("📧 Warning: users_collection is None - database connection issue")
                except ImportError as ie:
                    print(f"📧 Import error for users_collection: {str(ie)}")
                    print("📧 Tip: Check if app.py is properly configured with database connection")
                except Exception as e:
                    print(f"📧 Error looking up creator email: {str(e)}")
                    print(f"📧 Error type: {type(e).__name__}")
            
            if creator_email and not any(r['email'] == creator_email for r in client_recipients):
                client_recipients.append({
                    'name': creator_name,
                    'email': creator_email
                })
                print(f"📧 Added client creator staff email: {creator_email}")
            
            if not tmis_recipients and not client_recipients:
                print("⚠️ No recipients found for Brevo email")
                return False
            
            success = True
            
            # Send to TMIS users (assigned staff only)
            if tmis_recipients:
                subject = f"Client {update_type.title()}: {client_data.get('legal_name', 'Unknown Client')}"
                html_body = self._create_tmis_email_template(client_data, admin_name, update_type)
                
                print(f"📤 Brevo: Sending TMIS email to {len(tmis_recipients)} assigned staff...")
                tmis_success = self._send_brevo_email(tmis_recipients, subject, html_body)
                if tmis_success:
                    print(f"✅ TMIS email sent via Brevo to {len(tmis_recipients)} assigned staff")
                else:
                    print("❌ Failed to send TMIS email via Brevo")
                    success = False
            
            # Send to client
            if client_recipients:
                if loan_status:
                    subject = f"Your Loan Status Update - TMIS Business Guru"
                    html_body = self._create_loan_status_client_email_template(client_data, loan_status, admin_name)
                else:
                    subject = "Your Business Application Status Update"
                    html_body = self._create_client_email_template(client_data, update_type)
                
                print(f"📤 Brevo: Sending client email to {len(client_recipients)} recipients...")
                client_success = self._send_brevo_email(client_recipients, subject, html_body)
                if client_success:
                    print(f"✅ Client email sent via Brevo to {len(client_recipients)} recipients")
                else:
                    print("❌ Failed to send client email via Brevo")
                    success = False
            
            print(f"🏁 Brevo: Overall success = {success}")
            return success
            
        except Exception as e:
            print(f"💥 Brevo email error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            return False
    
    def _send_brevo_email(self, recipients, subject, html_body):
        """
        Send email using Brevo API
        """
        try:
            import re
            
            print(f"📤 Brevo API: Preparing email data...")
            
            # Validate inputs
            if not recipients:
                print("❌ No recipients provided")
                return False
            
            if not subject:
                print("❌ No subject provided")
                return False
            
            if not html_body:
                print("❌ No email body provided")
                return False
            
            # Convert HTML to plain text
            text_body = re.sub('<[^<]+?>', '', html_body)
            text_body = re.sub(r'\s+', ' ', text_body).strip()
            
            # Format recipients properly for Brevo API
            # Brevo expects recipients in a specific format
            formatted_recipients = []
            for recipient in recipients:
                if isinstance(recipient, dict):
                    # If recipient is already a dict with name and email
                    formatted_recipients.append(sib_api_v3_sdk.SendSmtpEmailTo(
                        email=recipient['email'], 
                        name=recipient.get('name', recipient['email'].split('@')[0])
                    ))
                elif isinstance(recipient, str):
                    # If recipient is just an email string
                    formatted_recipients.append(sib_api_v3_sdk.SendSmtpEmailTo(
                        email=recipient, 
                        name=recipient.split('@')[0]
                    ))
            
            # Validate from email
            if not self.brevo_from_email:
                print("❌ Brevo from_email not configured")
                return False
            
            # Create Brevo email object
            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=formatted_recipients,
                subject=subject,
                html_content=html_body,
                text_content=text_body,
                sender=sib_api_v3_sdk.SendSmtpEmailSender(
                    name=self.brevo_from_name or 'TMIS Business Guru',
                    email=self.brevo_from_email
                )
            )
            
            print(f"📧 Brevo Recipients: {len(formatted_recipients)} recipients")
            
            print(f"📤 Brevo API: Sending to {len(recipients)} recipients")
            print(f"📧 Subject: {subject}")
            print(f"📧 From: {self.brevo_from_name} <{self.brevo_from_email}>")
            
            # Attempt to send via Brevo
            print("🚀 Calling Brevo API...")
            result = self.brevo_service.send_transac_email(send_smtp_email)
            
            print(f"📝 Brevo API Response: {result}")
            
            # Check for successful response
            if result:
                # Brevo API returns a message_id on success
                if hasattr(result, 'message_id') and result.message_id:
                    print(f"✅ Brevo email sent successfully! Message ID: {result.message_id}")
                    return True
                else:
                    print(f"❌ Brevo email failed")
                    print(f"   Full response: {result}")
                    return False
            else:
                print(f"❌ Brevo API returned no response")
                return False
                
        except ApiException as e:
            print(f"💥 Brevo API error: {str(e)}")
            print(f"   Status code: {e.status}")
            print(f"   Reason: {e.reason}")
            print(f"   Body: {e.body}")
            return False
        except Exception as e:
            print(f"💥 Brevo API error: {str(e)}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            return False
    
    def _create_loan_status_client_email_template(self, client_data, loan_status, admin_name):
        """
        Create HTML email template for loan status updates to clients
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        client_name = client_data.get('legal_name') or client_data.get('trade_name') or "Client"
        
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .content {{ line-height: 1.6; color: #333; }}
                .client-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .info-row {{ display: flex; justify-content: space-between; margin: 10px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                .info-label {{ font-weight: bold; color: #555; }}
                .info-value {{ color: #333; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; color: #666; font-size: 12px; }}
                .status-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: bold; color: white; }}
                .loan-status-highlight {{ background-color: #e7f3ff; border: 1px solid #b3d9ff; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Your Loan Status Update</h1>
                </div>
                
                <div class="content">
                    <p>Dear <strong>{client_name}</strong>,</p>
                    
                    <div class="loan-status-highlight">
                        <h3 style="margin: 0; color: #333;">Your loan status is <strong style="color: {self._get_loan_status_color(loan_status)};">{loan_status.upper()}</strong> by admin in TMIS Business Guru</h3>
                    </div>
                    
                    <p><strong>Updated on:</strong> {current_time}</p>
                    
                    <p>If you have any questions or concerns about your loan status, please reply to this email or contact our support team.</p>
                    
                    <p>Best regards,<br>
                    <strong>TMIS Business Guru Team</strong></p>
                </div>
                
                <div class="footer">
                    <p>This is an automated notification from TMIS Business Guru system.</p>
                    <p>&copy; 2024 TMIS Business Guru. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template

# Create global email service instance
email_service = EmailService()
