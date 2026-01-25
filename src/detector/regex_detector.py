import re
from typing import List, Dict, Tuple
from math import log2

class RegexDetector:
    """Detects secrets using regex patterns and entropy analysis."""
    
    def __init__(self):
        self.patterns = {
            'aws_access_key': r'AKIA[0-9A-Z]{16}',
            'aws_secret_key': r'aws(.{0,20})?[\'"][0-9a-zA-Z/+]{40}[\'"]',
            'github_token': r'gh[pousr]_[A-Za-z0-9_]{36,}',
            'generic_api_key': r'[aA][pP][iI][-_]?[kK][eE][yY][\s:=]+[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?',
            'slack_token': r'xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24,}',
            'stripe_key': r'sk_live_[0-9a-zA-Z]{24,}',
            'jwt_token': r'eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
            'private_key': r'-----BEGIN (RSA|EC|OPENSSH|PGP) PRIVATE KEY-----',
            'password_in_url': r'[a-zA-Z]{3,10}://[^:]+:([^@]{8,})@',
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'high_entropy_string': None  # Special case, handled separately
        }
    
    def calculate_entropy(self, text: str) -> float:
        """Calculate Shannon entropy of a string."""
        if not text:
            return 0.0
        
        entropy = 0
        for char in set(text):
            probability = text.count(char) / len(text)
            entropy -= probability * log2(probability)
        return entropy
    
    def detect_high_entropy_strings(self, text: str, threshold: float = 4.5, min_length: int = 20) -> List[Dict]:
        """Detect strings with high entropy (likely secrets)."""
        words = re.findall(r'\b[A-Za-z0-9+/=]{20,}\b', text)
        detections = []
        
        for word in words:
            if len(word) >= min_length:
                entropy = self.calculate_entropy(word)
                if entropy >= threshold:
                    detections.append({
                        'type': 'high_entropy_string',
                        'value': word[:20] + '...' if len(word) > 20 else word,
                        'entropy': round(entropy, 2),
                        'position': text.find(word)
                    })
        
        return detections
    
    def detect(self, text: str) -> Tuple[List[Dict], int]:
        """
        Detect secrets in text.
        Returns: (list of detections, risk_score)
        """
        detections = []
        
        # Check regex patterns
        for secret_type, pattern in self.patterns.items():
            if pattern is None:
                continue
                
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                detections.append({
                    'type': secret_type,
                    'value': match.group(0)[:30] + '...' if len(match.group(0)) > 30 else match.group(0),
                    'position': match.start(),
                    'severity': self._get_severity(secret_type)
                })
        
        # Check high entropy strings
        entropy_detections = self.detect_high_entropy_strings(text)
        detections.extend(entropy_detections)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(detections)
        
        return detections, risk_score
    
    def _get_severity(self, secret_type: str) -> str:
        """Get severity level for detected secret type."""
        high_severity = ['aws_secret_key', 'private_key', 'stripe_key', 'password_in_url']
        medium_severity = ['aws_access_key', 'github_token', 'generic_api_key', 'jwt_token']
        
        if secret_type in high_severity:
            return 'HIGH'
        elif secret_type in medium_severity:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _calculate_risk_score(self, detections: List[Dict]) -> int:
        """Calculate overall risk score (0-100)."""
        if not detections:
            return 0
        
        severity_scores = {'HIGH': 40, 'MEDIUM': 25, 'LOW': 10}
        total_score = 0
        
        for detection in detections:
            severity = detection.get('severity', 'LOW')
            total_score += severity_scores.get(severity, 10)
        
        return min(total_score, 100)