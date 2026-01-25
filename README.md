# RedactAI

A local AI-powered security tool that prevents sensitive information from being accidentally sent to Large Language Models (LLMs).

## Problem Statement

As students and professionals increasingly rely on large language models for coding, debugging, and writing assistance, they often unknowingly expose sensitive information such as API keys, credentials, internal code, or personal data when submitting prompts to LLMs. Despite security policies and training, manual caution is unreliable, especially under time pressure. Once sensitive data is sent to a cloud-hosted LLM, organizations lose control over where that data is processed or stored, creating data sovereignty, privacy, and compliance risks.

## Solution

RedactAI is a browser extension and local backend service that autonomously analyzes user input for sensitive information before it is sent to an LLM. The tool runs entirely on the user's device, combining AI-based semantic classification with deterministic secret detection to decide whether a prompt is safe, risky, or should be blocked. Users receive immediate risk assessments, and only proceed if the content is deemed safe, ensuring sensitive data never leaves the device unintentionally.

## Features

### Core Functionality
- Real-time content analysis before LLM submission
- AI-powered semantic classification of sensitive content
- Regex-based pattern matching for secrets and credentials
- Risk scoring system (0-100 scale)
- Visual popup warnings before submission
- Automatic blocking of high-risk content

### Security & Compliance
- Fully local AI processing (no external API calls/third party service for detection for privacy)
- Email notifications to administrators when sensitive content is detected
- Comprehensive audit logging of all scan attempts
- User confirmation emails for transparency

### User Experience
- Browser extension for ChatGPT, Claude.ai, and DeepSeek
- Persistent on-screen indicator showing protection status
- Web dashboard for scan history and configuration
- User authentication and session management

## Technologies Used

### Backend
- **FastAPI** - Modern Python web framework for building APIs
- **Python 3.13** - Core programming language
- **SQLAlchemy** - SQL toolkit and ORM
- **SQLite** - Lightweight database for local storage
- **Uvicorn** - ASGI server for running FastAPI

### AI/Machine Learning
- **Sentence Transformers** (all-MiniLM-L6-v2) - Local embedding model for semantic analysis
- **Scikit-learn** - Machine learning library for classification
- **Logistic Regression** - Classification algorithm for content categorization
- **NumPy & Pandas** - Data manipulation and numerical computing

### Security & Authentication
- **Argon2** - Modern password hashing algorithm
- **Python-JOSE** - JWT token generation and validation
- **Python-dotenv** - Environment variable management

### Frontend
- **Chrome Extension** (Manifest V3) - Browser integration
- **Vanilla JavaScript** - Content scripts and background workers
- **HTML/CSS** - Popup and dashboard interfaces
- **Jinja2** - Server-side templating

### Email & Notifications
- **SMTP** - Email protocol for notifications
- **smtplib** - Python SMTP client

## Architecture
```
Browser (ChatGPT/Claude/DeepSeek)
         |
         v
Chrome Extension (Content Script)
         |
         v (Message Passing)
Background Script
         |
         v (HTTP/REST API)
Local FastAPI Server (localhost:8000)
         |
         v
Detection Engine
    |         |
    v         v
Regex     AI Classifier
Detector  (Local Model)
         |
         v
Risk Decision Engine
         |
         v
SQLite Database + Email Notifier
```

## How to Run

### Prerequisites
- Python 3.13 or higher
- Google Chrome browser
- Git

### Installation

#### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/RedactAI.git
cd RedactAI
```

#### 2. Set Up Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

#### 3. Train the AI Model
```bash
python train_classifier.py
```

This will:
- Train the semantic classifier on sample data
- Save the trained model to `src/models/classifier.pkl`
- Display training accuracy

#### 4. Configure Email Notifications (Optional)

Create a `.env` file in the project root:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

For Gmail:
1. Enable 2-Factor Authentication
2. Generate an App Password at https://myaccount.google.com/apppasswords
3. Use the app password in the `.env` file

#### 5. Start the Backend Server
```bash
python run.py
```

The server will start at `http://localhost:8000`

You should see:
```
Model loaded from src/models/classifier.pkl
Database initialized
RedactAI is running!
```

#### 6. Create a User Account

1. Open browser and go to `http://localhost:8000`
2. Click "Sign up"
3. Fill in the registration form:
   - Username
   - Your email address
   - Password (minimum 6 characters)
   - Administrator email (for notifications)
4. Click "Create Account"
5. You will be automatically logged in and redirected to the dashboard

#### 7. Install Chrome Extension

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top-right corner)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder from the project directory
5. The RedactAI extension icon should appear in your Chrome toolbar

#### 8. Test the Extension

1. Go to https://chatgpt.com
2. Look for the "RedactAI Active" indicator in the bottom-left corner
3. Type a test message with sensitive content:
```
   My AWS access key is AKIAIOSFODNN7EXAMPLE
   Password: admin123
   Database: postgres://user:pass@localhost
```
4. Click the Send button
5. A popup should appear warning about the sensitive content
6. You can either cancel to edit or proceed (which will trigger email notifications)

### Troubleshooting

#### Extension Not Working
- Check browser console (F12) for error messages
- Verify the backend server is running
- Ensure you're logged in at `http://localhost:8000`
- Reload the extension at `chrome://extensions/`

#### Email Not Sending
- Verify `.env` file exists and has correct credentials
- Check spam folder for emails
- Ensure 2FA is enabled for Gmail
- Test with a different SMTP provider if needed

#### Model Not Loading
- Run `python train_classifier.py` to create the model
- Verify `src/models/classifier.pkl` exists
- Check file permissions

## Project Structure
```
RedactAI/
├── src/
│   ├── detector/
│   │   ├── __init__.py
│   │   ├── regex_detector.py      # Pattern matching for secrets
│   │   ├── ai_classifier.py       # ML-based semantic analysis
│   │   └── detection_engine.py    # Combined detection logic
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── database.py                # Database models and setup
│   ├── schemas.py                 # Pydantic models
│   ├── auth.py                    # Authentication logic
│   └── email_notifier.py          # Email notification system
├── chrome-extension/
│   ├── manifest.json              # Extension configuration
│   ├── content.js                 # Content script for page monitoring
│   ├── background.js              # Background service worker
│   ├── popup.html                 # Extension popup UI
│   ├── popup.js                   # Popup logic
│   ├── styles.css                 # Styling for overlays
│   └── icons/                     # Extension icons
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html
├── data/                          # SQLite database (created on first run)
├── logs/                          # Application logs
├── requirements.txt               # Python dependencies
├── run.py                         # Server startup script
├── .env                           # Environment variables (create this)
├── .gitignore
└── README.md
```

## Detection Categories

The AI classifier categorizes content into four main types:

- **Credentials**: API keys, passwords, tokens, access keys
- **Personal Data**: Email addresses, phone numbers, SSNs, credit cards
- **Proprietary Information**: Internal IPs, confidential data, trade secrets
- **Safe Content**: General queries, code without secrets

## Risk Levels

- **SAFE (0-39)**: Content can be sent without warnings
- **WARN (40-69)**: User receives a warning but can proceed
- **BLOCK (70-100)**: High-risk content, administrator notified if user proceeds

## Development

### Running Tests
```bash
python -m pytest tests/
```

