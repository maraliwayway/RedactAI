from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict
from datetime import datetime

# User schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    notification_email: EmailStr  # Boss/admin email for notifications

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    notification_email: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

# Analysis schemas
class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)

class TextAnalysisResponse(BaseModel):
    decision: str  # SAFE, WARN, BLOCK
    overall_risk_score: int
    regex_detections: List[Dict]
    ai_category: str
    ai_confidence: float
    explanation: str
    timestamp: datetime

class ScanLogResponse(BaseModel):
    id: int
    text_preview: str
    decision: str
    risk_score: int
    timestamp: datetime
    
    class Config:
        from_attributes = True