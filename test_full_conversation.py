"""
Full conversation flow test for WhatsApp Lead Bot
Simulates a complete conversation from first message to lead collection completion
"""
import requests
import json
import time
from typing import List, Dict

# Your webhook URL (n8n or local)
WEBHOOK_URL = "https://amanraj31.app.n8n.cloud/webhook-test/ffbe48f3-5f70-40c1-b625-4a78bab55561/webhook"
# Or for local testing: "http://localhost:8000/api/webhook"

# Test phone number (use the same number throughout to maintain conversation state)
TEST_PHONE = "917736053341"

def create_message_payload(phone: str, message_text: str, message_id: str = None) -> Dict:
    """Create a webhook payload for an incoming message"""
    if not message_id:
        message_id = f"wamid.test_{int(time.time())}"
    
    return {
        "object": "whatsapp_business_account",
        "entry": [
            {
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [
                    {
                        "value": {
                            "messaging_product": "whatsapp",
                            "metadata": {
                                "display_phone_number": "15551412315",
                                "phone_number_id": "892196903303430"
                            },
                            "messages": [
                                {
                                    "from": phone,
                                    "id": message_id,
                                    "timestamp": str(int(time.time())),
                                    "text": {
                                        "body": message_text
                                    },
                                    "type": "text"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }

def send_webhook(payload: Dict, description: str) -> bool:
    """Send a webhook payload and return success status"""
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print(f"\n📤 Sending: {description}")
        print(f"   Message: {payload['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']}")
        
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers, timeout=10)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Success")
            return True
        else:
            print(f"   ⚠️  Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_full_conversation_flow():
    """
    Test the complete conversation flow:
    1. First message (language detection + consent)
    2. User responds "YES" to consent
    3. User provides name
    4. User provides email
    5. User provides phone
    6. User provides location
    7. User provides job type
    8. Lead collection completes
    """
    
    print("=" * 70)
    print("🧪 TESTING FULL CONVERSATION FLOW")
    print("=" * 70)
    
    # Conversation steps
    conversation_steps = [
        {
            "step": 1,
            "description": "First message - Language detection + Consent request",
            "message": "Hello, I'm interested in truck driving jobs in Europe"
        },
        {
            "step": 2,
            "description": "User grants consent",
            "message": "YES",
            "wait": 2  # Wait 2 seconds for bot to process and respond
        },
        {
            "step": 3,
            "description": "User provides name",
            "message": "My name is John Smith",
            "wait": 2
        },
        {
            "step": 4,
            "description": "User provides email",
            "message": "My email is john.smith@example.com",
            "wait": 2
        },
        {
            "step": 5,
            "description": "User provides phone",
            "message": "My phone number is +1234567890",
            "wait": 2
        },
        {
            "step": 6,
            "description": "User provides location",
            "message": "I'm located in Warsaw, Poland",
            "wait": 2
        },
        {
            "step": 7,
            "description": "User provides job type",
            "message": "I'm interested in truck driving jobs",
            "wait": 2
        }
    ]
    
    results = []
    
    for step_info in conversation_steps:
        step = step_info["step"]
        description = step_info["description"]
        message = step_info["message"]
        wait_time = step_info.get("wait", 1)
        
        # Create payload
        payload = create_message_payload(TEST_PHONE, message)
        
        # Send webhook
        success = send_webhook(payload, f"Step {step}: {description}")
        results.append({"step": step, "success": success, "description": description})
        
        # Wait before next message (to simulate real conversation timing)
        if wait_time > 0:
            print(f"   ⏳ Waiting {wait_time} seconds...")
            time.sleep(wait_time)
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for result in results:
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} - Step {result['step']}: {result['description']}")
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\n📈 Success Rate: {passed}/{total} ({passed*100//total}%)")
    
    if passed == total:
        print("🎉 All conversation steps completed successfully!")
    else:
        print("⚠️  Some steps failed. Check your webhook logs for details.")

def test_consent_denial_flow():
    """Test conversation flow when user denies consent"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTING CONSENT DENIAL FLOW")
    print("=" * 70)
    
    steps = [
        {
            "description": "First message",
            "message": "Hello"
        },
        {
            "description": "User denies consent",
            "message": "NO"
        }
    ]
    
    test_phone = f"{TEST_PHONE}_denial"
    
    for step_info in steps:
        payload = create_message_payload(test_phone, step_info["message"])
        send_webhook(payload, step_info["description"])
        time.sleep(1)

def test_multilingual_flow():
    """Test conversation in different languages"""
    
    print("\n" + "=" * 70)
    print("🧪 TESTING MULTILINGUAL FLOWS")
    print("=" * 70)
    
    languages = [
        {"lang": "Polish", "first": "Cześć, szukam pracy", "consent": "TAK"},
        {"lang": "German", "first": "Hallo, ich suche einen Job", "consent": "JA"},
        {"lang": "Spanish", "first": "Hola, busco trabajo", "consent": "SÍ"},
    ]
    
    for i, lang_info in enumerate(languages):
        test_phone = f"{TEST_PHONE}_lang_{i}"
        
        print(f"\n🌍 Testing {lang_info['lang']} conversation:")
        
        # First message
        payload = create_message_payload(test_phone, lang_info["first"])
        send_webhook(payload, f"{lang_info['lang']} - First message")
        time.sleep(1)
        
        # Consent
        payload = create_message_payload(test_phone, lang_info["consent"])
        send_webhook(payload, f"{lang_info['lang']} - Consent")
        time.sleep(2)

if __name__ == "__main__":
    print("🚀 Starting WhatsApp Lead Bot Conversation Tests\n")
    
    # Test 1: Full conversation flow
    test_full_conversation_flow()
    
    # Test 2: Consent denial
    test_consent_denial_flow()
    
    # Test 3: Multilingual support
    test_multilingual_flow()
    
    print("\n" + "=" * 70)
    print("✅ All tests completed!")
    print("=" * 70)
    print("\n💡 Tips:")
    print("   - Check your n8n workflow execution logs")
    print("   - Verify conversation state is maintained between messages")
    print("   - Check that bot responses are generated correctly")
    print("   - Verify lead data collection at each step")

