"""
Letter of Credit (LC) form schema and field mappings
"""

# Standard LC form schema
LC_FORM_SCHEMA = {
    "transaction_role": {
        "field": "role_in_transaction",
        "type": "string",
        "options": ["Exporter/Supplier (Beneficiary)", "Importer (Applicant)"],
        "aliases": ["transaction role", "role", "party type", "transaction type"]
    },
    "amount_and_payment": {
        "amount_usd": {
            "field": "amount",
            "type": "number",
            "aliases": ["amount", "lc amount", "value", "transaction amount", "credit amount", "usd amount"]
        },
        "payment_terms": {
            "field": "payment_terms",
            "type": "string",
            "options": ["Sight LC", "Usance LC", "Deferred LC", "UPAS LC"],
            "aliases": ["payment terms", "terms", "payment type", "lc terms", "payment method"]
        }
    },
    "lc_details": {
        "lc_type": {
            "field": "lc_type",
            "type": "string",
            "options": ["Local (Pakistan)", "International"],
            "aliases": ["lc type", "type", "credit type", "letter type"]
        },
        "is_lc_issued": {
            "field": "is_issued",
            "type": "boolean",
            "aliases": ["is issued", "issued", "lc issued", "already issued", "status"]
        },
        "expected_issuing_banks": {
            "field": "expected_banks",
            "type": "string",
            "options": ["All_Banks"],
            "aliases": ["expected banks", "issuing banks", "banks to issue", "preferred banks"],
            "special_mapping": {
                "description": "ANY bank from ANY country should ALWAYS be mapped to 'All_Banks'",
                "rules": [
                    "Any specific bank name → All_Banks",
                    "Multiple banks → All_Banks",
                    "UAE banks → All_Banks",
                    "Pakistani banks → All_Banks",
                    "International banks → All_Banks"
                ]
            }
        },
        "issuing_bank_country": {
            "field": "bank_country",
            "type": "string",
            "aliases": ["country", "bank country", "issuing country", "country of issue"]
        },
        "issuing_bank": {
            "field": "issuing_bank",
            "type": "string",
            "aliases": ["bank", "issuing bank", "bank name", "financial institution"]
        },
        "lc_issuing_date": {
            "field": "issue_date",
            "type": "date",
            "aliases": ["issue date", "issuing date", "date of issue", "lc date", "issuance date"]
        },
        "expected_lc_issuance_date": {
            "field": "expected_issue_date",
            "type": "date",
            "aliases": ["expected date", "expected issuance", "planned issue date"]
        },
        "expected_shipment_date": {
            "field": "expected_shipment_date",
            "type": "date",
            "aliases": ["shipment date", "shipping date", "expected shipment", "delivery date"]
        },
        "expected_confirmation_date": {
            "field": "expected_confirmation_date",
            "type": "date",
            "aliases": ["confirmation date", "expected confirmation", "date to add confirmation"]
        }
    },
    "lc_confirmation": {
        "send_to_other_banks": {
            "field": "send_to_other_banks",
            "type": "boolean",
            "aliases": ["send to other banks", "other banks", "additional banks"]
        },
        "preferred_confirming_banks": {
            "field": "confirming_banks",
            "type": "array",
            "item_schema": {
                "country": "string",
                "bank": "string",
                "city": "string",
                "swift_code": "string"
            },
            "aliases": ["confirming banks", "preferred banks", "confirmation banks"]
        }
    },
    "shipment_details": {
        "shipment_type": {
            "field": "shipment_type",
            "type": "string",
            "options": ["Port", "Airport", "Land"],
            "aliases": ["shipment type", "transport type", "shipping method", "delivery method"]
        },
        "port_of_loading": {
            "field": "loading_port",
            "type": "string",
            "aliases": ["port of loading", "loading port", "origin port", "departure port", "pol"]
        },
        "port_of_destination": {
            "field": "destination_port",
            "type": "string",
            "aliases": ["port of destination", "destination port", "arrival port", "pod", "discharge port"]
        },
        "product_description": {
            "field": "product_description",
            "type": "string",
            "max_length": 50,
            "aliases": ["product", "goods", "merchandise", "commodity", "description"]
        }
    },
    "importer_info": {
        "applicant_name": {
            "field": "applicant_name",
            "type": "string",
            "aliases": ["name of applicant", "applicant", "buyer", "importer name", "importer"]
        },
        "city_of_import": {
            "field": "import_city",
            "type": "string",
            "aliases": ["city of import", "import city", "buyer city", "destination city"]
        }
    },
    "exporter_info": {
        "beneficiary_name": {
            "field": "beneficiary_name",
            "type": "string",
            "aliases": ["name of beneficiary", "beneficiary", "seller", "exporter name", "exporter", "supplier"]
        },
        "city_of_export": {
            "field": "export_city",
            "type": "string",
            "aliases": ["city of export", "export city", "seller city", "origin city"]
        },
        "beneficiary_country": {
            "field": "beneficiary_country",
            "type": "string",
            "aliases": ["beneficiary country", "exporter country", "country of export", "seller country"]
        }
    },
    "confirmation_charges": {
        "charges_on_account_of": {
            "field": "charges_account",
            "type": "string",
            "options": ["Exporter (Beneficiary)", "Importer (Applicant)"],
            "aliases": ["charges on account of", "charges to", "paid by", "account of"]
        },
        "expected_charges": {
            "field": "expected_charges",
            "type": "number",
            "aliases": ["expected charges", "charges", "fees", "cost"]
        },
        "pricing_per_annum": {
            "field": "pricing_per_annum",
            "type": "number",
            "aliases": ["pricing per annum", "annual pricing", "yearly rate", "per annum"]
        }
    },
    "attachments": {
        "documents": {
            "field": "documents",
            "type": "array",
            "aliases": ["documents", "attachments", "files", "lc drafts", "invoice"]
        }
    },
    "bidding_deadline": {
        "last_date_for_bids": {
            "field": "bid_deadline",
            "type": "date",
            "aliases": ["bidding deadline", "last date", "deadline", "bid date", "closing date", "validity", "valid for", "validity period"],
            "note": "If document shows validity in days (e.g., '60 days'), calculate by adding days to lc_issuing_date"
        }
    }
}


