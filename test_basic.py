#!/usr/bin/env python3
"""
Basic functionality tests for the WhatsApp Lead Collection system
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    try:
        from app.utils.consent_texts import get_consent_text, is_consent_yes, DEFAULT_LANGUAGE
        from app.utils.validators import validate_email, validate_phone, validate_required_fields
        from app.services.language_service import detect_language
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_consent_texts():
    """Test consent text functionality"""
    try:
        from app.utils.consent_texts import get_consent_text, is_consent_yes

        # Test English consent text
        text = get_consent_text("en")
        assert "permission to process your personal data" in text
        print("✅ English consent text loaded")

        # Test consent detection
        assert is_consent_yes("YES", "en") == True
        assert is_consent_yes("NO", "en") == False
        print("✅ Consent detection working")

        return True
    except Exception as e:
        print(f"❌ Consent text error: {e}")
        return False

def test_validators():
    """Test data validation"""
    try:
        from app.utils.validators import validate_email, validate_phone

        # Test email validation
        assert validate_email("test@example.com") == True
        assert validate_email("invalid-email") == False
        print("✅ Email validation working")

        # Test phone validation
        assert validate_phone("+1234567890") == True
        assert validate_phone("invalid") == False
        print("✅ Phone validation working")

        return True
    except Exception as e:
        print(f"❌ Validator error: {e}")
        return False

def test_language_detection():
    """Test language detection"""
    try:
        from app.services.language_service import detect_language, DEFAULT_LANGUAGE

        # Test English detection
        lang = detect_language("Hello, how are you?")
        assert lang in ["en", DEFAULT_LANGUAGE]  # Should detect English or fallback
        print("✅ Language detection working")

        return True
    except Exception as e:
        print(f"❌ Language detection error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running basic functionality tests...\n")

    tests = [
        test_imports,
        test_consent_texts,
        test_validators,
        test_language_detection
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed! The system is ready for deployment.")
        print("\n📋 Next steps:")
        print("1. Set up environment variables in .env file")
        print("2. Configure WhatsApp Business API")
        print("3. Set up Google Sheets API")
        print("4. Configure SMTP for email notifications")
        print("5. Deploy and test with real WhatsApp messages")
        return True
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

