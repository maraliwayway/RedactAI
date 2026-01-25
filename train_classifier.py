from src.detector.ai_classifier import AIClassifier

def main():
    print("🤖 Training AI Classifier\n")
    
    classifier = AIClassifier()
    classifier.train()
    classifier.save_model()
    
    print("\n✅ Training complete!")
    
    # Test predictions
    print("\n🧪 Testing predictions:")
    test_cases = [
        "My API key is abc123",
        "How do I write a loop?",
        "SSN: 123-45-6789",
        "Our internal server is down"
    ]
    
    for text in test_cases:
        category, confidence, probs = classifier.predict(text)
        print(f"\nText: {text}")
        print(f"Category: {category} ({confidence:.2%} confidence)")
        print(f"Probabilities: {probs}")

if __name__ == "__main__":
    main()