"""
SWIFT MT700 Code Reference for Letter of Credit
"""

SWIFT_MT700_CODES = {
    "27": {
        "name": "Sequence of Total",
        "description": "Indicates message sequence number",
        "example": "1/1"
    },
    "40A": {
        "name": "Form of Documentary Credit",
        "description": "Type of LC",
        "options": ["IRREVOCABLE", "REVOCABLE"],
        "maps_to": "lc_type"
    },
    "20": {
        "name": "Documentary Credit Number",
        "description": "LC reference number",
        "example": "LC2025-00123",
        "maps_to": "lc_number"
    },
    "31C": {
        "name": "Date of Issue",
        "description": "LC issue date (YYMMDD)",
        "format": "YYMMDD",
        "example": "250101",
        "maps_to": "lc_details.lc_issuing_date"
    },
    "31D": {
        "name": "Date and Place of Expiry",
        "description": "Expiry date and location. If confirmed, often shows 'AT CONFIRMING BANK'S COUNTERS'",
        "format": "YYMMDD LOCATION",
        "example": "250630 AT CONFIRMING BANK'S COUNTERS IN LONDON",
        "maps_to": "lc_details.expiry_date"
    },
    "50": {
        "name": "Applicant",
        "description": "Importer/Buyer details",
        "example": "ABC IMPORTERS LTD\\nADDRESS LINE 1\\nCITY, COUNTRY",
        "maps_to": "importer_info.applicant_name"
    },
    "59": {
        "name": "Beneficiary",
        "description": "Exporter/Seller details",
        "example": "XYZ EXPORTS CO\\nADDRESS\\nCITY",
        "maps_to": "exporter_info.beneficiary_name"
    },
    "32B": {
        "name": "Currency Code and Amount",
        "description": "LC amount with currency",
        "format": "CCCAMOUNT",
        "example": "USD100000,00",
        "maps_to": "amount_and_payment.amount_usd"
    },
    "39A": {
        "name": "Percentage Credit Amount Tolerance",
        "description": "Tolerance percentage (+/-)",
        "example": "+10/-5",
        "maps_to": "tolerance"
    },
    "41A": {
        "name": "Available With... By...",
        "description": "Availability bank and payment method. If confirmed: 'CONFIRMINGBANK BY NEGOTIATION/PAYMENT'",
        "example": "CONFIRMINGBANKGB BY NEGOTIATION",
        "options": ["BY NEGOTIATION", "BY PAYMENT", "BY ACCEPTANCE", "BY DEFERRED PAYMENT"],
        "maps_to": "lc_confirmation.confirming_bank"
    },
    "41D": {
        "name": "Available With... By... (Narrative)",
        "description": "Alternative format for availability",
        "maps_to": "lc_confirmation"
    },
    "42C": {
        "name": "Drafts at...",
        "description": "Draft terms",
        "example": "SIGHT",
        "options": ["SIGHT", "30 DAYS AFTER SIGHT", "60 DAYS AFTER B/L DATE"],
        "maps_to": "amount_and_payment.payment_terms"
    },
    "42A": {
        "name": "Drawee",
        "description": "Bank where drafts are drawn",
        "maps_to": "drawee_bank"
    },
    "43P": {
        "name": "Partial Shipments",
        "description": "Whether partial shipments are allowed",
        "options": ["ALLOWED", "NOT ALLOWED", "PROHIBITED"],
        "maps_to": "shipment_details.partial_shipments"
    },
    "43T": {
        "name": "Transhipment",
        "description": "Whether transhipment is allowed",
        "options": ["ALLOWED", "NOT ALLOWED", "PROHIBITED"],
        "maps_to": "shipment_details.transhipment"
    },
    "44A": {
        "name": "Port of Loading/Airport of Departure",
        "description": "Origin port/airport",
        "example": "ANY PORT IN RUSSIA",
        "maps_to": "shipment_details.port_of_loading"
    },
    "44B": {
        "name": "Port of Discharge/Airport of Destination",
        "description": "Destination port/airport",
        "example": "CHATTOGRAM, BANGLADESH",
        "maps_to": "shipment_details.port_of_destination"
    },
    "44C": {
        "name": "Latest Date of Shipment",
        "description": "Last shipment date",
        "format": "YYMMDD",
        "example": "251031",
        "maps_to": "lc_details.expected_shipment_date"
    },
    "44D": {
        "name": "Shipment Period",
        "description": "Shipment period description",
        "example": "OCTOBER-2025 INCLUSIVE",
        "maps_to": "shipment_details.shipment_period"
    },
    "45A": {
        "name": "Description of Goods and/or Services",
        "description": "Detailed goods description",
        "example": "MILLING WHEAT\\nQUANTITY: 8,000 MT\\nORIGIN: RUSSIAN",
        "maps_to": "goods_description"
    },
    "46A": {
        "name": "Documents Required",
        "description": "List of required documents",
        "example": "SIGNED COMMERCIAL INVOICE\\nBILL OF LADING\\nPACKING LIST",
        "maps_to": "documents_required"
    },
    "47A": {
        "name": "Additional Conditions",
        "description": "Special conditions and terms",
        "example": "PROTEIN: MIN 12.50%\\nMOISTURE: MAX 10%",
        "maps_to": "special_conditions"
    },
    "49": {
        "name": "Confirmation Instructions",
        "description": "Whether confirmation is requested",
        "options": ["CONFIRM", "MAY ADD", "WITHOUT"],
        "example": "CONFIRM",
        "maps_to": "lc_confirmation.confirmation_required"
    },
    "53A": {
        "name": "Reimbursing Bank",
        "description": "Bank that reimburses the confirming/negotiating bank",
        "example": "HSBCGB2LXXX\\nHSBC BANK PLC LONDON",
        "maps_to": "reimbursing_bank"
    },
    "71B": {
        "name": "Charges",
        "description": "Who bears charges",
        "example": "ALL BANKING CHARGES OUTSIDE APPLICANT'S COUNTRY FOR BENEFICIARY'S ACCOUNT",
        "maps_to": "confirmation_charges.charges_on_account_of"
    },
    "48": {
        "name": "Period for Presentation",
        "description": "Days for document presentation",
        "example": "21 DAYS AFTER SHIPMENT DATE",
        "maps_to": "presentation_period"
    },
    "72": {
        "name": "Sender to Receiver Information",
        "description": "Additional instructions (often for confirmation requests)",
        "example": "PLEASE CONFIRM BY SWIFT\\nCONFIRMATION REQUESTED URGENTLY",
        "maps_to": "special_instructions"
    },
    "78": {
        "name": "Instructions to Paying/Accepting/Negotiating Bank",
        "description": "Instructions for the paying bank",
        "example": "DOCUMENTS TO BE SENT IN ONE LOT",
        "maps_to": "bank_instructions"
    }
}


