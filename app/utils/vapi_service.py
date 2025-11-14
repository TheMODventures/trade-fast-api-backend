"""
VAPI Service - Handles all VAPI API interactions
"""
import os
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class VAPIService:
    """Service class for interacting with VAPI API"""

    def __init__(self):
        self.api_key = os.getenv("VAPI_API_KEY")
        self.base_url = "https://api.vapi.ai"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        if not self.api_key:
            raise ValueError("VAPI_API_KEY not found in environment variables")

    async def create_assistant(self, assistant_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new VAPI assistant

        Args:
            assistant_config: Assistant configuration dictionary

        Returns:
            Created assistant details
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/assistant",
                headers=self.headers,
                json=assistant_config,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Get assistant details by ID

        Args:
            assistant_id: The assistant ID

        Returns:
            Assistant details
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def update_assistant(
        self,
        assistant_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing assistant

        Args:
            assistant_id: The assistant ID
            updates: Dictionary of fields to update

        Returns:
            Updated assistant details
        """
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                json=updates,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def delete_assistant(self, assistant_id: str) -> Dict[str, Any]:
        """
        Delete an assistant

        Args:
            assistant_id: The assistant ID

        Returns:
            Deletion confirmation
        """
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.base_url}/assistant/{assistant_id}",
                headers=self.headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def create_phone_call(
        self,
        phone_number: str,
        assistant_id: Optional[str] = None,
        assistant_config: Optional[Dict[str, Any]] = None,
        customer_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create an outbound phone call

        Args:
            phone_number: Phone number to call (E.164 format recommended: +1234567890)
            assistant_id: ID of pre-created assistant (if using existing)
            assistant_config: Inline assistant configuration (if creating on-the-fly)
            customer_data: Additional data to pass to the assistant

        Returns:
            Call details including call ID and status
        """
        call_payload: Dict[str, Any] = {
            "phoneNumberId": os.getenv("VAPI_PHONE_NUMBER_ID"),  # Your VAPI phone number
            "customer": {
                "number": phone_number
            }
        }

        # Use either assistant_id or assistant_config
        if assistant_id:
            call_payload["assistantId"] = assistant_id
        elif assistant_config:
            call_payload["assistant"] = assistant_config
        else:
            raise ValueError("Either assistant_id or assistant_config must be provided")

        # Add custom data if provided
        if customer_data:
            call_payload["customer"]["data"] = customer_data

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/call/phone",
                headers=self.headers,
                json=call_payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()

    async def get_call_transcript(self, call_id: str) -> Dict[str, Any]:
        """
        Get transcript for a completed call

        Args:
            call_id: The call ID

        Returns:
            Call transcript
        """
        call_details = await self.get_call(call_id)
        return {
            "call_id": call_id,
            "transcript": call_details.get("transcript", []),
            "messages": call_details.get("messages", [])
        }

    async def get_call_recording(self, call_id: str) -> Optional[str]:
        """
        Get recording URL for a completed call

        Args:
            call_id: The call ID

        Returns:
            Recording URL if available
        """
        call_details = await self.get_call(call_id)
        return call_details.get("recordingUrl")

    def validate_webhook_signature(
        self,
        payload: str,
        signature: str,
        secret: Optional[str] = None
    ) -> bool:
        """
        Validate webhook signature from VAPI

        Args:
            payload: Raw request body
            signature: Signature from request headers
            secret: Webhook secret (defaults to env variable)

        Returns:
            True if signature is valid
        """
        import hmac
        import hashlib

        if secret is None:
            secret = os.getenv("VAPI_WEBHOOK_SECRET", "")

        expected_signature = hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected_signature, signature)


# Singleton instance
_vapi_service_instance: Optional[VAPIService] = None


def get_vapi_service() -> VAPIService:
    """Get or create VAPIService singleton instance"""
    global _vapi_service_instance
    if _vapi_service_instance is None:
        _vapi_service_instance = VAPIService()
    return _vapi_service_instance
