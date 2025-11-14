"""
Voice LC Agent - Extract LC data from voice transcripts using Gemini
"""
import json
import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI


class VoiceLCAgent:
    """Agent for extracting LC data from voice conversation transcripts"""

    def __init__(self):
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1
        )

    async def extract_lc_from_transcript(
        self,
        transcript: str,
        provided_lc_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured LC data from voice conversation transcript

        Args:
            transcript: Voice conversation text
            provided_lc_data: Already filled LC fields (optional)

        Returns:
            Extracted LC data in structured format
        """
        try:
            if not transcript or len(transcript.strip()) < 10:
                return {
                    "success": False,
                    "error": "Transcript is too short or empty",
                    "extracted_data": {}
                }

            # Build context about already provided data
            provided_context = ""
            if provided_lc_data:
                provided_context = f"\n\nALREADY PROVIDED DATA (from web form):\n{json.dumps(provided_lc_data, indent=2)}"

            # Create extraction prompt with exact field requirements
            extraction_prompt = f"""You are an expert at extracting Letter of Credit (LC) information from voice conversations.

{provided_context}

VOICE CONVERSATION TRANSCRIPT:
{transcript}

TASK:
Extract ALL LC information from this conversation and return in the EXACT JSON structure below.

CRITICAL FIELD NAMING RULES:
- Use "amount_usd" (NOT "amount")
- Use "is_lc_issued" (NOT "is_issued")
- Use "expected_banks" (NOT "issuing_bank")
- Use "import_city" (NOT "city_of_import")
- Use "export_city" (NOT "city_of_export")

EXTRACTION RULES:

1. **Amounts**: Convert to numbers
   - "one million dollars" → 1000000
   - "$1M" → 1000000
   - "fifty thousand" → 50000

2. **Payment Terms** (use EXACT values):
   - "Sight LC" | "Usance LC" | "Deferred LC" | "Red Clause LC" | "Back to Back LC" | "Transferable LC" | "Revolving LC"

3. **LC Type** (use EXACT values):
   - "International" or "Local (Pakistan)"

4. **Shipment Type** (use EXACT values):
   - "Port to Port" | "Air" | "Rail" | "Road"

5. **Booleans**:
   - "yes it's issued" → true
   - "not issued" → false

6. **Dates**: Convert to YYYY-MM-DD format

7. **Missing Data**: Return null (not empty string, not omit)

REQUIRED JSON STRUCTURE:
{{
  "transaction_role": "Exporter/Supplier (Beneficiary)" | "Importer (Applicant)" | null,
  "amount_and_payment": {{
    "amount_usd": number | null,
    "payment_terms": "Sight LC" | "Usance LC" | "Deferred LC" | null
  }},
  "lc_details": {{
    "lc_type": "International" | "Local (Pakistan)" | null,
    "is_lc_issued": true | false | null,
    "expected_banks": "All_Banks" | "Bank Name" | null,
    "issue_date": "YYYY-MM-DD" | null,
    "expected_shipment_date": "YYYY-MM-DD" | null,
    "expected_confirmation_date": "YYYY-MM-DD" | null
  }},
  "shipment_details": {{
    "shipment_type": "Port to Port" | "Air" | "Rail" | "Road" | null,
    "loading_port": "string" | null,
    "destination_port": "string" | null,
    "product_description": "string" | null
  }},
  "importer_info": {{
    "applicant_name": "string" | null,
    "import_city": "string" | null
  }},
  "exporter_info": {{
    "beneficiary_name": "string" | null,
    "export_city": "string" | null,
    "beneficiary_country": "string" | null
  }},
  "confirmation_charges": {{
    "charges_account": "Beneficiary" | "Applicant" | null,
    "expected_charges": number | null,
    "pricing_per_annum": number | null
  }},
  "bidding_deadline": {{
    "bid_deadline": "YYYY-MM-DD" | null
  }}
}}

Return ONLY the JSON object. No markdown, no code blocks, no explanation."""

            # Use Gemini to extract structured data
            print("🤖 Calling Gemini for data extraction...")
            response = await self.gemini_llm.ainvoke(extraction_prompt)
            extracted_text = response.content

            print(f"📄 Gemini response length: {len(extracted_text)} characters")

            # Parse JSON from response
            extracted_data = self._parse_json_from_response(extracted_text)

            # Merge with provided data
            if provided_lc_data:
                extracted_data = self._merge_lc_data(provided_lc_data, extracted_data)

            # Determine confidence based on how much data was extracted
            confidence = self._calculate_confidence(extracted_data)

            return {
                "success": True,
                "extracted_data": extracted_data,
                "confidence": confidence
            }

        except Exception as e:
            print(f"❌ Error in extract_lc_from_transcript: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "extracted_data": {}
            }

    def _parse_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response (handles markdown code blocks)"""
        try:
            # Try direct parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re

            # Try ```json ... ```
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            print(f"⚠️ Could not parse JSON from response")
            # Return empty structure
            return {}

    def _merge_lc_data(
        self,
        provided_data: Dict[str, Any],
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge provided data with extracted data"""
        import copy

        # Start with provided data
        merged = copy.deepcopy(provided_data)

        # Add/override with extracted data
        for section, fields in extracted_data.items():
            if section not in merged:
                merged[section] = {}

            if isinstance(fields, dict):
                for field, value in fields.items():
                    # Add if not present or override if extracted value is not None
                    if field not in merged[section] or (value is not None and merged[section][field] is None):
                        merged[section][field] = value

        return merged

    def _calculate_confidence(self, extracted_data: Dict[str, Any]) -> str:
        """Calculate confidence level based on extracted data completeness"""
        total_fields = 0
        filled_fields = 0

        for section, fields in extracted_data.items():
            if isinstance(fields, dict):
                for field, value in fields.items():
                    total_fields += 1
                    if value is not None:
                        filled_fields += 1

        if total_fields == 0:
            return "low"

        fill_ratio = filled_fields / total_fields

        if fill_ratio >= 0.7:
            return "high"
        elif fill_ratio >= 0.4:
            return "medium"
        else:
            return "low"


# Singleton instance
_voice_lc_agent_instance: Optional[VoiceLCAgent] = None


def get_voice_lc_agent() -> VoiceLCAgent:
    """Get or create VoiceLCAgent singleton instance"""
    global _voice_lc_agent_instance
    if _voice_lc_agent_instance is None:
        _voice_lc_agent_instance = VoiceLCAgent()
    return _voice_lc_agent_instance
