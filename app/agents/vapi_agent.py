"""
VAPI Agent - Business logic for voice call LC form completion
"""
import json
import os
from typing import Dict, Any, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from app.utils.vapi_service import get_vapi_service
from app.utils.vapi_lc_assistant import (
    get_lc_completion_assistant_config,
    merge_collected_data
)
from app.utils.lc_schema import get_extraction_prompt


class VAPIAgent:
    """Agent for handling VAPI voice call operations for LC form completion"""

    def __init__(self):
        self.vapi_service = get_vapi_service()
        self.gemini_llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.1
        )

    async def initiate_lc_completion_call(
        self,
        phone_number: str,
        provided_lc_data: Dict[str, Any],
        webhook_url: Optional[str] = None,
        company_name: str = "Trade Finance Solutions"
    ) -> Dict[str, Any]:
        """
        Initiate an outbound call to complete LC form fields

        Args:
            phone_number: Phone number to call (E.164 format: +1234567890)
            provided_lc_data: LC form fields already filled from frontend
            webhook_url: URL to receive webhook events
            company_name: Company name for assistant greeting

        Returns:
            Call initiation result with call_id
        """
        try:
            # Generate assistant configuration based on what's already provided
            assistant_config = get_lc_completion_assistant_config(
                provided_fields=provided_lc_data,
                company_name=company_name
            )

            # Add webhook URL if provided
            if webhook_url:
                assistant_config["serverUrl"] = webhook_url

            # Store the provided data in assistant metadata for later retrieval
            assistant_config["metadata"] = {
                "provided_lc_data": provided_lc_data,
                "purpose": "lc_form_completion"
            }

            # Initiate the call with inline assistant configuration
            call_result = await self.vapi_service.create_phone_call(
                phone_number=phone_number,
                assistant_config=assistant_config,
                customer_data={"lc_data": provided_lc_data}
            )

            return {
                "success": True,
                "call_id": call_result.get("id"),
                "status": call_result.get("status"),
                "phone_number": phone_number,
                "provided_fields_count": self._count_provided_fields(provided_lc_data),
                "message": "LC completion call initiated successfully",
                "details": call_result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to initiate LC completion call"
            }

    async def get_call_status(self, call_id: str) -> Dict[str, Any]:
        """
        Get current status of a call

        Args:
            call_id: The call ID

        Returns:
            Call status information
        """
        try:
            call_details = await self.vapi_service.get_call(call_id)

            return {
                "success": True,
                "call_id": call_id,
                "status": call_details.get("status"),
                "started_at": call_details.get("startedAt"),
                "ended_at": call_details.get("endedAt"),
                "duration": call_details.get("duration"),
                "details": call_details
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get call status"
            }

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """
        End an ongoing call

        Args:
            call_id: The call ID

        Returns:
            Call end confirmation
        """
        try:
            result = await self.vapi_service.end_call(call_id)

            return {
                "success": True,
                "call_id": call_id,
                "message": "Call ended successfully",
                "details": result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to end call"
            }

    async def extract_lc_data_from_transcript(
        self,
        transcript: list,
        messages: Optional[list] = None,
        provided_lc_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured LC data from call transcript using Gemini

        Args:
            transcript: Call transcript
            messages: Call messages
            provided_lc_data: Fields that were already provided (for context)

        Returns:
            Extracted LC data from the conversation
        """
        try:
            # Build transcript text from messages
            transcript_text = self._format_transcript(transcript, messages)

            if not transcript_text:
                return {
                    "success": False,
                    "error": "No transcript available",
                    "collected_data": {}
                }

            # Create extraction prompt
            extraction_prompt = f"""{get_extraction_prompt()}

CONTEXT:
The customer was having a voice conversation to complete their LC form. Some fields were already provided before the call:

Already Provided:
{json.dumps(provided_lc_data or {}, indent=2)}

TRANSCRIPT OF THE VOICE CONVERSATION:
{transcript_text}

TASK:
Extract ONLY the NEW information that was collected during this voice conversation. Do NOT include the information that was already provided before the call.

Return a JSON object with ONLY the fields that were discussed and collected during this call."""

            # Use Gemini to extract structured data
            response = await self.gemini_llm.ainvoke(extraction_prompt)
            extracted_text = response.content

            # Parse JSON from response
            collected_data = self._parse_json_from_response(extracted_text)

            return {
                "success": True,
                "collected_data": collected_data,
                "transcript_text": transcript_text
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "collected_data": {}
            }

    async def get_complete_lc_data(
        self,
        call_id: str
    ) -> Dict[str, Any]:
        """
        Get complete LC data by merging provided fields with collected fields from call

        Args:
            call_id: The call ID

        Returns:
            Complete LC form data (provided + collected)
        """
        try:
            # Get call details to retrieve metadata
            call_details = await self.vapi_service.get_call(call_id)

            # Extract provided data from metadata
            metadata = call_details.get("assistant", {}).get("metadata", {})
            provided_lc_data = metadata.get("provided_lc_data", {})

            # Get transcript
            transcript_data = await self.vapi_service.get_call_transcript(call_id)

            # Extract collected data from transcript
            extraction_result = await self.extract_lc_data_from_transcript(
                transcript=transcript_data.get("transcript", []),
                messages=transcript_data.get("messages", []),
                provided_lc_data=provided_lc_data
            )

            if not extraction_result.get("success"):
                return {
                    "success": False,
                    "error": extraction_result.get("error"),
                    "message": "Failed to extract LC data from transcript"
                }

            # Merge provided and collected data
            collected_data = extraction_result.get("collected_data", {})
            complete_lc_data = merge_collected_data(provided_lc_data, collected_data)

            return {
                "success": True,
                "call_id": call_id,
                "complete_lc_data": complete_lc_data,
                "provided_fields": provided_lc_data,
                "collected_fields": collected_data,
                "transcript": transcript_data.get("transcript"),
                "message": "LC data successfully merged"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get complete LC data"
            }

    async def process_webhook_event(
        self,
        event_type: str,
        event_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process webhook events from VAPI

        Args:
            event_type: Type of webhook event
            event_data: Event data payload

        Returns:
            Processing result
        """
        call_id = event_data.get("call", {}).get("id")

        # Handle different event types
        if event_type == "call.started":
            return {
                "success": True,
                "action": "call_started",
                "call_id": call_id,
                "message": "LC completion call started"
            }

        elif event_type == "call.ended":
            # Extract and merge LC data when call ends
            lc_data_result = await self.get_complete_lc_data(call_id)

            return {
                "success": True,
                "action": "call_ended",
                "call_id": call_id,
                "lc_data": lc_data_result.get("complete_lc_data"),
                "message": "Call ended and LC data extracted"
            }

        elif event_type == "transcript.update":
            return {
                "success": True,
                "action": "transcript_update",
                "call_id": call_id,
                "message": "Transcript update received"
            }

        else:
            return {
                "success": True,
                "action": "unknown_event",
                "event_type": event_type,
                "message": f"Received unknown event type: {event_type}"
            }

    async def list_recent_calls(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        List recent LC completion calls

        Args:
            limit: Maximum number of calls to return

        Returns:
            List of recent calls
        """
        try:
            calls = await self.vapi_service.list_calls(limit)

            return {
                "success": True,
                "calls": calls,
                "count": len(calls) if isinstance(calls, list) else 0
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to list calls"
            }

    def _count_provided_fields(self, data: Dict[str, Any]) -> int:
        """Count number of fields provided"""
        count = 0
        for section, fields in data.items():
            if isinstance(fields, dict):
                count += sum(1 for v in fields.values() if v is not None)
        return count

    def _format_transcript(self, transcript: list, messages: Optional[list]) -> str:
        """Format transcript into readable text"""
        lines = []

        # Try to format from messages first (more structured)
        if messages:
            for msg in messages:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                lines.append(f"{role.upper()}: {content}")

        # Fallback to transcript list
        elif transcript:
            for item in transcript:
                if isinstance(item, dict):
                    speaker = item.get("speaker", "unknown")
                    text = item.get("text", "")
                    lines.append(f"{speaker}: {text}")
                elif isinstance(item, str):
                    lines.append(item)

        return "\n".join(lines)

    def _parse_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response (handles markdown code blocks)"""
        try:
            # Try direct parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))

            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            # Return empty if can't parse
            return {}


# Singleton instance
_vapi_agent_instance: Optional[VAPIAgent] = None


def get_vapi_agent() -> VAPIAgent:
    """Get or create VAPIAgent singleton instance"""
    global _vapi_agent_instance
    if _vapi_agent_instance is None:
        _vapi_agent_instance = VAPIAgent()
    return _vapi_agent_instance
