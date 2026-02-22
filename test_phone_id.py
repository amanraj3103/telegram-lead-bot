"""
Quick test script to verify WhatsApp Phone Number ID and access token
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_token = os.getenv("WHATSAPP_API_TOKEN")
phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")

if not api_token or not phone_number_id:
    print("❌ Missing credentials in .env file")
    exit(1)

# Test 1: Get phone number details
url = f"https://graph.facebook.com/v18.0/{phone_number_id}"
headers = {
    "Authorization": f"Bearer {api_token}"
}

print(f"Testing Phone Number ID: {phone_number_id}")
print(f"Access Token: {api_token[:20]}...")
print("\n" + "="*50)

try:
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        print("✅ Phone Number ID is valid!")
        print(f"Phone Number: {data.get('display_phone_number', 'N/A')}")
        print(f"Verified Name: {data.get('verified_name', 'N/A')}")
        print(f"Quality Rating: {data.get('quality_rating', 'N/A')}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 401:
            print("\n⚠️  Access token is invalid or expired")
        elif response.status_code == 403:
            print("\n⚠️  Access token doesn't have permission for this phone number")
except Exception as e:
    print(f"❌ Error: {e}")

