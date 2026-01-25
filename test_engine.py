from src.detector.detection_engine import DetectionEngine

def test_detection_engine():
    engine = DetectionEngine()
    
    test_cases = [
        ("How do I write a Python function?", "SAFE"),
        ("My API key is api-key-abc123xyz456", "WARN"),
        ("AWS Secret: aws_secret_key='a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0'", "BLOCK"),
        ("Contact me at john@example.com", "WARN"),
        ("Our internal database is at 192.168.1.50", "WARN"),
    ]
    
    print("🧪 Testing Full Detection Engine\n")
    print("=" * 80)
    
    for text, expected_decision in test_cases:
        result = engine.analyze(text)
        status = "✅" if result['decision'] == expected_decision else "⚠️"
        
        print(f"\n{status} Test Case:")
        print(f"Text: {text}")
        print(f"Decision: {result['decision']} (expected: {expected_decision})")
        print(f"Risk Score: {result['overall_risk_score']}/100")
        print(f"AI Category: {result['ai_category']} ({result['ai_confidence']:.2%})")
        print(f"Regex Detections: {len(result['regex_detections'])}")
        print(f"Explanation: {result['explanation']}")
        print("-" * 80)

if __name__ == "__main__":
    test_detection_engine()