"""
Voice LC Controller - Extract LC data from voice transcript
Simple approach: Frontend sends transcript, backend extracts structured data
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.agents.voice_lc_agent import get_voice_lc_agent

router = APIRouter(
    prefix="/api/v1/voice-lc",
    tags=["Voice LC Extraction"]
)


class TranscriptExtractionRequest(BaseModel):
    transcript: str = Field(
        ...,
        description="Voice conversation transcript",
        example="User: I need an LC for $50,000. Agent: What are the payment terms? User: Sight LC. Agent: Port of loading? User: Karachi to Dubai..."
    )
    provided_lc_data: Optional[dict] = Field(
        None,
        description="Already filled LC fields (optional)",
        example={
            "importer_info": {
                "applicant_name": "Ali Osaid"
            }
        }
    )


@router.post("/extract-from-transcript")
async def extract_lc_from_transcript(request: TranscriptExtractionRequest):
    """
    Extract LC form data from voice conversation transcript.

    **How it works:**
    1. Frontend records user's voice or gets transcript from VAPI
    2. Frontend sends transcript to this endpoint
    3. Backend uses Gemini to extract structured LC data
    4. Returns data in same format as OCR endpoint

    **Example Request:**
    ```json
    {
      "transcript": "I need an international LC for fifty thousand dollars. Payment terms are sight LC. Loading from Karachi port to Jebel Ali in Dubai. The product is cotton fabric.",
      "provided_lc_data": {
        "importer_info": {
          "applicant_name": "Ali Osaid"
        }
      }
    }
    ```

    **Example Response:**
    ```json
    {
      "success": true,
      "extracted_data": {
        "transaction_role": "Exporter/Supplier (Beneficiary)",
        "amount_and_payment": {
          "amount_usd": 50000,
          "payment_terms": "Sight LC"
        },
        "lc_details": {
          "lc_type": "International",
          "is_lc_issued": false
        },
        "shipment_details": {
          "shipment_type": "Port",
          "port_of_loading": "Karachi",
          "port_of_destination": "Jebel Ali",
          "product_description": "cotton fabric"
        },
        "importer_info": {
          "applicant_name": "Ali Osaid",
          "import_city": "Dubai"
        }
      },
      "confidence": "high",
      "message": "LC data extracted successfully from transcript"
    }
    ```
    """
    import traceback
    print("\n" + "="*80)
    print("🎤 VOICE TRANSCRIPT EXTRACTION REQUEST")
    print("="*80)

    try:
        print(f"📝 Transcript length: {len(request.transcript)} characters")
        print(f"📋 Provided data: {bool(request.provided_lc_data)}")

        agent = get_voice_lc_agent()

        print("🔄 Extracting LC data from transcript...")
        result = await agent.extract_lc_from_transcript(
            transcript=request.transcript,
            provided_lc_data=request.provided_lc_data or {}
        )

        if not result.get("success"):
            print(f"❌ Extraction failed: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to extract LC data")
            )

        print("✅ LC data extracted successfully")
        print(f"📊 Extracted fields: {len(result.get('extracted_data', {}))} sections")
        print("="*80 + "\n")

        return {
            "success": True,
            "extracted_data": result.get("extracted_data"),
            "confidence": result.get("confidence", "medium"),
            "message": "LC data extracted successfully from transcript"
        }

    except HTTPException:
        raise
    except Exception as e:
        print("\n" + "="*80)
        print("❌ EXTRACTION ERROR")
        print("="*80)
        print(f"Error: {str(e)}")
        print("\nTraceback:")
        print(traceback.format_exc())
        print("="*80 + "\n")

        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check for voice LC extraction"""
    return {
        "status": "healthy",
        "service": "Voice LC Extraction",
        "message": "Ready to extract LC data from voice transcripts"
    }
