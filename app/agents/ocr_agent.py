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

    async def detect_hs_code(self, product_description: str) -> dict:
        """
        Detect HS Code (Harmonized System Code) for a product description

        Args:
            product_description: Description of the product/goods

        Returns:
            dict: HS code information including code, description, and confidence
        """
        if not product_description or len(product_description.strip()) == 0:
            return {
                "hs_code": None,
                "hs_description": None,
                "confidence": "low",
                "reason": "No product description provided"
            }

        try:
            hs_prompt = f"""You are an expert in HS Codes (Harmonized System Codes) used in international trade.

Product Description: "{product_description}"

Your task:
1. Analyze the product description
2. Determine the most appropriate HS Code (6-digit minimum, 8-digit if possible)
3. Provide the official HS code description
4. Assess your confidence level

HS Code Format:
- First 2 digits: Chapter (e.g., 84 = Machinery)
- Next 2 digits: Heading (e.g., 8471 = Computers)
- Next 2 digits: Subheading (e.g., 847130 = Portable computers)
- Optional 2 more digits: National level (e.g., 84713090)

Common HS Code Examples:
- Electronics/Computers: Chapter 84, 85
- Textiles: Chapter 50-63
- Machinery: Chapter 84
- Vehicles: Chapter 87
- Chemicals: Chapter 28-38
- Food products: Chapter 02-24

Return your response in JSON format:
{{
  "hs_code": "XXXXXX",
  "hs_description": "Official HS code description",
  "chapter": "Chapter name",
  "confidence": "high" or "medium" or "low",
  "reasoning": "Why this HS code was selected",
  "alternative_codes": ["code1", "code2"] // if applicable
}}

Be specific and accurate. If uncertain, indicate "medium" or "low" confidence."""

            # Query Gemini for HS code detection
            response = self.model.generate_content(hs_prompt)

            # Parse response
            result = self._clean_json_response(response.text)

            # Validate result
            if not isinstance(result, dict) or "hs_code" not in result:
                # Fallback parsing if JSON not properly formatted
                return {
                    "hs_code": None,
                    "hs_description": "Unable to determine HS code",
                    "confidence": "low",
                    "reason": "Could not parse HS code response",
                    "raw_response": response.text[:500]
                }

            return result

        except Exception as e:
            return {
                "hs_code": None,
                "hs_description": None,
                "confidence": "low",
                "reason": f"Error detecting HS code: {str(e)}"
            }

    async def extract_lc_form(self, file_bytes: bytes) -> dict:
        """
        Extract Letter of Credit form data with intelligent field mapping, enum enforcement, and HS code detection

        Args:
            file_bytes: PDF file bytes of LC form

        Returns:
            dict: Structured LC form data with enforced enum values and HS code
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

            # Detect HS Code based on product description
            product_description = parsed_data.get("shipment_details", {}).get("product_description")
            if product_description:
                hs_code_info = await self.detect_hs_code(product_description)

                # Add HS code to shipment details
                if "shipment_details" not in parsed_data:
                    parsed_data["shipment_details"] = {}

                parsed_data["shipment_details"]["hs_code"] = hs_code_info.get("hs_code")
                parsed_data["shipment_details"]["hs_description"] = hs_code_info.get("hs_description")
                parsed_data["shipment_details"]["hs_confidence"] = hs_code_info.get("confidence")
                parsed_data["shipment_details"]["hs_chapter"] = hs_code_info.get("chapter")

                # Store full HS code info for reference
                parsed_data["hs_code_analysis"] = hs_code_info

            return {
                "success": True,
                "lc_data": parsed_data,
                "mime_type": "application/pdf",
                "model": "gemini-2.5-pro",
                "schema_version": "1.1",
                "features": ["ocr_extraction", "hs_code_detection"]
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
