console.log('RedactAI Extension loaded');

// Configuration
const API_URL = 'http://localhost:8000';
let isAnalyzing = false;
let lastAnalyzedText = '';

// Site-specific selectors for text input
const SITE_SELECTORS = {
  'chatgpt.com': {
    input: 'div#prompt-textarea[contenteditable="true"]', 
    sendButton: 'button[data-testid="send-button"]'
  },
  'chat.openai.com': {
    input: 'div#prompt-textarea[contenteditable="true"]',  
    sendButton: 'button[data-testid="send-button"]'
  },
  'claude.ai': {
    input: 'div[contenteditable="true"]',
    sendButton: 'button[aria-label="Send Message"]'
  },
  'chat.deepseek.com': {
    input: 'textarea',
    sendButton: 'button[type="submit"]'
  }
};

// Get current site config
function getSiteConfig() {
  const hostname = window.location.hostname;
  for (const [domain, config] of Object.entries(SITE_SELECTORS)) {
    if (hostname.includes(domain)) {
      return config;
    }
  }
  return null;
}

// Get text from input (handles both textarea and contenteditable)
function getInputText(element) {
  if (!element) return '';
  
  if (element.tagName === 'TEXTAREA' || element.tagName === 'INPUT') {
    return element.value;
  } else if (element.isContentEditable) {
    return element.innerText || element.textContent;
  }
  return '';
}

// Analyze text with backend (via background script to bypass CSP)
async function analyzeText(text) {
  console.log('📡 Sending text to background script for analysis...');
  
  return new Promise((resolve) => {
    chrome.runtime.sendMessage(
      { action: 'analyzeText', text: text },
      (response) => {
        if (chrome.runtime.lastError) {
          console.error('❌ Chrome runtime error:', chrome.runtime.lastError);
          resolve(null);
          return;
        }

        if (!response) {
          console.error('❌ No response from background script');
          resolve(null);
          return;
        }

        if (response.success === false) {
          console.error('❌ API error:', response.error);
          resolve(null);
          return;
        }

        if (response.data && response.data.error === 'NOT_AUTHENTICATED') {
          console.error('❌ Not authenticated');
          alert('⚠️ Please log in to RedactAI at http://localhost:8000 first!');
          resolve(null);
          return;
        }

        console.log('✅ Analysis result:', response.data);
        resolve(response.data);
      }
    );
  });
}

// Show warning overlay
function showWarning(result, inputElement, sendButton) {
  // Remove existing overlay
  const existing = document.getElementById('redactai-overlay');
  if (existing) existing.remove();

  // Create overlay
  const overlay = document.createElement('div');
  overlay.id = 'redactai-overlay';
  overlay.className = `redactai-overlay ${result.decision.toLowerCase()}`;

  overlay.innerHTML = `
    <div class="redactai-modal">
      <div class="redactai-header warn">
        <span class="redactai-icon">⚠️</span>
        <h2>Sensitive Content Detected</h2>
      </div>
      <div class="redactai-content">
        <div class="redactai-score">
          <strong>Risk Score:</strong> ${result.overall_risk_score}/100
        </div>
        <div class="redactai-category">
          <strong>Category:</strong> ${result.ai_category} (${(result.ai_confidence * 100).toFixed(1)}% confidence)
        </div>
        <div class="redactai-explanation">
          <strong>Why:</strong> ${result.explanation}
        </div>
        ${result.regex_detections.length > 0 ? `
          <div class="redactai-detections">
            <strong>Detections:</strong>
            <ul>
              ${result.regex_detections.slice(0, 3).map(d => 
                `<li>${d.type.replace(/_/g, ' ')}</li>`
              ).join('')}
            </ul>
          </div>
        ` : ''}
        <div class="redactai-warning-text">
          ⚠️ <strong>If you proceed, your administrator will be notified.</strong>
        </div>
      </div>
      <div class="redactai-button-explanation">
        <strong>Cancel</strong> to edit your message, or <strong>Send Anyway</strong> (boss will be notified)
      </div>
      <div class="redactai-actions">
        <button id="redactai-cancel" class="redactai-btn redactai-btn-cancel">
          Cancel
        </button>
        <button id="redactai-proceed" class="redactai-btn redactai-btn-warning">
          Send Anyway
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(overlay);

  // Add event listeners
  document.getElementById('redactai-cancel').addEventListener('click', () => {
    overlay.remove();
    inputElement.focus();
  });

  document.getElementById('redactai-proceed').addEventListener('click', async () => {
    console.log('User clicked Proceed - sending emails...');
    overlay.remove();
    
    // Get the text
    const text = getInputText(inputElement);
    
    // Send notification that user proceeded
    chrome.runtime.sendMessage(
      { action: 'userProceeded', text: text },
      (response) => {
        if (response && response.success) {
          console.log('✅ Boss notified!');
        }
      }
    );
    
    // Allow submission to LLM
    lastAnalyzedText = text;
    sendButton.click();
  });
}

// Check before submission
async function checkBeforeSubmit(event, inputElement, sendButton) {
  const text = getInputText(inputElement);
  
  // Skip if empty
  if (!text || text.trim().length < 10) {
    return;
  }

  // Skip if already analyzed this exact text
  if (text === lastAnalyzedText) {
    return;
  }

  // Prevent default submission
  event.preventDefault();
  event.stopPropagation();

  // Show loading state
  if (sendButton) {
    sendButton.disabled = true;
  }

  console.log('🔍 Analyzing text before submission...');

  // Analyze
  const result = await analyzeText(text);

  // Re-enable button
  if (sendButton) {
    sendButton.disabled = false;
  }

  if (!result) {
    console.warn('Could not analyze text. Allowing submission.');
    lastAnalyzedText = text;
    return;
  }

  console.log('Analysis result:', result);

  // If SAFE, allow submission
  if (result.decision === 'SAFE') {
    console.log('✅ Content is safe, allowing submission');
    lastAnalyzedText = text;
    sendButton.click();
    return;
  }

  // Show warning for WARN or BLOCK
  showWarning(result, inputElement, sendButton);
}

// Initialize monitoring
function initializeMonitoring() {
  const config = getSiteConfig();
  
  if (!config) {
    console.log('RedactAI: Site not configured for monitoring');
    return;
  }

  console.log('RedactAI: Initializing monitoring...');

  // Wait for elements to load
  const checkInterval = setInterval(() => {
    const inputElement = document.querySelector(config.input);
    const sendButton = document.querySelector(config.sendButton);

    if (inputElement && sendButton) {
      clearInterval(checkInterval);
      console.log('✅ RedactAI: Monitoring active');

      // Intercept send button clicks
      sendButton.addEventListener('click', (e) => {
        checkBeforeSubmit(e, inputElement, sendButton);
      }, true);

      // Also intercept Enter key in input
      inputElement.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          checkBeforeSubmit(e, inputElement, sendButton);
        }
      }, true);
    }
  }, 1000);

  // Stop checking after 30 seconds
  setTimeout(() => clearInterval(checkInterval), 30000);
}

// Start monitoring when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeMonitoring);
} else {
  initializeMonitoring();
}

// Re-initialize on navigation (for SPAs)
let lastUrl = location.href;
new MutationObserver(() => {
  const url = location.href;
  if (url !== lastUrl) {
    lastUrl = url;
    console.log('🔄 Page navigation detected, reinitializing...');
    initializeMonitoring();
  }
}).observe(document, { subtree: true, childList: true });