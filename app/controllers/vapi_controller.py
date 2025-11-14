"""
VAPI Controller - REST API endpoints for LC form completion via WEB voice calls
This handles voice conversations that happen IN THE BROWSER on the LC form page
"""
from fastapi import APIRouter, HTTPException, Request, Header
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.agents.vapi_agent import get_vapi_agent
from app.utils.vapi_service import get_vapi_service
from app.utils.vapi_lc_assistant import get_lc_completion_assistant_config

router = APIRouter(
    prefix="/api/v1/vapi",
    tags=["VAPI - LC Voice Completion"]
)


# ============== Request/Response Models ==============

class CreateLCAssistantRequest(BaseModel):
    provided_lc_data: Dict[str, Any] = Field(
        ...,
        description="LC form fields already filled from frontend",
        example={
            "transaction_role": "Exporter/Supplier (Beneficiary)",
            "amount_and_payment": {
                "amount_usd": 50000,
                "payment_terms": "Sight LC"
            },
            "importer_info": {
                "applicant_name": "Ali Osaid"
            }
        }
    )
    company_name: str = Field(
        default="Trade Origin",
        description="Company name for greeting"
    )


class EndCallRequest(BaseModel):
    call_id: str = Field(..., description="The call ID to end")


# ============== Endpoints ==============

@router.post("/lc/create-assistant")
async def create_lc_assistant(body: CreateLCAssistantRequest):
    """
    Create a VAPI assistant configuration for LC form completion.

    **How the web integration works:**
    1. User fills 4-5 fields on LC form in your React app
    2. User clicks "Call Agent to Fill Form" button
    3. Frontend calls this endpoint with filled fields
    4. Backend returns assistant configuration
    5. Frontend uses VAPI SDK to start voice call in browser
    6. User talks with AI agent to complete remaining fields
    7. When call ends, frontend calls `/lc/get-complete-data/{call_id}` to get all data

    **Example Request:**
    ```json
    {
      "provided_lc_data": {
        "transaction_role": "Exporter/Supplier (Beneficiary)",
        "amount_and_payment": {
          "amount_usd": 50000
        },
        "importer_info": {
          "applicant_name": "Ali Osaid"
        }
      }
    }
    ```

    **Response:**
    Returns assistant configuration to use with VAPI SDK in frontend.
    The frontend will use this to initiate the web call.
    """
    import traceback
    print("\n" + "="*80)
    print("🔵 CREATE LC ASSISTANT REQUEST RECEIVED")
    print("="*80)

    try:
        print(f"📥 Request Data:")
        print(f"  - Company Name: {body.company_name}")
        print(f"  - Provided LC Data: {body.provided_lc_data}")
        print(f"  - Number of sections: {len(body.provided_lc_data)}")

        print("\n🔄 Generating assistant configuration...")
        # Generate assistant configuration
        assistant_config = get_lc_completion_assistant_config(
            provided_fields=body.provided_lc_data,
            company_name=body.company_name
        )
        print("✅ Assistant configuration generated")

        # Add webhook URL (your backend webhook endpoint)
        # You can set BACKEND_URL in .env or it will use localhost
        import os
        backend_url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
        webhook_url = f"{backend_url}/api/v1/vapi/webhook"
        print(f"\n🔗 Setting webhook URL: {webhook_url}")
        assistant_config["serverUrl"] = webhook_url

        # Store provided data in metadata
        assistant_config["metadata"] = {
            "provided_lc_data": body.provided_lc_data,
            "purpose": "lc_form_completion"
        }
        print("✅ Metadata added to assistant config")

        print("\n✅ SUCCESS - Returning assistant configuration")
        print("="*80 + "\n")

        return {
            "success": True,
            "assistant_config": assistant_config,
            "message": "Assistant configuration created successfully"
        }

    except Exception as e:
        print("\n" + "="*80)
        print("❌ ERROR IN CREATE LC ASSISTANT")
        print("="*80)
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print("\nFull Traceback:")
        print(traceback.format_exc())
        print("="*80 + "\n")

        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/lc/call-status/{call_id}")
