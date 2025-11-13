from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.agents.prompt_agent import PromptAgent

# Version 1 Router
router = APIRouter(prefix="/api/v1/agent", tags=["AI Agent v1"])

prompt_agent = PromptAgent()

class PromptRequest(BaseModel):
    prompt: str = Field(..., description="The prompt/question to send to the AI agent", min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Controls randomness (0.0-2.0)")

@router.post("/ask")
async def ask_ai_agent(request: PromptRequest):
    """
    **LC Form Filling Agent - Understands Natural Language & SWIFT MT700 Codes**

    - Powered by: Google Gemini 1.5 Flash with SWIFT code knowledge
    - Fills LC forms from user descriptions
    - Supports both natural language AND SWIFT MT700 codes
    - Returns structured JSON matching LC form schema with enforced enums

    **Use Cases:**
    1. Natural language LC form filling
    2. SWIFT MT700 code interpretation
    3. Mixed format (natural + SWIFT codes)
    4. LC confirmation requests

    **Natural Language Examples:**
    ```json
    {
        "prompt": "I want expiry at 31 June, beneficiary will be Ali, bank is in Pakistan",
        "temperature": 0.3
    }
    ```
    ```json
    {
        "prompt": "Create LC for $50,000, sight payment, exporter in UAE, shipment from Dubai port",
        "temperature": 0.3
    }
    ```

    **SWIFT Code Examples:**
    ```json
    {
        "prompt": "31D is 250631, 59 is ABC Exports Ltd, 32B USD100000, 49 CONFIRM",
        "temperature": 0.3
    }
    ```
    ```json
    {
        "prompt": "40A IRREVOCABLE, 41A STANDARDCHARTERED BY NEGOTIATION, 72 PLEASE CONFIRM BY SWIFT",
        "temperature": 0.3
    }
    ```

    **Mixed Format:**
    ```json
    {
        "prompt": "31D: 250630, beneficiary Ali in Dubai, amount 100k USD, confirm required",
        "temperature": 0.3
    }
    ```

    **Key SWIFT Codes Supported:**
    - 31D: Expiry date and place
    - 32B: Amount (e.g., USD100000)
    - 41A: Confirming bank and method
    - 49: Confirmation instruction (CONFIRM/WITHOUT)
    - 50: Applicant/Importer
    - 59: Beneficiary/Exporter
    - 44A/44B: Loading/Destination ports
    - 72: Special instructions

    **Response Format:**
    Returns structured JSON with:
    - `lc_form`: Complete LC form with enum values
    - `interpretation`: What was understood
    - `swift_codes_used`: Which SWIFT codes were detected
    - `missing_fields`: Fields not provided by user
    """
    try:
        result = await prompt_agent.run(request.prompt)

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Prompt processing failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
