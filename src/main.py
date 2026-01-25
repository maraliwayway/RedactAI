from fastapi import FastAPI, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from .email_notifier import EmailNotifier

from .database import get_db, User, ScanLog, init_db
from .schemas import (
    UserCreate, UserLogin, UserResponse, Token,
    TextAnalysisRequest, TextAnalysisResponse, ScanLogResponse
)
from .auth import (
    verify_password, get_password_hash, create_access_token, decode_access_token
)
from .detector.detection_engine import DetectionEngine

# Initialize FastAPI app
app = FastAPI(title="RedactAI", description="Local AI Gatekeeper for Safe LLM Usage")

# Templates
templates = Jinja2Templates(directory="templates")

# Initialize detection engine
detection_engine = DetectionEngine()
email_notifier = EmailNotifier() 


# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print("🚀 RedactAI is running!")

# Helper: Get current user from cookie
def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    """Get current user from session cookie."""
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    username = decode_access_token(token)
    if not username:
        return None
    
    user = db.query(User).filter(User.username == username).first()
    return user

# ==================== API Routes ====================

@app.post("/api/signup", response_model=UserResponse)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if username exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=get_password_hash(user.password),
        notification_email=user.notification_email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/api/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token."""
    db_user = db.query(User).filter(User.username == user.username).first()
    
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create access token
    access_token = create_access_token(data={"sub": db_user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/analyze", response_model=TextAnalysisResponse)
def analyze_text(
    request: TextAnalysisRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Analyze text for sensitive content."""
    current_user = get_current_user(req, db)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Run detection
    result = detection_engine.analyze(request.text)
    
    # Log the scan
    log = ScanLog(
        user_id=current_user.id,
        text_preview=request.text[:100],
        decision=result['decision'],
        risk_score=result['overall_risk_score'],
        ai_category=result['ai_category'],
        detections_count=len(result['regex_detections']),
        was_blocked=(result['decision'] == 'BLOCK')
    )
    db.add(log)
    db.commit()
    
    return {
        **result,
        "timestamp": datetime.utcnow()
    }

@app.post("/api/user-proceeded")
def user_proceeded_with_warning(
    request: TextAnalysisRequest,
    req: Request,
    db: Session = Depends(get_db)
):
    """Called when user proceeds despite warning - sends email to boss."""
    current_user = get_current_user(req, db)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Re-analyze to get the warning details
    result = detection_engine.analyze(request.text)
    
    # Get platform from referrer header
    referrer = req.headers.get('referer', '')
    platform = 'Unknown Platform'
    if 'chatgpt.com' in referrer or 'chat.openai.com' in referrer:
        platform = 'ChatGPT'
    elif 'claude.ai' in referrer:
        platform = 'Claude.ai'
    elif 'deepseek.com' in referrer:
        platform = 'DeepSeek'
    
    print(f"📧 User {current_user.username} proceeded despite warning on {platform}!")
    print(f"   Sending email notifications...")
    
    # Send to boss
    boss_notified = email_notifier.send_blocked_content_alert(
        user_email=current_user.email,
        boss_email=current_user.notification_email,
        username=current_user.username,
        analysis_result=result,
        text_preview=request.text[:200],
        platform=platform  # NEW: Pass platform
    )
    
    # Send confirmation to user
    email_notifier.send_user_confirmation(
        user_email=current_user.email,
        username=current_user.username,
        analysis_result=result,
        text_preview=request.text[:200],
        boss_notified=boss_notified
    )
    
    return {"status": "emails_sent", "boss_notified": boss_notified}


@app.get("/api/history", response_model=list[ScanLogResponse])
def get_scan_history(
    req: Request,
    db: Session = Depends(get_db),
    limit: int = 20
):
    """Get user's scan history."""
    current_user = get_current_user(req, db)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    logs = db.query(ScanLog).filter(
        ScanLog.user_id == current_user.id
    ).order_by(ScanLog.timestamp.desc()).limit(limit).all()
    
    return logs

# ==================== HTML Routes ====================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page - redirect to dashboard if logged in, else show login."""
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard")
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page."""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    """Signup page."""
    return templates.TemplateResponse("signup.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Main dashboard for text analysis."""
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login")
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": user
    })

@app.post("/web-login")
async def web_login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle web form login."""
    db_user = db.query(User).filter(User.username == username).first()
    
    if not db_user or not verify_password(password, db_user.hashed_password):
        return RedirectResponse(url="/login?error=invalid", status_code=303)
    
    # Create token
    access_token = create_access_token(data={"sub": db_user.username})
    
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.post("/web-signup")
async def web_signup(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    notification_email: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle web form signup."""
    # Check existing users
    if db.query(User).filter(User.username == username).first():
        return RedirectResponse(url="/signup?error=username_exists", status_code=303)
    
    if db.query(User).filter(User.email == email).first():
        return RedirectResponse(url="/signup?error=email_exists", status_code=303)
    
    # Create user
    db_user = User(
        username=username,
        email=email,
        hashed_password=get_password_hash(password),
        notification_email=notification_email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Auto-login
    access_token = create_access_token(data={"sub": db_user.username})
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/logout")
async def logout():
    """Logout user."""
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    return response