async def get_call_status(call_id: str):
    """
    Get the current status of an LC completion call.

    **Call Statuses:**
    - `in-progress`: Call is active, conversation ongoing
    - `ended`: Call has ended

    Frontend can poll this endpoint to know when the call is complete.
    """
    agent = get_vapi_agent()

    try:
        result = await agent.get_call_status(call_id)

        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("message"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/lc/end-call")
async def end_call(request: EndCallRequest):
    """
    End an ongoing LC completion call.

    Frontend can call this if user wants to end the call manually.
    """
    agent = get_vapi_agent()

    try:
        result = await agent.end_call(request.call_id)

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lc/get-complete-data/{call_id}")
async def get_complete_lc_data(call_id: str):
    """
    Get the complete LC form data after call completion.

    **🎯 THIS IS THE MAIN ENDPOINT** - Frontend calls this after the voice call ends.

    **Returns:**
    - `complete_lc_data`: Merged data (provided + collected from voice call)
    - `provided_fields`: What was originally filled in the form
    - `collected_fields`: What was collected via voice conversation
    - `transcript`: Full conversation transcript

    **When to call:**
    - After VAPI SDK triggers "call-end" event
    - Or after polling `/lc/call-status` shows status "ended"

    **Example Response:**
    ```json
    {
      "success": true,
      "call_id": "abc123",
      "complete_lc_data": {
        "transaction_role": "Exporter/Supplier (Beneficiary)",
        "amount_and_payment": {
          "amount_usd": 50000,
          "payment_terms": "Sight LC"
        },
        "lc_details": {
          "lc_type": "International",
          "is_lc_issued": false
        },
        "importer_info": {
          "applicant_name": "Ali Osaid",
          "city_of_import": "Dubai"
        },
        "shipment_details": {
          "shipment_type": "Port",
          "port_of_loading": "Karachi"
        }
      }
    }
    ```

    **Frontend Integration:**
    ```javascript
    // After call ends
    const response = await fetch(`/vapi/lc/get-complete-data/${callId}`);
    const data = await response.json();

    // Update your LC form with complete data
    setLCFormData(data.complete_lc_data);
    ```
    """
    agent = get_vapi_agent()

    try:
        result = await agent.get_complete_lc_data(call_id)

        if not result.get("success"):
            raise HTTPException(status_code=404, detail=result.get("message"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lc/transcript/{call_id}")
async def get_transcript(call_id: str):
    """
    Get only the conversation transcript.

    Returns raw transcript without data extraction.
    """
    vapi_service = get_vapi_service()

    try:
        result = await vapi_service.get_call_transcript(call_id)
        return {
            "success": True,
            "call_id": call_id,
            "transcript": result.get("transcript"),
            "messages": result.get("messages")
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/lc/recording/{call_id}")
async def get_recording(call_id: str):
    """
    Get the recording URL for a completed call.

    Returns URL to download/stream the call recording.
    """
    vapi_service = get_vapi_service()

    try:
        recording_url = await vapi_service.get_call_recording(call_id)

        if not recording_url:
            raise HTTPException(
                status_code=404,
                detail="Recording not available for this call"
            )

        return {
            "success": True,
            "call_id": call_id,
            "recording_url": recording_url
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def vapi_webhook(
    request: Request,
    x_vapi_signature: Optional[str] = Header(None, alias="x-vapi-signature")
):
    """
    Webhook endpoint to receive events from VAPI.

    **Events:**
    - `call.started`: When call begins
    - `call.ended`: When call ends
    - `transcript.update`: Real-time transcript updates

    **Security:**
    Validates webhook signatures using VAPI_WEBHOOK_SECRET env variable.

    **Note:** Your frontend can also listen to these events via VAPI SDK,
    so this webhook is optional but recommended for backend processing.
    """
    agent = get_vapi_agent()
    vapi_service = get_vapi_service()

    try:
        # Get raw body for signature validation
        body = await request.body()
        body_str = body.decode("utf-8")

        # Validate signature if provided
        if x_vapi_signature:
            is_valid = vapi_service.validate_webhook_signature(
                payload=body_str,
                signature=x_vapi_signature
            )
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid webhook signature")

        # Parse JSON
        event_data = await request.json()

        # Extract event type
        event_type = event_data.get("type") or event_data.get("event")

        if not event_type:
            raise HTTPException(status_code=400, detail="Event type not found")

        # Process the event
        result = await agent.process_webhook_event(event_type, event_data)

        return {
            "success": True,
            "event_type": event_type,
            "processed": result
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        # Return 200 to prevent VAPI retries
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/health")
async def health_check():
    """
    Health check for VAPI integration.
    """
    try:
        vapi_service = get_vapi_service()
        if not vapi_service.api_key:
            return {
                "status": "error",
                "message": "VAPI_API_KEY not configured"
            }

        return {
            "status": "healthy",
            "service": "VAPI LC Form Completion",
            "message": "VAPI integration configured"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
