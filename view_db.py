from src.database import SessionLocal, User, ScanLog

db = SessionLocal()

# View all users
print("=" * 60)
print("USERS:")
print("=" * 60)
users = db.query(User).all()
for user in users:
    print(f"\nID: {user.id}")
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"Boss/Admin Email: {user.notification_email}")
    print(f"Created: {user.created_at}")
    print("-" * 60)

# View all scan logs
print("\n" + "=" * 60)
print("SCAN LOGS:")
print("=" * 60)
logs = db.query(ScanLog).order_by(ScanLog.timestamp.desc()).limit(10).all()
for log in logs:
    user = db.query(User).filter(User.id == log.user_id).first()
    print(f"\nUser: {user.username if user else 'Unknown'}")
    print(f"Decision: {log.decision}")
    print(f"Risk Score: {log.risk_score}")
    print(f"Text: {log.text_preview}")
    print(f"Timestamp: {log.timestamp}")
    print("-" * 60)

db.close()