import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv
from app.utils.lc_schema import get_extraction_prompt

load_dotenv()

class OCRAgent:
    def __init__(self):
        """Initialize the OCR agent with Gemini Vision for PDF processing"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')

    def _clean_json_response(self, text: str) -> dict:
        """Clean and parse JSON from model response"""
        try:
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            text = text.strip()

            # Try to parse JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return {"raw_text": text, "parsed": False}

    async def extract_lc_form(self, file_bytes: bytes) -> dict:
        """
        Extract Letter of Credit form data with intelligent field mapping and enum enforcement

        Args:
            file_bytes: PDF file bytes of LC form

        Returns:
            dict: Structured LC form data with enforced enum values
        """
        try:
            # Get specialized LC extraction prompt with enforced schema and enums
            extraction_prompt = get_extraction_prompt()

            # Create file part for PDF
            file_part = {
                "mime_type": "application/pdf",
                "data": file_bytes
            }

            # Generate content with specialized prompt
            response = self.model.generate_content([extraction_prompt, file_part])

            # Clean and parse JSON response
            parsed_data = self._clean_json_response(response.text)

            return {
                "success": True,
                "lc_data": parsed_data,
                "mime_type": "application/pdf",
                "model": "gemini-2.5-pro",
                "schema_version": "1.0"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
