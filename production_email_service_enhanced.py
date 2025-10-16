#!/usr/bin/env python3
"""
Enhanced Production Email Service for TMIS Business Guru
Fixes email sending issues in production environment (Render + Vercel)
Matches the email templates shown in user screenshots
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict, Any, Optional
import traceback

# Configure logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedProductionEmailService:
    """
    Enhanced email service specifically designed for production environments
    Handles Render backend + Vercel frontend deployment with robust error handling
    """
    
    def __init__(self):
        """Initialize email service with production-ready configuration"""
        self.smtp_email = os.getenv('SMTP_EMAIL')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        
        # Production environment detection
        self.is_production = (
            os.getenv('FLASK_ENV') == 'production' or 
            os.getenv('RENDER') == 'true' or
            os.getenv('VERCEL') == '1'
        )
        
        # Enhanced logging for production debugging
        logger.info(f"=== ENHANCED EMAIL SERVICE INITIALIZATION ===")
        logger.info(f"Environment: {'Production' if self.is_production else 'Development'}")
        logger.info(f"SMTP Server: {self.smtp_server}:{self.smtp_port}")
        logger.info(f"SMTP Email: {self.smtp_email}")
        logger.info(f"SMTP Password: {'Set' if self.smtp_password else 'Missing'}")
        
        # Validate configuration
        self.config_valid = self._validate_configuration()
        
        if self.config_valid:
            logger.info("✅ Enhanced email service initialized successfully")
        else:
            logger.error("❌ Enhanced email service initialization failed")
    
    def _validate_configuration(self) -> bool:
        """Validate SMTP configuration and log detailed errors"""
        missing_vars = []
        
        if not self.smtp_email:
            missing_vars.append('SMTP_EMAIL')
        if not self.smtp_password:
            missing_vars.append('SMTP_PASSWORD')
        if not self.smtp_server:
            missing_vars.append('SMTP_SERVER')
        if not self.smtp_port:
            missing_vars.append('SMTP_PORT')
        
        if missing_vars:
            logger.error(f"❌ Missing SMTP environment variables: {', '.join(missing_vars)}")
            logger.error("🔧 Required environment variables for Render:")
            logger.error("   - SMTP_EMAIL: Your Gmail address")
            logger.error("   - SMTP_PASSWORD: Your Gmail App Password (16 characters)")
            logger.error("   - SMTP_SERVER: smtp.gmail.com (default)")
            logger.error("   - SMTP_PORT: 587 (default)")
            logger.error("📋 Set these in your Render dashboard under Environment Variables")
            return False
        
        logger.info("✅ SMTP configuration validation passed")
        return True
    
    def send_client_update_notification(
        self, 
        client_data: Dict[str, Any], 
        admin_name: str, 
        tmis_users: List[Dict[str, Any]], 
        update_type: str = "updated",
        loan_status: str = None
    ) -> bool:
        """
        Send email notification when admin updates a client
        Enhanced for production reliability with detailed logging
        """
        try:
            logger.info(f"🚀 Starting enhanced email notification process...")
            logger.info(f"Update type: {update_type}")
            logger.info(f"Admin: {admin_name}")
            logger.info(f"TMIS users count: {len(tmis_users)}")
            logger.info(f"Client: {client_data.get('legal_name', 'Unknown')}")
            
            # Validate configuration before sending
            if not self.config_valid:
                logger.error("❌ Email configuration invalid - aborting notification")
                return False
            
            # Prepare email recipients
            tmis_recipients = []
            client_recipients = []
            
            # Add TMIS users (users with tmis.* emails)
            for user in tmis_users:
                user_email = user.get('email', '')
                if user_email and user_email.lower().startswith('tmis.'):
                    tmis_recipients.append(user_email)
                    logger.info(f"📧 Added TMIS recipient: {user_email}")
            
            # Add client emails
            if client_data.get('user_email'):
                client_recipients.append(client_data['user_email'])
                logger.info(f"📧 Added client user email: {client_data['user_email']}")
            
            if client_data.get('company_email') and client_data['company_email'] != client_data.get('user_email'):
                client_recipients.append(client_data['company_email'])
                logger.info(f"📧 Added client company email: {client_data['company_email']}")
            
            logger.info(f"📊 Email summary: {len(tmis_recipients)} TMIS, {len(client_recipients)} client recipients")
            
            success = True
            
            # Send emails to TMIS users (internal notification)
            if tmis_recipients:
                subject = f"Client Status Updated: {client_data.get('legal_name', 'Unknown Client')}"
                html_body = self._create_tmis_email_template(client_data, admin_name, update_type)
                
                tmis_success = self._send_email_with_retry(tmis_recipients, subject, html_body)
                if tmis_success:
                    logger.info(f"✅ TMIS email sent to {len(tmis_recipients)} recipients")
                else:
                    logger.error("❌ Failed to send TMIS email")
                    success = False
            
            # Send emails to client (customer-friendly notification)
            if client_recipients:
                # Check if this is a loan status update
                if loan_status:
                    subject = f"Your Loan Status Update - TMIS Business Guru"
                    html_body = self._create_loan_status_client_email_template(client_data, loan_status, admin_name)
                else:
                    subject = f"Your Business Application Status Update"
                    html_body = self._create_client_email_template(client_data, update_type)
                
                client_success = self._send_email_with_retry(client_recipients, subject, html_body)
                if client_success:
                    logger.info(f"✅ Client email sent to {len(client_recipients)} recipients")
                else:
                    logger.error("❌ Failed to send client email")
                    success = False
            
            if not tmis_recipients and not client_recipients:
                logger.warning("⚠️ No recipients found for email notification")
                return False
            
            if success:
                logger.info(f"🎉 All email notifications sent successfully")
            else:
                logger.error("❌ Some email notifications failed")
            
            return success
            
        except Exception as e:
            logger.error(f"💥 Exception in email notification: {str(e)}")
            logger.error(f"💥 Full traceback: {traceback.format_exc()}")
            return False
    
    def _send_email_with_retry(self, recipients: List[str], subject: str, html_body: str, max_retries: int = 3) -> bool:
        """
        Production-optimized email sending with retry logic and enhanced error handling
        """
        for attempt in range(max_retries):
            try:
                logger.info(f"📤 Attempt {attempt + 1}/{max_retries} - Sending email to: {recipients}")
                logger.info(f"📧 Subject: {subject}")
                
                # Create message
                msg = MIMEMultipart('alternative')
                msg['From'] = self.smtp_email
                msg['To'] = ', '.join(recipients)
                msg['Subject'] = subject
                
                # Add HTML content
                html_part = MIMEText(html_body, 'html', 'utf-8')
                msg.attach(html_part)
                
                # Production-specific SMTP connection with enhanced error handling
                logger.info(f"🔌 Connecting to SMTP server: {self.smtp_server}:{self.smtp_port}")
                
                # Use timeout for production reliability
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=60) as server:
                    logger.info("🔐 Starting TLS encryption...")
                    server.starttls()
                    
                    logger.info("🔑 Authenticating with SMTP server...")
                    server.login(self.smtp_email, self.smtp_password)
                    
                    logger.info("📨 Sending email message...")
                    server.send_message(msg)
                    
                    logger.info(f"✅ Email sent successfully to {len(recipients)} recipients on attempt {attempt + 1}")
                
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"🔐 SMTP Authentication failed on attempt {attempt + 1}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error("💡 Check your Gmail App Password in Render environment variables")
                    logger.error("💡 Ensure 2FA is enabled and App Password is 16 characters")
                return False
            except smtplib.SMTPRecipientsRefused as e:
                logger.error(f"📧 Recipients refused on attempt {attempt + 1}: {str(e)}")
                return False
            except smtplib.SMTPServerDisconnected as e:
                logger.error(f"🔌 SMTP server disconnected on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
                continue
            except smtplib.SMTPException as e:
                logger.error(f"📧 SMTP error on attempt {attempt + 1}: {str(e)}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
                continue
            except Exception as e:
                logger.error(f"💥 Unexpected error on attempt {attempt + 1}: {str(e)}")
                logger.error(f"💥 Full traceback: {traceback.format_exc()}")
                if attempt < max_retries - 1:
                    logger.info(f"🔄 Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
                continue
        
        logger.error(f"❌ Failed to send email after {max_retries} attempts")
        return False
    
    def _get_status_color(self, status: str) -> str:
        """Get color for status badge"""
        status_colors = {
            'interested': "#28a745",      # Green
            'not_interested': "#dc3545",  # Red
            'pending': "#6f42c1",         # Purple
            'hold': "#ffc107",            # Yellow/Orange
            'processing': "#17a2b8",      # Blue
        }
        return status_colors.get(status.lower(), "#6c757d")  # Default gray
    
    def _get_loan_status_color(self, loan_status: str) -> str:
        """Get color for loan status badge"""
        loan_status_colors = {
            'approved': "#28a745",    # Green
            'processing': "#17a2b8",  # Blue
            'hold': "#ffc107",        # Orange
            'rejected': "#dc3545",    # Red
            'soon': "#6c757d",        # Gray
        }
        return loan_status_colors.get(loan_status.lower(), "#6c757d")  # Default gray
    
    def _create_tmis_email_template(self, client_data: Dict[str, Any], admin_name: str, update_type: str) -> str:
        """Create HTML email template for TMIS users (matches screenshot format)"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
                .production-notice {{ background-color: #e7f3ff; border: 1px solid #b3d9ff; padding: 10px; border-radius: 5px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔔 Client Status Updated Notification</h1>
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
                            <span class="status-badge" style="background-color: {self._get_status_color(client_data.get('status', ''))};">{client_data.get('status', 'N/A').title()}</span>
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
                    <strong>Business Application Team</strong></p>
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
    
    def _create_client_email_template(self, client_data: Dict[str, Any], update_type: str) -> str:
        """Create HTML email template for client emails (matches screenshot format)"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
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
                            <span class="status-badge" style="background-color: {self._get_status_color(client_data.get('status', ''))};">{client_data.get('status', 'N/A').title()}</span>
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
                    <p>&copy; 2024 Business Application. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html_template
    
    def _create_loan_status_client_email_template(self, client_data: Dict[str, Any], loan_status: str, admin_name: str) -> str:
        """Create HTML email template for loan status updates to clients"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get client name - prefer legal_name, fallback to trade_name or "Client"
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
                            <span class="status-badge" style="background-color: {self._get_status_color(client_data.get('status', ''))};">{client_data.get('status', 'N/A').title()}</span>
                        </div>
                        
                        <div class="info-row">
                            <span class="info-label">Loan Status:</span>
                            <span class="status-badge" style="background-color: {self._get_loan_status_color(loan_status)};">{loan_status.title()}</span>
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
    
    def test_email_configuration(self, test_email: Optional[str] = None) -> bool:
        """
        Test email configuration in production environment
        """
        try:
            logger.info("🧪 Testing enhanced email configuration...")
            
            if not self.config_valid:
                return False
            
            # Test SMTP connection
            logger.info("🔌 Testing SMTP connection...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=60) as server:
                server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                logger.info("✅ SMTP connection test successful")
            
            # Send test email if recipient provided
            if test_email:
                logger.info(f"📧 Sending test email to: {test_email}")
                subject = "TMIS Business Guru - Enhanced Production Email Test"
                body = f"""
                <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; margin-bottom: 30px;">
                            <h1 style="margin: 0; font-size: 24px;">✅ Production Email Test Successful</h1>
                        </div>
                        <div style="line-height: 1.6; color: #333;">
                            <p>This email confirms that the TMIS Business Guru enhanced production email system is working correctly.</p>
                            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                                <h3 style="margin-top: 0; color: #333;">📋 Test Details</h3>
                                <p><strong>Environment:</strong> Production</p>
                                <p><strong>SMTP Server:</strong> {self.smtp_server}</p>
                                <p><strong>From Email:</strong> {self.smtp_email}</p>
                                <p><strong>Test Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                            </div>
                            <p>Email notifications for client updates should now work properly in production.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                success = self._send_email_with_retry([test_email], subject, body)
                if success:
                    logger.info("✅ Test email sent successfully")
                    return True
                else:
                    logger.error("❌ Test email failed")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Email configuration test failed: {str(e)}")
            logger.error(f"💥 Full traceback: {traceback.format_exc()}")
            return False

# Create global enhanced production email service instance
enhanced_email_service = EnhancedProductionEmailService()

# Export for backward compatibility
email_service = enhanced_email_service
