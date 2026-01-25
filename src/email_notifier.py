import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Dict
import os
from dotenv import load_dotenv

load_dotenv()

class EmailNotifier:
    """Send email notifications when sensitive content is blocked."""
    
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM_EMAIL')
        
        if not all([self.smtp_username, self.smtp_password, self.from_email]):
            print("⚠️  Email not configured. Set credentials in .env file")
    
    def send_blocked_content_alert(
    self,
    user_email: str,
    boss_email: str,
    username: str,
    analysis_result: Dict,
    text_preview: str,
    platform: str = "Unknown Platform"  # NEW: Add platform
    ) -> bool:
        """
        Send email to boss when user tries to send sensitive content.
        """
        if not all([self.smtp_username, self.smtp_password]):
            print("❌ Email not configured, skipping notification")
            return False
        
        # Get detection types for summary (no actual values)
        detection_types = []
        if analysis_result['regex_detections']:
            detection_types = [d['type'].replace('_', ' ').title() for d in analysis_result['regex_detections']]
        
        subject = f"RedactAI Security Alert: {username} attempted to send sensitive data"
        
        # Create email body
        body = f"""
    RedactAI Security Alert
    {'=' * 70}

    INCIDENT DETAILS:
    - User: {username}
    - User Email: {user_email}
    - Timestamp: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S %Z')}
    - Platform: {platform}

    RISK ASSESSMENT:
    - Decision: {analysis_result['decision']}
    - Risk Score: {analysis_result['overall_risk_score']}/100
    - AI Category: {analysis_result['ai_category']}
    - AI Confidence: {analysis_result['ai_confidence']:.1%}

    WHAT WAS DETECTED:
    - Number of Detections: {len(analysis_result['regex_detections'])}
    - Types of Sensitive Data: {', '.join(set(detection_types)) if detection_types else 'AI flagged as sensitive'}

    EXPLANATION:
    {analysis_result['explanation']}

    ACTION TAKEN:
    The user was warned but chose to proceed. This content has been logged 
    for your review.

    NEXT STEPS:
    1. Review the incident details above
    2. Contact {username} if needed to discuss data handling policies

    ---
    RedactAI - Local AI Security System
    Protecting your organization's sensitive data
        """
        
        try:
            # Create message
            message = MIMEMultipart()
            message['From'] = self.from_email
            message['To'] = boss_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Email notification sent to {boss_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            print(f"Error details: {str(e)}")
            import traceback
            traceback.print_exc()
            return False