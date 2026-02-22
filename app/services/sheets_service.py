"""
Google Sheets service for storing lead data
"""
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class SheetsService:
    def __init__(self):
        self.sheet_name = os.getenv("GOOGLE_SHEET_NAME", "Dream Axis Leads")
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")
        self.scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        if not self.credentials_path:
            raise ValueError("Missing Google credentials path")

        self.client = None
        self.sheet = None

    def authenticate(self):
        """Authenticate with Google Sheets API"""
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path, self.scope
            )
            self.client = gspread.authorize(creds)
        except Exception as e:
            print(f"Error authenticating with Google Sheets: {e}")
            raise

    def get_or_create_sheet(self) -> bool:
        """
        Get existing sheet or create new one with headers
        """
        if not self.client:
            self.authenticate()

        try:
            self.sheet = self.client.open(self.sheet_name)
            return True
        except gspread.SpreadsheetNotFound:
            try:
                self.sheet = self.client.create(self.sheet_name)
                # Set up headers
                headers = [
                    "timestamp", "phone", "full_name", "email", "location",
                    "job_type", "consent_status", "consent_timestamp",
                    "consent_version", "language_code"
                ]
                self.sheet.sheet1.append_row(headers)
                return True
            except Exception as e:
                print(f"Error creating sheet: {e}")
                return False
        except Exception as e:
            print(f"Error accessing sheet: {e}")
            return False

    def append_lead(self, lead_data: Dict[str, Any]) -> bool:
        """
        Append a lead record to the sheet
        """
        if not self.sheet and not self.get_or_create_sheet():
            return False

        try:
            # Ensure data is in correct order matching headers
            row_data = [
                lead_data.get("timestamp", ""),
                lead_data.get("phone", ""),
                lead_data.get("full_name", ""),
                lead_data.get("email", ""),
                lead_data.get("location", ""),
                lead_data.get("job_type", ""),
                lead_data.get("consent_status", "Granted"),
                lead_data.get("consent_timestamp", ""),
                lead_data.get("consent_version", "v1.0"),
                lead_data.get("language_code", "en")
            ]

            self.sheet.sheet1.append_row(row_data)
            return True
        except Exception as e:
            print(f"Error appending lead to sheet: {e}")
            return False

    def find_and_delete_lead(self, phone: str) -> bool:
        """
        Find and delete/anonymize a lead by phone number for GDPR compliance
        """
        if not self.sheet and not self.get_or_create_sheet():
            return False

        try:
            # Get all records
            records = self.sheet.sheet1.get_all_records()

            for i, record in enumerate(records, start=2):  # Start from row 2 (after headers)
                if record.get("phone") == phone:
                    # Anonymize the record instead of deleting (better for audit trail)
                    anonymized_data = [
                        record.get("timestamp", ""),
                        phone,  # Keep phone for audit but mark as deleted
                        "[DELETED]",  # Anonymize personal data
                        "[DELETED]",
                        "[DELETED]",
                        "[DELETED]",
                        "Deleted",
                        datetime.utcnow().isoformat(),
                        record.get("consent_version", "v1.0"),
                        record.get("language_code", "en")
                    ]

                    # Update the row with anonymized data
                    self.sheet.sheet1.update(f"A{i}:J{i}", [anonymized_data])
                    return True

            return False  # Phone not found
        except Exception as e:
            print(f"Error deleting lead: {e}")
            return False

    def get_lead_count(self) -> int:
        """Get total number of leads (excluding headers)"""
        if not self.sheet and not self.get_or_create_sheet():
            return 0

        try:
            return len(self.sheet.sheet1.get_all_records())
        except Exception as e:
            print(f"Error getting lead count: {e}")
            return 0

