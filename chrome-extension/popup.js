document.getElementById('openDashboard').addEventListener('click', () => {
    chrome.tabs.create({ url: 'http://localhost:8000/dashboard' });
  });
  
  document.getElementById('testExtension').addEventListener('click', () => {
    chrome.tabs.create({ url: 'https://chatgpt.com' });
  });
  
  // Check if backend is running
  async function checkBackend() {
    try {
      const response = await fetch('http://localhost:8000/');
      if (response.ok) {
        document.getElementById('status').className = 'status';
        document.getElementById('status').innerHTML = '<span>✅</span><span>Protection Active</span>';
      }
    } catch (error) {
      document.getElementById('status').className = 'status inactive';
      document.getElementById('status').innerHTML = '<span>⚠️</span><span>Backend Offline</span>';
    }
  }
  
  checkBackend();