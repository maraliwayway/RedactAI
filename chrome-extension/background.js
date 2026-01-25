console.log('RedactAI background script loaded');

const API_URL = 'http://localhost:8000';

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'analyzeText') {
    console.log('Background: Analyzing text...');
    
    // Make API call (not blocked by CSP in background script)
    fetch(`${API_URL}/api/analyze`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ text: request.text })
    })
    .then(response => {
      console.log('Background: API response status:', response.status);
      if (response.status === 401) {
        return { error: 'NOT_AUTHENTICATED', status: 401 };
      }
      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      console.log('Background: Sending result back to content script');
      sendResponse({ success: true, data: data });
    })
    .catch(error => {
      console.error('Background: Error:', error);
      sendResponse({ success: false, error: error.message });
    });
    
    // Keep channel open for async response
    return true;
  }
});