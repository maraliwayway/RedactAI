from src.email_notifier import EmailNotifier
import os
from dotenv import load_dotenv

load_dotenv()

print("=== EMAIL CONFIGURATION CHECK ===")
print(f"SMTP_SERVER: {os.getenv('SMTP_SERVER')}")
print(f"SMTP_PORT: {os.getenv('SMTP_PORT')}")
print(f"SMTP_USERNAME: {os.getenv('SMTP_USERNAME')}")
print(f"SMTP_PASSWORD: {'SET' if os.getenv('SMTP_PASSWORD') else 'NOT SET'}")
print(f"SMTP_FROM_EMAIL: {os.getenv('SMTP_FROM_EMAIL')}")
print()

# Test email sending
notifier = EmailNotifier()

result = {
    'decision': 'WARN',
    'overall_risk_score': 85,
    'ai_category': 'credentials',
    'ai_confidence': 0.95,
    'explanation': 'Found 2 potential secret(s): Email, Generic Api Key',
    'regex_detections': [
        {'type': 'email', 'value': 'test@example.com'},
        {'type': 'generic_api_key', 'value': 'api_key_abc123'}
    ]
}

print("=== SENDING TEST EMAIL ===")
success = notifier.send_blocked_content_alert(
    user_email='mara_liwayway_david@sfu.ca',
    boss_email='akm27@sfu.ca',
    username='maraliwayway',
    analysis_result=result,
    text_preview='My API key is abc123xyz and my email is test@example.com'
)

print(f"\nEmail sent: {success}")

if not success:
    print("\nTROUBLESHOOTING:")
    print("1. Check if .env file exists: cat .env")
    print("2. Make sure Gmail app password is correct")
    print("3. Check spam folder")
    print("4. Try with different email provider")