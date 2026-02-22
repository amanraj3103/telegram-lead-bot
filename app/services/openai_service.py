"""
OpenAI service for AI-powered lead collection conversations
"""
import json
from typing import Dict, Any, Optional
import openai
import os

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Missing OpenAI API key")

        openai.api_key = self.api_key
        self.model = "gpt-3.5-turbo"  # Cost-effective for this use case

    def generate_next_question(
        self,
        language_code: str,
        collected_data: Dict[str, Any],
        last_response: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Generate the next question in the conversation using OpenAI
        Returns JSON with question and current data state
        """

        system_prompt = f"""
You are a WhatsApp lead collection assistant for Dream Axis Travel Solutions.

You must:
- Ask questions in the user's language: {language_code}
- Collect ONLY: full_name, phone, email, location, job_type
- Ask one question at a time
- Never store data yourself
- Never infer or guess values
- Output ONLY valid JSON
- Use null for missing values
- Be concise and professional

Current collected data: {json.dumps(collected_data, ensure_ascii=False)}
Last user response: "{last_response}"

If data is complete, return {{"complete": true, "data": collected_data}}
Otherwise, return {{"complete": false, "question": "your question here", "field": "field_name"}}
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": last_response or "Start conversation"}
                ],
                max_tokens=300,
                temperature=0.3  # Low temperature for consistent responses
            )

            content = response["choices"][0]["message"]["content"].strip()

            # Parse JSON response
            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                print(f"Invalid JSON from OpenAI: {content}")
                return None

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return None

    def extract_data_from_response(
        self,
        response: str,
        current_data: Dict[str, Any],
        language_code: str
    ) -> Dict[str, Any]:
        """
        Extract and validate data from user response
        """

        system_prompt = f"""
You are a data extraction assistant for Dream Axis Travel Solutions.

Extract information from the user's response and update the current data.
Only extract: full_name, phone, email, location, job_type
Use null for missing values.
Be precise - don't infer or guess.

Current data: {json.dumps(current_data, ensure_ascii=False)}
User response: "{response}"
Language: {language_code}

Output ONLY valid JSON with updated data fields.
"""

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt}
                ],
                max_tokens=200,
                temperature=0.1
            )

            content = response["choices"][0]["message"]["content"].strip()

            try:
                result = json.loads(content)
                return result
            except json.JSONDecodeError:
                print(f"Invalid JSON from OpenAI extraction: {content}")
                return current_data

        except Exception as e:
            print(f"Error in data extraction: {e}")
            return current_data

