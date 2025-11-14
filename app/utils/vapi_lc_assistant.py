"""
VAPI LC Form Completion Assistant Configuration
This assistant helps complete LC form fields through voice conversation
"""
from typing import Dict, Any, List
from app.utils.lc_schema import LC_FORM_SCHEMA


def get_missing_fields_description(provided_fields: Dict[str, Any]) -> str:
    """
    Generate a description of fields that still need to be collected
    based on what was already provided from the frontend
    """
    all_fields_info = []
    missing_fields_info = []

    # Flatten the schema to get all fields
    for section_name, section_data in LC_FORM_SCHEMA.items():
        for field_name, field_info in section_data.items():
            if isinstance(field_info, dict) and 'field' in field_info:
                field_key = field_info['field']
                field_type = field_info.get('type', 'string')
                options = field_info.get('options', [])
                aliases = field_info.get('aliases', [])

                # Check if this field is missing from provided data
                field_path = f"{section_name}.{field_name}"
                is_missing = not _is_field_provided(provided_fields, section_name, field_name)

                field_desc = {
                    'section': section_name,
                    'field_name': field_name,
                    'field_key': field_key,
                    'type': field_type,
                    'options': options,
                    'aliases': aliases,
                    'is_missing': is_missing
                }

                all_fields_info.append(field_desc)
                if is_missing:
                    missing_fields_info.append(field_desc)

    return _format_fields_for_prompt(missing_fields_info, all_fields_info)


def _is_field_provided(data: Dict[str, Any], section: str, field: str) -> bool:
    """Check if a field value was provided in the data"""
    if section in data:
        section_data = data[section]
        if isinstance(section_data, dict):
            # Check both field name and nested structure
            return field in section_data and section_data[field] is not None
    return False


def _format_fields_for_prompt(missing_fields: List[Dict], all_fields: List[Dict]) -> str:
    """Format field information for the assistant prompt"""
    if not missing_fields:
        return "All fields have been provided. No additional information needed."

    prompt = "FIELDS TO COLLECT:\n\n"

    # Group by section
    sections = {}
    for field in missing_fields:
        section = field['section']
        if section not in sections:
            sections[section] = []
        sections[section].append(field)

    for section_name, fields in sections.items():
        prompt += f"\n**{section_name.upper().replace('_', ' ')}:**\n"
        for field in fields:
            prompt += f"\n- {field['field_key']} ({field['type']})\n"
            if field['aliases']:
                prompt += f"  Can also be called: {', '.join(field['aliases'])}\n"
            if field['options']:
                prompt += f"  ⚠️ MUST be one of: {', '.join(field['options'])}\n"

    return prompt


