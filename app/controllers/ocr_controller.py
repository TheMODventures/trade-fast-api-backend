from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.ocr_agent import OCRAgent
from app.agents.sanctions_agent import SanctionsAgent

# Version 1 Router
router = APIRouter(prefix="/api/v1/ocr", tags=["OCR v1"])

ocr_agent = OCRAgent()
sanctions_agent = SanctionsAgent()

@router.post("/extract-lc-form")
async def extract_letter_of_credit_form(file: UploadFile = File(...)):
    """
    **Extract and map Letter of Credit (LC) form data with automatic sanctions compliance check**

    This endpoint now includes:
    1. **OCR Extraction** - Extracts LC data from PDF using Gemini Vision
    2. **Sanctions Check** - Automatically runs after extraction to check trade sanctions
    3. **Compliance Status** - Returns both extraction results and compliance verification

    - Supports: PDF format only
    - Intelligently maps fields even if terminology differs
    - Handles synonyms: buyer/importer/applicant, seller/exporter/beneficiary, etc.
    - Returns: Structured JSON with LC data + sanctions compliance status
    - Use case: LC form processing with automatic compliance verification

    **Extracted Fields:**
    - Transaction Role (Exporter/Importer)
    - Amount & Payment Terms (with enum enforcement)
    - LC Details (Type, Issuing Bank, Dates)
    - LC Confirmation Details
    - Shipment Information
    - Importer/Exporter Information
    - Confirmation Charges
    - Bidding Deadline

    **Sanctions Compliance Check (Automatic - Offline Database):**
    - Country sanctions (OFAC, UN, EU) - hardcoded database
    - Port restrictions - high-risk ports
    - Product/commodity controls - dual-use goods detection
    - Fast, reliable offline checking (no API calls required)

    **Response includes:**
    - success: Whether extraction succeeded
    - lc_data: Extracted LC information
    - compliance: Sanctions check results
    - final_status: "APPROVED" | "DENIED" | "REVIEW_REQUIRED" | "PENDING"
    - risk_assessment: "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"

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

        # Step 1: Extract LC form data using OCR
        file_bytes = await file.read()
        extraction_result = await ocr_agent.extract_lc_form(file_bytes)

        if not extraction_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=extraction_result.get("error", "LC form extraction failed")
            )

        # Step 2: Automatically run sanctions compliance check
        lc_data = extraction_result.get("lc_data")
        sanctions_result = await sanctions_agent.check_lc_compliance(lc_data)

        # Step 3: Determine final status
        if sanctions_result.get("blocked"):
            final_status = "DENIED"
        elif sanctions_result.get("risk_level") in ["HIGH", "CRITICAL"] and not sanctions_result.get("compliant"):
            final_status = "REVIEW_REQUIRED"
        elif sanctions_result.get("compliant"):
            final_status = "APPROVED"
        else:
            final_status = "PENDING"

        # Step 4: Return combined results (extraction + compliance)
        return {
            "success": True,
            "lc_data": lc_data,
            "compliance": sanctions_result,
            "final_status": final_status,
            "risk_assessment": sanctions_result.get("risk_level"),
            "recommendations": sanctions_result.get("recommendations"),
            "processed_at": sanctions_result.get("checked_at"),
            # Include full extraction metadata
            "extraction_metadata": {
                "mime_type": extraction_result.get("mime_type"),
                "model": extraction_result.get("model"),
                "schema_version": extraction_result.get("schema_version")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        # Check if it's a rate limit error
        error_str = str(e).lower()
        if "429" in error_str or "quota" in error_str or "exhausted" in error_str:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "API rate limit exceeded",
                    "message": "Gemini API quota has been exhausted. Please wait 60 seconds and try again.",
                    "suggestions": [
                        "Wait 60 seconds before retrying",
                        "Check your API quota at https://aistudio.google.com",
                        "Consider upgrading your Gemini API tier for higher limits"
                    ],
                    "original_error": str(e)
                }
            )
        raise HTTPException(status_code=500, detail=str(e))
