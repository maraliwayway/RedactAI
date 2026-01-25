from src.detector.regex_detector import RegexDetector

def test_regex_detector():
    detector = RegexDetector()
    
    # Test cases
    test_cases = [
        ("Hello world, this is safe text", 0),
        ("My API key is api_key: sk_live_1234567890abcdefghijklmn", 1),
        ("AWS key: AKIAIOSFODNN7EXAMPLE", 1),
        ("My email is john@example.com", 1),
        ("Here's my JWT: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U", 1),
    ]
    
    print("🧪 Testing Regex Detector\n")
    for text, expected_min_detections in test_cases:
        detections, risk_score = detector.detect(text)
        status = "✅" if len(detections) >= expected_min_detections else "❌"
        print(f"{status} Text: {text[:50]}...")
        print(f"   Detections: {len(detections)}, Risk Score: {risk_score}")
        if detections:
            for d in detections:
                print(f"   - Found: {d['type']} (severity: {d.get('severity', 'N/A')})")
        print()

if __name__ == "__main__":
    test_regex_detector()