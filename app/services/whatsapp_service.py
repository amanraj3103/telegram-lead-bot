"""
WhatsApp Cloud API service for sending and receiving messages
"""
import hmac
import hashlib
import requests
import json
from typing import Optional, Dict, Any
from fastapi import HTTPException
import os

class WhatsAppService:
    def __init__(self):
        self.api_token = os.getenv("WHATSAPP_API_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        self.app_secret = os.getenv("WHATSAPP_APP_SECRET")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"

        if not all([self.api_token, self.phone_number_id]):
            raise ValueError("Missing required WhatsApp API credentials")

    def verify_webhook_signature(self, request_body: bytes, signature: str) -> bool:
        """
        Verify webhook signature from Meta
        """
        if not self.app_secret:
            # No app secret configured; skip signature verification
            return True

        expected_signature = hmac.new(
            self.app_secret.encode('utf-8'),
            request_body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(f"sha256={expected_signature}", signature)

    def send_message(self, to_phone: str, message: str) -> Optional[Dict[str, Any]]:
        """
        Send a text message via WhatsApp Cloud API
        """
        if not to_phone.startswith('+'):
            to_phone = f"+{to_phone}"

        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "to": to_phone,
            "type": "text",
            "text": {
                "body": message
            }
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            error_body = ""
            error_details = {}
            if getattr(e, "response", None) is not None:
                error_body = f" | Response: {e.response.text}"
                try:
                    error_json = e.response.json()
                    error_details = error_json.get("error", {})
                    error_code = error_details.get("code")
                    error_message = error_details.get("message", "")
                    
                    # Handle specific error codes
                    if error_code == 131030:
                        print(f"⚠️  WhatsApp Error: Recipient phone number ({to_phone}) not in allowed list.")
                        print(f"   To fix: Add this number to your allowed recipients list in Meta Business Manager:")
                        print(f"   https://business.facebook.com/settings/whatsapp-business-account")
                        print(f"   Go to: WhatsApp Manager > API Setup > Manage phone number list")
                    elif error_code == 131009:
                        print(f"⚠️  WhatsApp Error: Invalid parameter value")
                        print(f"   Check: Phone number format, message content, or API configuration")
                    else:
                        print(f"Error sending WhatsApp message: {e}{error_body}")
                except (json.JSONDecodeError, KeyError):
                    print(f"Error sending WhatsApp message: {e}{error_body}")
            else:
                print(f"Error sending WhatsApp message: {e}{error_body}")
            return None

    def extract_message_data(self, webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract message data from webhook payload
        """
        try:
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})

            # Handle both message and status updates
            if "messages" in value:
                message = value["messages"][0]
                return {
                    "phone": message["from"],
                    "message_id": message["id"],
                    "message_text": message.get("text", {}).get("body", ""),
                    "timestamp": message.get("timestamp"),
                    "type": "message"
                }
            elif "statuses" in value:
                # Status update (delivered, read, etc.)
                status = value["statuses"][0]
                return {
                    "phone": status.get("recipient_id"),
                    "status": status.get("status"),
                    "timestamp": status.get("timestamp"),
                    "type": "status"
                }

        except (KeyError, IndexError) as e:
            print(f"Error extracting message data: {e}")

        return None

    def mark_message_as_read(self, message_id: str) -> bool:
        """
        Mark a message as read
        """
        url = f"{self.base_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            error_body = ""
            if getattr(e, "response", None) is not None:
                error_body = f" | Response: {e.response.text}"
            print(f"Error marking message as read: {e}{error_body}")
            return False

    def validate_webhook_request(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """
        Validate webhook verification request from Meta
        """
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

