"""
Test script to simulate WhatsApp webhook events
This helps test your webhook endpoint locally or with n8n
"""
import requests
import json

# Your webhook URL (n8n or local)
WEBHOOK_URL = "https://amanraj31.app.n8n.cloud/webhook-test/ffbe48f3-5f70-40c1-b625-4a78bab55561/webhook"
# Or for local testing: "http://localhost:8000/api/webhook"

def test_incoming_message():
    """Simulate an incoming WhatsApp message webhook"""
    
    # Sample webhook payload for incoming message
    payload = {
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
                                    "from": "917736053341",  # Test recipient
                                    "id": "wamid.test123",
                                    "timestamp": "1234567890",
                                    "text": {
                                        "body": "Hello, I'm interested in the job"
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
    
    headers = {
        "Content-Type": "application/json",
        # Note: In production, Meta sends X-Hub-Signature-256 header
        # For testing, you might want to skip signature verification temporarily
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_message_status():
    """Simulate a message status update webhook"""
    
    payload = {
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
                            "statuses": [
                                {
                                    "id": "wamid.test123",
                                    "status": "delivered",
                                    "timestamp": "1234567890",
                                    "recipient_id": "917736053341"
                                }
                            ]
                        },
                        "field": "messages"
                    }
                ]
            }
        ]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_webhook_verification():
    """Test webhook verification (GET request)"""
    
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": "your_verify_token_here",  # Replace with your actual token
        "hub.challenge": "test_challenge_12345"
    }
    
    try:
        response = requests.get(WEBHOOK_URL, params=params)
        print(f"✅ Status Code: {response.status_code}")
        print(f"✅ Response: {response.text}")
        
        # Should return the challenge value
        if response.text == params["hub.challenge"]:
            print("✅ Webhook verification successful!")
            return True
        else:
            print("❌ Webhook verification failed - challenge mismatch")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing WhatsApp Webhook\n")
    print("=" * 50)
    
    print("\n1. Testing Webhook Verification (GET)...")
    test_webhook_verification()
    
    print("\n2. Testing Incoming Message (POST)...")
    test_incoming_message()
    
    print("\n3. Testing Message Status (POST)...")
    test_message_status()
    
    print("\n" + "=" * 50)
    print("✅ Testing complete!")

