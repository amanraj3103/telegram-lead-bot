"""
WhatsApp webhook route handler
"""
from fastapi import APIRouter, Request, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from typing import Dict, Any, Optional
import json
import os

from app.services.whatsapp_service import WhatsAppService
from app.services.language_service import detect_language
from app.services.openai_service import OpenAIService
from app.services.sheets_service import SheetsService
from app.services.email_service import EmailService
from app.utils.consent_texts import (
    get_consent_text, is_consent_yes, is_consent_no, is_delete_request,
    get_consent_data
)
from app.utils.validators import validate_required_fields, create_lead_record

# Global services (will be injected via dependency injection in main.py)
openai_service = None
sheets_service = None
email_service = None

# In-memory storage for conversation state (in production, use Redis/database)
conversation_states = {}

router = APIRouter()

def get_whatsapp_service():
    return WhatsAppService()

def get_openai_service():
    return OpenAIService()

def get_sheets_service():
    return SheetsService()

def get_email_service():
    return EmailService()

@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Webhook verification endpoint for Meta WhatsApp API
    """
    challenge = whatsapp_service.validate_webhook_request(hub_mode, hub_verify_token, hub_challenge)
    if challenge:
        return PlainTextResponse(content=challenge)
    else:
        raise HTTPException(status_code=403, detail="Verification failed")

@router.post("/webhook")
async def handle_webhook(
    request: Request,
    whatsapp_service: WhatsAppService = Depends(get_whatsapp_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    sheets_service: SheetsService = Depends(get_sheets_service),
    email_service: EmailService = Depends(get_email_service)
):
    """
    Main webhook handler for incoming WhatsApp messages
    """
    try:
        # Get raw body for signature verification
        body = await request.body()

        # Verify webhook signature (optional but recommended for production)
        signature = request.headers.get("X-Hub-Signature-256")
        if signature and not whatsapp_service.verify_webhook_signature(body, signature):
            raise HTTPException(status_code=403, detail="Invalid signature")

        # Parse webhook data
        webhook_data = json.loads(body)

        # Extract message data
        message_data = whatsapp_service.extract_message_data(webhook_data)
        if not message_data:
            return {"status": "ok"}  # Not a message we need to handle

        phone = message_data["phone"]
        message_text = message_data["message_text"].strip()

        # Handle the message based on conversation state
        process_message(
            phone, message_text, message_data,
            whatsapp_service, openai_service, sheets_service, email_service
        )

        # Mark message as read
        if message_data.get("message_id"):
            whatsapp_service.mark_message_as_read(message_data["message_id"])

        return {"status": "ok"}

    except Exception as e:
        print(f"Webhook error: {e}")
        # Send error notification
        try:
            email_service.send_error_notification(
                "Webhook processing error",
                str(e)
            )
        except:
            pass
        raise HTTPException(status_code=500, detail="Internal server error")

def process_message(
    phone: str,
    message_text: str,
    message_data: Dict[str, Any],
    whatsapp_service: WhatsAppService,
    openai_service: OpenAIService,
    sheets_service: SheetsService,
    email_service: EmailService
):
    """
    Process incoming message and manage conversation flow
    """
    # Initialize conversation state if new user
    if phone not in conversation_states:
        # Detect language from first message
        language_code = detect_language(message_text)
        conversation_states[phone] = {
            "language_code": language_code,
            "stage": "consent",  # Start with consent
            "consent_given": False,
            "lead_data": {},
            "consent_timestamp": None
        }

    state = conversation_states[phone]
    language_code = state["language_code"]

    # Check for delete request first (works regardless of consent stage)
    if is_delete_request(message_text, language_code):
        handle_delete_request(phone, language_code, whatsapp_service, sheets_service)
        return

    # Handle conversation based on current stage
    if state["stage"] == "consent":
        handle_consent_stage(phone, message_text, state, message_data, whatsapp_service)

    elif state["stage"] == "collection":
        handle_collection_stage(
            phone, message_text, state,
            whatsapp_service, openai_service, sheets_service, email_service
        )

def handle_consent_stage(
    phone: str,
    message_text: str,
    state: Dict[str, Any],
    message_data: Dict[str, Any],
    whatsapp_service: WhatsAppService
):
    """Handle GDPR consent collection stage"""
    language_code = state["language_code"]
    consent_data = get_consent_data(language_code)

    if is_consent_yes(message_text, language_code):
        # Consent granted
        state["consent_given"] = True
        state["consent_timestamp"] = message_data.get("timestamp")
        state["stage"] = "collection"

        # Send confirmation and start collection
        confirmation_msg = consent_data["confirmation_yes"]
        whatsapp_service.send_message(phone, confirmation_msg)

        # Start AI conversation
        start_lead_collection(phone, state, whatsapp_service, openai_service)

    elif is_consent_no(message_text, language_code):
        # Consent denied
        confirmation_msg = consent_data["confirmation_no"]
        whatsapp_service.send_message(phone, confirmation_msg)

        # Reset conversation
        if phone in conversation_states:
            del conversation_states[phone]

    else:
        # Invalid response, send consent text again
        consent_text = get_consent_text(language_code)
        whatsapp_service.send_message(phone, consent_text)

def handle_collection_stage(
    phone: str,
    message_text: str,
    state: Dict[str, Any],
    whatsapp_service: WhatsAppService,
    openai_service: OpenAIService,
    sheets_service: SheetsService,
    email_service: EmailService
):
    """Handle lead data collection stage"""
    # Extract data from response
    extracted_data = openai_service.extract_data_from_response(
        message_text, state["lead_data"], state["language_code"]
    )

    # Update collected data
    state["lead_data"].update(extracted_data)

    # Check if collection is complete
    errors = validate_required_fields(state["lead_data"])

    if not errors:
        # Collection complete, save lead
        save_lead_and_notify(
            phone, state, sheets_service, email_service, whatsapp_service
        )
    else:
        # Generate next question
        next_question = openai_service.generate_next_question(
            state["language_code"], state["lead_data"], message_text
        )

        if next_question and not next_question.get("complete", False):
            question_text = next_question.get("question", "")
            if question_text:
                whatsapp_service.send_message(phone, question_text)

def start_lead_collection(
    phone: str,
    state: Dict[str, Any],
    whatsapp_service: WhatsAppService,
    openai_service: OpenAIService
):
    """Start the AI-powered lead collection conversation"""
    # Generate first question
    first_question = openai_service.generate_next_question(
        state["language_code"], {}, ""
    )

    if first_question and not first_question.get("complete", False):
        question_text = first_question.get("question", "")
        if question_text:
            whatsapp_service.send_message(phone, question_text)

def save_lead_and_notify(
    phone: str,
    state: Dict[str, Any],
    sheets_service: SheetsService,
    email_service: EmailService,
    whatsapp_service: WhatsAppService
):
    """Save completed lead and send notifications"""
    # Create complete lead record
    lead_record = create_lead_record(
        phone=phone,
        lead_data=state["lead_data"],
        language_code=state["language_code"],
        consent_status="Granted",
        consent_version="v1.0"
    )

    # Save to Google Sheets
    if sheets_service.append_lead(lead_record):
        # Send admin notification
        email_service.send_lead_notification(lead_record)

        # Send confirmation to user
        confirmation_msg = "Thank you! Your information has been recorded. We'll be in touch soon."
        if state["language_code"] != "en":
            # Use language-specific confirmation (could be enhanced)
            confirmation_msg = "Thank you! Your information has been recorded. We'll be in touch soon."

        whatsapp_service.send_message(phone, confirmation_msg)

        # Clean up conversation state
        if phone in conversation_states:
            del conversation_states[phone]
    else:
        # Error saving lead
        error_msg = "Sorry, there was an error saving your information. Please try again later."
        whatsapp_service.send_message(phone, error_msg)

def handle_delete_request(
    phone: str,
    language_code: str,
    whatsapp_service: WhatsAppService,
    sheets_service: SheetsService
):
    """Handle GDPR delete request"""
    consent_data = get_consent_data(language_code)

    # Attempt deletion
    if sheets_service.find_and_delete_lead(phone):
        confirmation_msg = consent_data["deletion_confirmation"]
        whatsapp_service.send_message(phone, confirmation_msg)

        # Clean up conversation state
        if phone in conversation_states:
            del conversation_states[phone]
    else:
        # Phone not found
        error_msg = "No records found for this phone number."
        whatsapp_service.send_message(phone, error_msg)