def get_lc_completion_assistant_config(
    provided_fields: Dict[str, Any],
    company_name: str = "Trade Origin"
) -> Dict[str, Any]:
    """
    Generate VAPI assistant configuration for LC form completion

    Args:
        provided_fields: Fields already filled from the frontend
        company_name: Company name for greeting

    Returns:
        VAPI assistant configuration
    """
    missing_fields_desc = get_missing_fields_description(provided_fields)

    # Generate a summary of what's already provided
    provided_summary = _generate_provided_summary(provided_fields)

    system_prompt = f"""You are a professional and friendly voice assistant for {company_name}, a trade finance company.

YOUR ROLE:
You are helping complete a Letter of Credit (LC) application form. The customer has already filled out some fields on our website, and you need to collect the REMAINING information through a natural conversation.

ALREADY PROVIDED INFORMATION:
{provided_summary}

{missing_fields_desc}

CONVERSATION GUIDELINES:

1. **Natural Flow**:
   - Have a natural conversation, don't make it feel like a rigid form
   - Ask questions conversationally, not robotically
   - Group related questions together when appropriate

2. **Confirmation**:
   - For critical information (amounts, dates, names), always confirm by reading back
   - If something sounds unclear, politely ask for clarification

3. **Handling Enum Fields** (fields with specific options):
   - When asking about these fields, mention the available options
   - Example: "For the payment terms, we offer Sight LC, Usance LC, Deferred LC, or UPAS LC. Which would you prefer?"
   - If they use different terminology, map it to the correct option

4. **Professional Yet Friendly**:
   - Be warm and conversational
   - Use phrases like "Great!", "Perfect!", "Thank you for that information"
   - If they don't know something, reassure them it's okay

5. **Efficiency**:
   - Don't ask for information that's already provided
   - Keep questions concise and clear
   - Move through the form efficiently while maintaining a friendly tone

6. **Closing**:
   - Once you've collected all the missing information, summarize what was collected
   - Confirm next steps
   - Thank them for their time

7. **If User Doesn't Mention a Field**:
   - ALWAYS ask about that field explicitly
   - Don't skip any missing fields
   - Example: If they don't mention payment terms, ask: "What payment terms would you prefer - Sight LC, Usance LC, Deferred LC, or UPAS LC?"
   - Go through ALL missing fields systematically
   - If they say "I don't know", mark it as null and move to next field
   - NEVER end the call until you've asked about EVERY missing field listed above

EXAMPLE CONVERSATION FLOW:

"Hello! Thank you for starting your LC application with {company_name}. I see you've already provided [mention a key field they filled]. I just need to collect a few more details to complete your application. This should only take a few minutes. Shall we begin?"

[Collect information naturally - go through EACH missing field]

"Perfect! Let me confirm what we've collected today... [summary]. Does everything sound correct?"

"Excellent! We now have all the information needed for your LC application. Our team will review this and get back to you within 24 hours. Is there anything else you'd like to know?"

DATA EXTRACTION:
As you collect information, structure it according to the LC form schema. Return data in proper JSON format with lowercase snake_case keys matching the schema sections and fields.

IMPORTANT RULES:
- ONLY collect information for the missing fields listed above
- For enum fields, use EXACT values from the options (e.g., "Sight LC", "Port", "International")
- If customer says they don't know something, mark it as null and move to next field
- ALWAYS ask about EVERY missing field - never skip fields
- If user doesn't mention a field, ASK them about it explicitly
- Always be respectful of their time
- Only end the conversation once ALL missing fields have been addressed (either collected or marked as unknown)
- Do NOT end the call prematurely - ensure completeness"""

    # VAPI config for web calls using Google Gemini
    # IMPORTANT: You MUST add Gemini API key in VAPI dashboard first:
    # https://dashboard.vapi.ai → Settings → Provider Keys → Add Google AI Key
    return {
        "firstMessage": f"Hello! Thank you for starting your LC application with {company_name}. I can see you've already filled out some information. I just need to collect a few more details to complete your application. This should only take a few minutes. Are you ready to continue?",
        "model": {
            "provider": "google",
            "model": "gemini-2.5-flash",  # Fixed: use gemini-2.5-flash, not 1.5
            "systemPrompt": system_prompt,
            "temperature": 0.7
        },
        "voice": {
            "provider": "playht",
            "voiceId": "jennifer"
        },
        "silenceTimeoutSeconds": 30,  # How long to wait for user response
        "maxDurationSeconds": 600,  # Max call duration (10 minutes)
        "endCallMessage": "Thank you for providing your information. We'll process your LC application shortly. Goodbye!",
        "endCallPhrases": ["goodbye", "that's all", "end call", "thank you goodbye"]
    }


def _generate_provided_summary(provided_fields: Dict[str, Any]) -> str:
    """Generate a human-readable summary of provided fields"""
    if not provided_fields:
        return "No fields have been provided yet."

    summary_lines = []
    for section, fields in provided_fields.items():
        if isinstance(fields, dict):
            for field, value in fields.items():
                if value is not None:
                    summary_lines.append(f"- {field}: {value}")

    if not summary_lines:
        return "No fields have been provided yet."

    return "\n".join(summary_lines)


def merge_collected_data(
    provided_fields: Dict[str, Any],
    collected_fields: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge the fields provided from frontend with fields collected via voice

    Args:
        provided_fields: Fields from frontend
        collected_fields: Fields collected via voice call

    Returns:
        Complete merged LC form data
    """
    import copy

    # Deep copy to avoid modifying original
    merged = copy.deepcopy(provided_fields)

    # Merge collected fields
    for section, fields in collected_fields.items():
        if section not in merged:
            merged[section] = {}

        if isinstance(fields, dict):
            for field, value in fields.items():
                # Only add if not already present or if the collected value is not None
                if field not in merged[section] or merged[section][field] is None:
                    merged[section][field] = value

    return merged