def get_extraction_prompt():
    """Generate comprehensive extraction prompt for LC documents using the schema"""
    import json

    # Build field information from schema
    field_guide = []
    enum_fields = []
    special_mappings = []

    for section_name, section_data in LC_FORM_SCHEMA.items():
        section_fields = []
        for field_name, field_info in section_data.items():
            if isinstance(field_info, dict) and 'field' in field_info:
                field_type = field_info.get('type', 'string')
                aliases = ', '.join(field_info.get('aliases', []))
                options = field_info.get('options', [])
                special_mapping = field_info.get('special_mapping')

                field_desc = f"  - {field_info['field']} (type: {field_type})"
                if aliases:
                    field_desc += f"\n    Aliases: {aliases}"
                if options:
                    field_desc += f"\n    **ENUM - MUST use one of: {', '.join(options)}**"
                    # Track enum fields for emphasis
                    enum_fields.append({
                        'field': field_info['field'],
                        'options': options,
                        'special_mapping': special_mapping
                    })

                section_fields.append(field_desc)

                # Track special mappings
                if special_mapping:
                    special_mappings.append({
                        'field': field_info['field'],
                        'description': special_mapping.get('description'),
                        'rules': special_mapping.get('rules', [])
                    })

        if section_fields:
            field_guide.append(f"\n**{section_name.upper().replace('_', ' ')}:**")
            field_guide.extend(section_fields)

    fields_text = '\n'.join(field_guide)

    # Build enum enforcement section
    enum_section = "\n\n=== CRITICAL: ENUM FIELDS (Use EXACT values only) ===\n"
    for enum_field in enum_fields:
        enum_section += f"\n{enum_field['field']}:\n"
        for option in enum_field['options']:
            enum_section += f"  - \"{option}\"\n"
        # Add special mapping note if present
        if enum_field.get('special_mapping'):
            enum_section += f"  ⚠️  Special Rule: {enum_field['special_mapping']['description']}\n"

    # Build special mappings section
    special_mapping_section = ""
    if special_mappings:
        special_mapping_section = "\n\n=== SPECIAL MAPPING RULES ===\n"
        for mapping in special_mappings:
            special_mapping_section += f"\n{mapping['field']}:\n"
            special_mapping_section += f"  {mapping['description']}\n"
            for rule in mapping['rules']:
                special_mapping_section += f"  - {rule}\n"

    return f"""You are an expert in extracting information from Letter of Credit (LC) documents and trade finance forms.

TASK: Extract ALL available information from the provided document and map it to the LC form schema below.

The document may use different terminology or wording, but you MUST match the data to these exact fields. Use the aliases provided to help identify fields even when they have different names.

=== LC FORM SCHEMA ===
{fields_text}
{enum_section}
{special_mapping_section}

=== EXTRACTION RULES ===

1. **Field Matching**: Use the aliases to identify fields even if they're worded differently
   - Example: "buyer", "applicant", "importer" all map to the same field
   - Example: "POL", "loading port", "origin port" all mean port_of_loading

2. **Data Types**:
   - string: Extract as text
   - number: Extract only numeric values (remove currency symbols, commas)
   - date: Keep the format from document (DD/MM/YYYY or YYYY-MM-DD)
   - boolean: Convert "Yes/No" or checkboxes to true/false
   - array: Extract multiple items as a list

3. **⚠️ CRITICAL - ENUM FIELDS (MUST USE EXACT VALUES)**:
   For fields marked with **ENUM**, you MUST return EXACTLY one of the specified values. Do NOT use variations or similar words.

   **Examples:**
   - ✅ CORRECT: "payment_terms": "Sight LC"
   - ❌ WRONG: "payment_terms": "sight" or "Sight Letter of Credit" or "at sight"

   - ✅ CORRECT: "role_in_transaction": "Exporter/Supplier (Beneficiary)"
   - ❌ WRONG: "role_in_transaction": "Exporter" or "Beneficiary"

   - ✅ CORRECT: "shipment_type": "Port"
   - ❌ WRONG: "shipment_type": "Sea Port" or "by port"

   - ✅ CORRECT: "lc_type": "International"
   - ❌ WRONG: "lc_type": "Foreign" or "Cross-border"

   **If the document has similar but not exact terms:**
   - "sight payment" → "Sight LC"
   - "deferred payment" → "Deferred LC"
   - "usance payment at sight" → "UPAS LC"
   - "exporter" or "seller" → "Exporter/Supplier (Beneficiary)"
   - "importer" or "buyer" → "Importer (Applicant)"
   - "sea" or "ocean" → "Port"
   - "air" or "flight" → "Airport"
   - "local" or "domestic" → "Local (Pakistan)"
   - "foreign" or "cross-border" → "International"

   **⚠️ CRITICAL - Bank Name Mapping:**
   - **For field "expected_banks"**: ALWAYS use "All_Banks" regardless of actual bank names
   - Examples:
     - "Emirates NBD" → "All_Banks"
     - "First Abu Dhabi Bank, Mashreq Bank" → "All_Banks"
     - "National Bank of Pakistan" → "All_Banks"
     - "HSBC" → "All_Banks"
     - "Standard Chartered" → "All_Banks"
     - "Citibank, Bank of America" → "All_Banks"
     - ANY bank name or list of banks → "All_Banks"

4. **Missing Fields**: If a field is not found in the document, set it to null

5. **⚠️ CRITICAL - Bidding Deadline Calculation**:
   - Sometimes the document shows "validity" in DAYS (e.g., "60 days", "90 days") instead of an actual date
   - **When you see validity in days**: Calculate the actual bidding deadline date by adding those days to the LC issue date
   - **Formula**: bid_deadline = lc_issuing_date + validity_days

   **Examples:**
   - If lc_issuing_date = "2025-01-01" and validity = "60 days"
     → bid_deadline = "2025-03-02" (January 1 + 60 days)

   - If lc_issuing_date = "2025-06-15" and validity = "90 days"
     → bid_deadline = "2025-09-13" (June 15 + 90 days)

   - If document shows actual date like "2025-12-31", use that directly
     → bid_deadline = "2025-12-31"

6. **Smart Extraction**:
   - Look for variations in terminology
   - Handle abbreviations (e.g., "POL" = Port of Loading)
   - Extract from tables, checkboxes, and form fields
   - Understand context (e.g., amounts near "USD" are in USD)

7. **Output Format**: Return a well-structured JSON object with sections matching the schema
   - **ALL JSON keys MUST be lowercase snake_case** (e.g., "amount_and_payment", "lc_details", "shipment_type")
   - Group fields by their section (transaction_role, amount_and_payment, etc.)
   - Use the exact field names from the schema
   - Ensure proper data types
   - **Use EXACT enum values as specified above**

=== OUTPUT STRUCTURE ===
Return the data in this JSON structure:
{{
  "transaction_role": "Exporter/Supplier (Beneficiary)" | "Importer (Applicant)",
  "amount_and_payment": {{
    "amount_usd": number,
    "payment_terms": "Sight LC" | "Usance LC" | "Deferred LC" | "UPAS LC"
  }},
  "lc_details": {{
    "lc_type": "Local (Pakistan)" | "International",
    "is_lc_issued": boolean,
    ...
  }},
  "shipment_details": {{
    "shipment_type": "Port" | "Airport" | "Land",
    ...
  }},
  "confirmation_charges": {{
    "charges_account": "Exporter (Beneficiary)" | "Importer (Applicant)",
    ...
  }},
  ...
}}

IMPORTANT:
1. Return ONLY valid JSON without markdown formatting or code blocks
2. ALL JSON keys MUST be lowercase snake_case format
3. Use EXACT enum values as listed in the ENUM FIELDS section above
4. Do NOT modify or abbreviate enum values"""


def get_validation_prompt():
    """Generate validation prompt for extracted data"""
    return """Review the extracted LC data and ensure:

1. All dates are in a consistent format
2. Amounts are numeric values
3. Required fields are not missing
4. Enums match the allowed options
5. All related fields are logically consistent

If you find any issues, correct them and return the cleaned data."""
