from typing import Dict, List
from .regex_detector import RegexDetector
from .ai_classifier import AIClassifier

class DetectionEngine:
    """Combines regex and AI detection for comprehensive analysis."""
    
    def __init__(self):
        self.regex_detector = RegexDetector()
        self.ai_classifier = AIClassifier()
        
        # Try to load trained model
        try:
            self.ai_classifier.load_model()
        except FileNotFoundError:
            print("⚠️  No trained model found. Training new model...")
            self.ai_classifier.train()
            self.ai_classifier.save_model()
    
    def analyze(self, text: str) -> Dict:
        """
        Comprehensive analysis combining regex and AI.
        Returns full risk assessment.
        """
        # Regex detection
        regex_detections, regex_risk = self.regex_detector.detect(text)
        
        # AI classification
        ai_category, ai_confidence, ai_probs = self.ai_classifier.predict(text)
        
        # Combine results
        overall_risk = self._calculate_overall_risk(regex_risk, ai_category, ai_confidence)
        decision = self._make_decision(overall_risk, regex_detections, ai_category)
        
        return {
            'decision': decision,  # 'SAFE', 'WARN', 'BLOCK'
            'overall_risk_score': overall_risk,
            'regex_detections': regex_detections,
            'regex_risk_score': regex_risk,
            'ai_category': ai_category,
            'ai_confidence': ai_confidence,
            'ai_probabilities': ai_probs,
            'explanation': self._generate_explanation(regex_detections, ai_category, decision)
        }
    
    def _calculate_overall_risk(self, regex_risk: int, ai_category: str, ai_confidence: float) -> int:
        """Calculate combined risk score (0-100)."""
        # Weight regex more heavily (it's more definitive)
        regex_weight = 0.7
        ai_weight = 0.3
        
        # Convert AI prediction to risk score
        ai_risk_map = {
            'credentials': 90,
            'personal_data': 70,
            'proprietary_info': 60,
            'safe': 0
        }
        ai_risk = ai_risk_map.get(ai_category, 0) * ai_confidence
        
        overall = int(regex_weight * regex_risk + ai_weight * ai_risk)
        return min(overall, 100)
    
    def _make_decision(self, risk_score: int, regex_detections: List, ai_category: str) -> str:
        """Make final decision: SAFE, WARN, or BLOCK."""
        # High-severity regex detections = automatic block
        high_severity_found = any(
            d.get('severity') == 'HIGH' for d in regex_detections
        )
        
        if high_severity_found or risk_score >= 70:
            return 'BLOCK'
        elif risk_score >= 40 or ai_category in ['credentials', 'personal_data']:
            return 'WARN'
        else:
            return 'SAFE'
    
    def _generate_explanation(self, regex_detections: List, ai_category: str, decision: str) -> str:
        """Generate human-readable explanation."""
        parts = []
        
        if regex_detections:
            types = [d['type'].replace('_', ' ').title() for d in regex_detections]
            parts.append(f"Found {len(regex_detections)} potential secret(s): {', '.join(set(types))}")
        
        if ai_category != 'safe':
            parts.append(f"AI detected: {ai_category.replace('_', ' ').title()}")
        
        if decision == 'BLOCK':
            parts.append("❌ This content should NOT be sent.")
        elif decision == 'WARN':
            parts.append("⚠️  Review carefully before sending.")
        else:
            parts.append("✅ Content appears safe.")
        
        return " | ".join(parts) if parts else "✅ No sensitive content detected."