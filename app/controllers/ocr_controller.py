from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.ocr_agent import OCRAgent

# Version 1 Router
router = APIRouter(prefix="/api/v1/ocr", tags=["OCR v1"])

ocr_agent = OCRAgent()

@router.post("/extract-lc-form")
async def extract_letter_of_credit_form(file: UploadFile = File(...)):
    """
    **Extract and map Letter of Credit (LC) form data with intelligent field matching**

    - Supports: PDF format only
    - Intelligently maps fields even if terminology differs
    - Handles synonyms: buyer/importer/applicant, seller/exporter/beneficiary, etc.
    - Returns: Structured JSON matching LC form schema with enforced enums
    - Use case: LC form processing, trade finance documents

    **Extracted Fields:**
    - Transaction Role (Exporter/Importer)
    - Amount & Payment Terms (with enum enforcement)
    - LC Details (Type, Issuing Bank, Dates)
    - LC Confirmation Details
    - Shipment Information
    - Importer/Exporter Information
    - Confirmation Charges
    - Bidding Deadline

    **Enum Fields (EXACT values only):**
    - transaction_role: "Exporter/Supplier (Beneficiary)" | "Importer (Applicant)"
    - payment_terms: "Sight LC" | "Usance LC" | "Deferred LC" | "UPAS LC"
    - lc_type: "Local (Pakistan)" | "International"
    - shipment_type: "Port" | "Airport" | "Land"
    - charges_account: "Exporter (Beneficiary)" | "Importer (Applicant)"
    - expected_banks: "All_Banks" (always)
    """
    try:
        # Validate file type - PDF only
        if file.content_type != 'application/pdf':
            raise HTTPException(
                status_code=400,
                detail=f"Only PDF files are supported. Received: {file.content_type}"
            )

        # Read file bytes
        file_bytes = await file.read()

        # Extract LC form data
        result = await ocr_agent.extract_lc_form(file_bytes)

        if not result["success"]:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "LC form extraction failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
