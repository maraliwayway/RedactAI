from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import numpy as np
import pickle
import os
from typing import Tuple, Dict

class AIClassifier:
    """AI-based semantic classifier for sensitive content detection."""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.classifier = None
        self.categories = ['credentials', 'personal_data', 'proprietary_info', 'safe']
        
    def train(self, training_data: list = None):
        """Train the classifier with sample data."""
        if training_data is None:
            training_data = self._get_default_training_data()
        
        # Prepare data
        texts = [item['text'] for item in training_data]
        labels = [item['label'] for item in training_data]
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Train classifier
        print("Training classifier...")
        self.classifier = LogisticRegression(max_iter=1000, random_state=42)
        self.classifier.fit(embeddings, labels)
        
        print(f"✓ Training complete. Accuracy: {self.classifier.score(embeddings, labels):.2%}")
        
    def predict(self, text: str) -> Tuple[str, float, Dict]:
        """
        Predict if text contains sensitive information.
        Returns: (category, confidence, details)
        """
        if self.classifier is None:
            raise ValueError("Classifier not trained. Call train() first.")
        
        # Generate embedding
        embedding = self.encoder.encode([text])
        
        # Predict
        prediction = self.classifier.predict(embedding)[0]
        probabilities = self.classifier.predict_proba(embedding)[0]
        confidence = float(np.max(probabilities))
        
        # Get probability distribution
        prob_dict = {self.categories[i]: float(probabilities[i]) 
                     for i in range(len(self.categories))}
        
        return prediction, confidence, prob_dict
    
    def save_model(self, path: str = 'src/models/classifier.pkl'):
        """Save trained classifier."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.classifier, f)
        print(f"✓ Model saved to {path}")
    
    def load_model(self, path: str = 'src/models/classifier.pkl'):
        """Load trained classifier."""
        with open(path, 'rb') as f:
            self.classifier = pickle.load(f)
        print(f"✓ Model loaded from {path}")
    
    def _get_default_training_data(self) -> list:
        """Default training dataset."""
        return [
            # Credentials
            {"text": "Here's my API key: sk_live_abc123xyz", "label": "credentials"},
            {"text": "My password is SecurePass123!", "label": "credentials"},
            {"text": "Database credentials: user=admin, pass=secret", "label": "credentials"},
            {"text": "AWS access key AKIAIOSFODNN7EXAMPLE", "label": "credentials"},
            {"text": "GitHub token: ghp_abc123xyz", "label": "credentials"},
            {"text": "Login with username admin and password test123", "label": "credentials"},
            {"text": "Auth token: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", "label": "credentials"},
            {"text": "SSH private key: -----BEGIN RSA PRIVATE KEY-----", "label": "credentials"},
            
            # Personal Data
            {"text": "My social security number is 123-45-6789", "label": "personal_data"},
            {"text": "Contact me at john.doe@email.com or 555-0123", "label": "personal_data"},
            {"text": "Credit card: 4532-1234-5678-9010", "label": "personal_data"},
            {"text": "My address is 123 Main St, Anytown USA", "label": "personal_data"},
            {"text": "Date of birth: January 15, 1990", "label": "personal_data"},
            {"text": "Driver's license number: D1234567", "label": "personal_data"},
            {"text": "Phone number is 555-123-4567", "label": "personal_data"},
            
            # Proprietary Info
            {"text": "Internal server IP: 192.168.1.100", "label": "proprietary_info"},
            {"text": "Our Q4 revenue projection is $5M", "label": "proprietary_info"},
            {"text": "Confidential: Project Falcon launches next month", "label": "proprietary_info"},
            {"text": "Trade secret algorithm uses XYZ methodology", "label": "proprietary_info"},
            {"text": "Internal database schema for customer table", "label": "proprietary_info"},
            {"text": "Company VPN configuration: vpn.internal.company.com", "label": "proprietary_info"},
            
            # Safe Content
            {"text": "How do I write a for loop in Python?", "label": "safe"},
            {"text": "Explain the concept of machine learning", "label": "safe"},
            {"text": "What's the weather like today?", "label": "safe"},
            {"text": "Can you help me debug this error?", "label": "safe"},
            {"text": "Write a function to sort an array", "label": "safe"},
            {"text": "Best practices for REST API design", "label": "safe"},
            {"text": "How does React hooks work?", "label": "safe"},
            {"text": "Explain quantum computing in simple terms", "label": "safe"},
            {"text": "What are the benefits of exercise?", "label": "safe"},
            {"text": "Recipe for chocolate chip cookies", "label": "safe"},
        ]