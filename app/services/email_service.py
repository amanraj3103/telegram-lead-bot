"""
Email service for admin notifications via SMTP
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Dict, Any, Optional

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.sender_email = os.getenv("SMTP_USERNAME")
        self.sender_password = os.getenv("SMTP_PASSWORD")
        self.admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")

        if not all([self.sender_email, self.sender_password, self.admin_emails]):
            raise ValueError("Missing required email configuration")

        # Clean up admin emails
        self.admin_emails = [email.strip() for email in self.admin_emails if email.strip()]

    def send_lead_notification(self, lead_data: Dict[str, Any]) -> bool:
        """
        Send email notification to admins about new lead
        """
        if not self.admin_emails:
            return False

        subject = "🆕 New Driver Lead – WhatsApp"

        # Create message body
        body = self._create_lead_email_body(lead_data)

        return self._send_email(subject, body, self.admin_emails)

    def _create_lead_email_body(self, lead_data: Dict[str, Any]) -> str:
        """Create formatted email body for lead notification"""
        body = f"""
🆕 New Driver Lead Received via WhatsApp

📅 Timestamp: {lead_data.get('timestamp', 'N/A')}
📱 Phone: {lead_data.get('phone', 'N/A')}
👤 Full Name: {lead_data.get('full_name', 'N/A')}
📧 Email: {lead_data.get('email', 'N/A')}
📍 Location: {lead_data.get('location', 'N/A')}
🚛 Job Type: {lead_data.get('job_type', 'N/A')}

🔒 Consent Status: {lead_data.get('consent_status', 'N/A')}
🕐 Consent Timestamp: {lead_data.get('consent_timestamp', 'N/A')}
📋 Consent Version: {lead_data.get('consent_version', 'N/A')}
🌍 Language: {lead_data.get('language_code', 'N/A')}

📡 Source: Meta WhatsApp Cloud API
🏢 Company: Dream Axis Travel Solutions

---
This is an automated notification from the WhatsApp Lead Collection System.
"""

        return body

    def _send_email(self, subject: str, body: str, recipients: list) -> bool:
        """
        Send email via SMTP
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            # Add body
            msg.attach(MIMEText(body, 'plain'))

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()

            # Login
            server.login(self.sender_email, self.sender_password)

            # Send email
            text = msg.as_string()
            server.sendmail(self.sender_email, recipients, text)

            # Close session
            server.quit()

            return True

        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_error_notification(self, error_message: str, error_details: Optional[str] = None) -> bool:
        """
        Send error notification to admins
        """
        if not self.admin_emails:
            return False

        subject = "🚨 WhatsApp Lead System Error"

        body = f"""
🚨 System Error Alert

An error occurred in the WhatsApp Lead Collection System:

❌ Error: {error_message}

{f"📋 Details: {error_details}" if error_details else ""}

🕐 Timestamp: {os.environ.get('CURRENT_DATE', 'Unknown')}

Please check the system logs for more information.
"""

        return self._send_email(subject, body, self.admin_emails)

