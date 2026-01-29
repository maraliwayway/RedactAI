# RedactAI

A local AI-powered security tool that prevents sensitive information from being accidentally sent to Large Language Models (LLMs).

## Team
- **Mara David** ([@maraliwayway](https://github.com/maraliwayway)) - Frontend, Backend, AI/ML Engineer
- **Amandeep Manan** ([@amandeepmanan04](https://github.com/amandeepmanan04)) - Designer, UI/UX Researcher, Pitcher

## Problem Statement

As students and professionals increasingly rely on large language models for coding, debugging, and writing assistance, they often unknowingly expose sensitive information such as API keys, credentials, internal code, or personal data when submitting prompts to LLMs. Despite security policies and training, manual caution is unreliable, especially under time pressure. Once sensitive data is sent to a cloud-hosted LLM, organizations lose control over where that data is processed or stored, creating data sovereignty, privacy, and compliance risks.

## Solution

RedactAI is a browser extension and local backend service that autonomously analyzes user input for sensitive information before it is sent to an LLM. The tool runs entirely on the user's device, combining AI-based semantic classification with deterministic secret detection to provide real-time risk assessments. Users receive immediate warnings about potentially sensitive content and can make informed decisions about whether to proceed.

## Features

### Core Functionality
- Real-time content analysis before LLM submission
- AI-powered semantic classification of sensitive content
- Regex-based pattern matching for secrets and credentials
- Risk scoring system (0-100 scale)
- Visual popup warnings before submission
- Two-tier decision system: SAFE (no warning) or WARN (user chooses to proceed or cancel)

### Security & Compliance
- Fully local AI processing using Sentence Transformers (no external API calls for detection)
- Email notifications to administrators when users proceed despite warnings
- Platform detection (ChatGPT only)
- Comprehensive audit logging of all scan attempts
- User confirmation emails for transparency

### User Experience
- Browser extension for ChatGPT
- Web dashboard for scan history and manual text analysis
- User authentication and session management
- Intuitive warning popups with clear explanations

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
- **NumPy** - Numerical computing library

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
- **Gmail SMTP** - Email delivery service

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
- Gmail account with 2-Factor Authentication (for email notifications)

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

#### 4. Configure Email Notifications

Create a `.env` file in the project root:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
SMTP_FROM_EMAIL=your-email@gmail.com
```

**To get a Gmail app password:**
1. Enable 2-Factor Authentication on your Google account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and generate a password
4. Copy the 16-character password (remove spaces)
5. Use this password in the `.env` file

**Note:** The SMTP credentials configure the email service used to send notifications. The administrator email is set during user account creation.

#### 5. Start the Backend Server
```bash
python run.py
```

The server will start at http://localhost:8000

You should see:
```
Model loaded from src/models/classifier.pkl
Database initialized
RedactAI is running!
```

#### 6. Create a User Account

1. Open browser and go to http://localhost:8000
2. Click "Sign up"
3. Fill in the registration form:
   - Username
   - Your email address
   - Password (minimum 6 characters)
   - Administrator email (receives notifications when you proceed despite warnings)
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
2. Type a test message with sensitive content:
```
   My email is test@example.com and my API key is sk_live_abc123xyz
```
3. Click the Send button
4. A popup should appear warning about the sensitive content
5. Click "Cancel & Edit" to revise, or "Proceed Anyway" to send (this will trigger email notifications to your administrator)

### Troubleshooting

#### Extension Not Working
- Check browser console (F12) for error messages
- Verify the backend server is running with `python run.py`
- Ensure you're logged in at http://localhost:8000
- Reload the extension at `chrome://extensions/`

#### Email Not Sending
- Verify `.env` file exists in project root with correct credentials
- Check that you're using a Gmail app password, not your regular password
- Check spam folder for emails
- Run `python test_email.py` to test email configuration
- Review terminal output for error messages

#### Model Not Loading
- Run `python train_classifier.py` to create the model
- Verify `src/models/classifier.pkl` exists
- Check file permissions

#### Database Issues
- Delete `data/redactai.db` and restart server to recreate database
- Run `python view_db.py` to inspect database contents

## Project Structure
```
RedactAI/
├── src/
│   ├── detector/
│   │   ├── regex_detector.py      # Pattern matching for secrets
│   │   ├── ai_classifier.py       # ML-based semantic analysis
│   │   └── detection_engine.py    # Combined detection logic
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
│   └── styles.css                 # Styling for overlays
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html
├── data/                          # SQLite database (created on first run)
├── requirements.txt               # Python dependencies
├── run.py                         # Server startup script
├── train_classifier.py            # Script to train AI model
├── view_db.py                     # Script to view database contents
├── test_email.py                  # Script to test email configuration
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

- **SAFE (0-29)**: Content can be sent without warnings
- **WARN (30-100)**: User receives a warning and can choose to proceed or cancel

## How It Works

1. **Browser Extension Monitors Input**: The Chrome extension monitors text input on ChatGPT, Claude.ai, and DeepSeek
2. **Real-Time Analysis**: When you click Send, the extension intercepts the submission and sends the text to the local backend for analysis
3. **Detection Engine**: The backend combines regex pattern matching with AI semantic classification to assess risk
4. **User Decision**: If sensitive content is detected, a popup appears with details and you choose whether to proceed
5. **Email Notification**: If you proceed despite the warning, an email is sent to your administrator with incident details
6. **Audit Logging**: All scans are logged in the database for review in the web dashboard

## Email Notifications

When a user proceeds despite a warning, the administrator receives an email containing:
- User information (username and email)
- Timestamp of the incident
- Platform where it occurred (ChatGPT, Claude.ai, DeepSeek)
- Risk assessment (score and AI category)
- Types of sensitive data detected (without revealing the actual values)
- Text preview of the submission

## Security & Privacy

- All AI detection runs locally on your machine
- No sensitive data is sent to external services
- User passwords are hashed with Argon2
- Session management uses JWT tokens
- Database is stored locally in SQLite

## License

MIT License