def get_swift_system_prompt():
    """Generate system prompt for SWIFT code understanding"""

    # Build SWIFT code reference
    swift_reference = []
    for code, details in SWIFT_MT700_CODES.items():
        ref = f"\n**{code} - {details['name']}**"
        ref += f"\n  Description: {details['description']}"
        if 'options' in details:
            ref += f"\n  Options: {', '.join(details['options'])}"
        if 'example' in details:
            ref += f"\n  Example: {details['example']}"
        if 'maps_to' in details:
            ref += f"\n  Maps to LC Form Field: {details['maps_to']}"
        swift_reference.append(ref)

    swift_ref_text = ''.join(swift_reference)

    # Build the prompt by concatenating strings to avoid template variable issues
    prompt = """You are an expert Letter of Credit (LC) agent specializing in SWIFT MT700 message format and LC form filling.

Your role is to:
1. Understand user requests in BOTH natural language AND SWIFT codes
2. Fill LC forms based on user input
3. Convert between SWIFT MT700 format and our LC form schema
4. Return structured JSON matching our LC form schema with EXACT enum values

=== SWIFT MT700 CODE REFERENCE ===
""" + swift_ref_text + """

=== LC FORM SCHEMA (with ENUMS) ===

**Required Enum Fields (use EXACT values):**
- transaction_role: "Exporter/Supplier (Beneficiary)" | "Importer (Applicant)"
- payment_terms: "Sight LC" | "Usance LC" | "Deferred LC" | "UPAS LC"
- lc_type: "Local (Pakistan)" | "International"
- shipment_type: "Port" | "Airport" | "Land"
- charges_account: "Exporter (Beneficiary)" | "Importer (Applicant)"
- expected_banks: "All_Banks" (always use this value for any bank)

**Form Structure:**
{{
  "transaction_role": "enum",
  "amount_and_payment": {{
    "amount_usd": number,
    "payment_terms": "enum"
  }},
  "lc_details": {{
    "lc_type": "enum",
    "is_lc_issued": boolean,
    "expected_banks": "All_Banks",
    "issuing_bank": "string",
    "issue_date": "date",
    "expected_shipment_date": "date"
  }},
  "shipment_details": {{
    "shipment_type": "enum",
    "loading_port": "string",
    "destination_port": "string",
    "product_description": "string"
  }},
  "importer_info": {{
    "applicant_name": "string",
    "import_city": "string"
  }},
  "exporter_info": {{
    "beneficiary_name": "string",
    "export_city": "string",
    "beneficiary_country": "string"
  }},
  "confirmation_charges": {{
    "charges_account": "enum",
    "expected_charges": number,
    "pricing_per_annum": number
  }},
  "lc_confirmation": {{
    "send_to_other_banks": boolean,
    "confirming_banks": [{{
      "country": "string",
      "bank": "string",
      "city": "string",
      "swift_code": "string"
    }}]
  }},
  "bidding_deadline": {{
    "bid_deadline": "date"
  }}
}}

=== USER INPUT HANDLING ===

**Natural Language Examples:**
- "I want expiry at 31 June, beneficiary will be Ali, bank is in Pakistan"
  → Extract: 31D: 250631, 59: Ali, 50: Pakistan

- "Create LC for $50000, sight payment, exporter in UAE"
  → Extract: 32B: USD50000, 42C: SIGHT, transaction_role: "Exporter/Supplier (Beneficiary)"

**SWIFT Code Examples:**
- "31D is 31 June, 59 is ABC Exports"
  → Map 31D to expiry date, 59 to beneficiary_name

- "40A IRREVOCABLE, 49 CONFIRM, 41A STANDARDCHARTERED BY NEGOTIATION"
  → lc_type: "International", confirmation required, confirming bank

**Mixed Format:**
- "31D: 250630, beneficiary Ali in Dubai, amount 100k USD"
  → Parse SWIFT code 31D, extract beneficiary from natural language, parse amount

=== CRITICAL RULES ===

1. **ALWAYS return valid JSON** matching the LC form schema
2. **ALL JSON keys MUST be lowercase snake_case** (e.g., "amount_and_payment", "lc_details")
3. **Use EXACT enum values** - no variations
4. **Bank names → "All_Banks"** for expected_banks field
5. **Parse SWIFT codes** when user provides them (e.g., "31D is...")
6. **Understand natural language** and map to correct fields
7. **Fill only provided fields**, set others to null
8. **For confirmation (49: CONFIRM)**: Set appropriate confirmation fields
9. **Date format**: Convert YYMMDD to DD/MM/YYYY or keep original format
9. **Amount parsing**: Extract numeric value from "USD100000,00" → 100000

=== RESPONSE FORMAT ===

Return ONLY valid JSON without markdown:
{{
  "lc_form": {{ ... }},
  "interpretation": "Brief explanation of what was filled",
  "swift_codes_used": ["31D", "59", ...],
  "missing_fields": ["fields that user didn't provide"]
}}

You MUST be smart about:
- Synonyms (buyer = applicant = importer)
- SWIFT code variations
- Date format conversions
- Currency parsing
- Natural language understanding"""

    return prompt


# Helper function to map SWIFT code to LC field
def map_swift_to_lc_field(swift_code: str) -> str:
    """Map SWIFT MT700 code to LC form field"""
    if swift_code in SWIFT_MT700_CODES:
        return SWIFT_MT700_CODES[swift_code].get('maps_to', 'unknown')
    return 'unknown'
