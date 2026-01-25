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
        text_preview: str
    ) -> bool:
        """
        Send email to boss when user tries to send blocked content.
        """
        if not all([self.smtp_username, self.smtp_password]):
            print("❌ Email not configured, skipping notification")
            return False
        
        subject = f"🚨 RedactAI Alert: {username} attempted to send sensitive data"
        
        # Create email body
        body = f"""
RedactAI Security Alert
{'=' * 60}

User: {username} ({user_email})
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Decision: {analysis_result['decision']}
Risk Score: {analysis_result['overall_risk_score']}/100

AI Classification:
- Category: {analysis_result['ai_category']}
- Confidence: {analysis_result['ai_confidence']:.1%}

Detections Found:
- Regex Detections: {len(analysis_result['regex_detections'])}
- Detection Types: {', '.join(set(d['type'] for d in analysis_result['regex_detections'])) if analysis_result['regex_detections'] else 'None'}

Explanation:
{analysis_result['explanation']}

Text Preview (first 200 characters):
{'-' * 60}
{text_preview}
{'-' * 60}

This content was flagged as {analysis_result['decision']} and the user was notified.

---
RedactAI - Local AI Gatekeeper
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
            return False
    
    def send_user_confirmation(
        self,
        user_email: str,
        username: str,
        analysis_result: Dict,
        text_preview: str,
        boss_notified: bool
    ) -> bool:
        """
        Send confirmation email to user about what was detected.
        """
        if not all([self.smtp_username, self.smtp_password]):
            return False
        
        subject = f"RedactAI: Your content analysis for {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
Hello {username},

RedactAI detected potentially sensitive content in your recent input.

Decision: {analysis_result['decision']}
Risk Score: {analysis_result['overall_risk_score']}/100
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{analysis_result['explanation']}

Text Preview:
{'-' * 60}
{text_preview}
{'-' * 60}

{"⚠️  Your administrator has been notified of this attempt." if boss_notified else ""}

For your reference, this analysis has been logged.

Best regards,
RedactAI Security System
        """
        
        try:
            message = MIMEMultipart()
            message['From'] = self.from_email
            message['To'] = user_email
            message['Subject'] = subject
            message.attach(MIMEText(body, 'plain'))
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
            
            print(f"✅ Confirmation email sent to {user_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send confirmation email: {e}")
            return False