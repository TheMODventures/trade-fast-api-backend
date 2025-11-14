# VAPI Voice AI Integration for LC Form Completion

## Overview

This integration allows users to complete LC (Letter of Credit) forms through **web-based voice conversations**. Users fill out some fields manually on the website, then click a button to have a voice conversation with an AI agent that collects the remaining information.

## How It Works

### Flow

1. **User fills partial LC form** (e.g., 4-5 fields) on your React frontend
2. **User clicks "Call Agent to Fill Form" button**
3. **Frontend calls backend** `/vapi/lc/create-assistant` with filled data
4. **Backend returns** VAPI assistant configuration
5. **Frontend initiates voice call** in browser using VAPI Web SDK
6. **User talks with AI agent** to provide missing information
7. **When call ends**, frontend calls `/vapi/lc/get-complete-data/{call_id}`
8. **Frontend receives complete LC data** (merged from form + voice)
9. **Frontend updates form** with all collected data

## Backend Setup

### 1. Environment Variables

Add to your `.env` file:

```bash
# VAPI Configuration
VAPI_API_KEY=your_vapi_api_key_here
VAPI_WEBHOOK_SECRET=your_webhook_secret_here  # Optional but recommended
```

Get your API key from: https://dashboard.vapi.ai

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

New dependency added: `httpx==0.27.0`

### 3. Start the Server

```bash
uvicorn app.main:app --reload
```

The VAPI endpoints will be available at: `http://localhost:8000/vapi/*`

## Backend API Endpoints

### 1. Create Assistant Configuration
**POST** `/vapi/lc/create-assistant`

Creates a VAPI assistant configured to collect missing LC fields.

**Request:**
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
  },
  "company_name": "Trade Finance Solutions"
}
```

**Response:**
```json
{
  "success": true,
  "assistant_config": {
    "name": "LC Form Completion Assistant",
    "firstMessage": "Hello! Thank you for starting your LC application...",
    "context": "...",
    "model": {...},
    "voice": {...},
    "transcriber": {...},
    "metadata": {...}
  }
}
```

### 2. Get Complete LC Data
**GET** `/vapi/lc/get-complete-data/{call_id}`

**This is the main endpoint!** Call this after the voice call ends to get complete data.

**Response:**
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
      "is_lc_issued": false,
      "expected_issuing_banks": "All_Banks"
    },
    "importer_info": {
      "applicant_name": "Ali Osaid",
      "city_of_import": "Dubai"
    },
    "shipment_details": {
      "shipment_type": "Port",
      "port_of_loading": "Karachi",
      "port_of_destination": "Jebel Ali"
    }
  },
  "provided_fields": {...},
  "collected_fields": {...},
  "transcript": [...]
}
```

### 3. Other Endpoints

- **GET** `/vapi/lc/call-status/{call_id}` - Check if call is still active
- **POST** `/vapi/lc/end-call` - End call manually
- **GET** `/vapi/lc/transcript/{call_id}` - Get conversation transcript
- **GET** `/vapi/lc/recording/{call_id}` - Get call recording URL
- **POST** `/vapi/webhook` - Webhook for VAPI events (optional)
- **GET** `/vapi/health` - Health check

## Frontend Integration

### 1. Install VAPI Web SDK

```bash
npm install @vapi-ai/web
```

### 2. React Component Example

```typescript
import { useVapi } from "@vapi-ai/web";
import { useState } from "react";

function LCFormWithVoice() {
  const [lcData, setLcData] = useState({
    transaction_role: "Exporter/Supplier (Beneficiary)",
    amount_and_payment: { amount_usd: 50000 },
    importer_info: { applicant_name: "Ali Osaid" }
  });

  const [isCallActive, setIsCallActive] = useState(false);
  const vapi = useVapi();

  const handleCallAgent = async () => {
    try {
      // Step 1: Get assistant config from backend
      const response = await fetch("/vapi/lc/create-assistant", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": "Bearer YOUR_API_KEY"
        },
        body: JSON.stringify({
          provided_lc_data: lcData,
          company_name: "Trade Finance Solutions"
        })
      });

      const data = await response.json();
      const assistantConfig = data.assistant_config;

      // Step 2: Start voice call in browser
      const call = await vapi.start(assistantConfig);
      setIsCallActive(true);

      // Step 3: Listen for call end event
      call.on("call-end", async () => {
        setIsCallActive(false);

        // Step 4: Get complete LC data
        const completeDataResponse = await fetch(
          `/vapi/lc/get-complete-data/${call.id}`,
          {
            headers: { "Authorization": "Bearer YOUR_API_KEY" }
          }
        );

        const completeData = await completeDataResponse.json();

        // Step 5: Update form with complete data
        setLcData(completeData.complete_lc_data);

        console.log("Form completed via voice!", completeData);
      });

    } catch (error) {
      console.error("Error starting voice call:", error);
    }
  };

  const handleEndCall = () => {
    vapi.stop();
    setIsCallActive(false);
  };

  return (
    <div>
      <h2>LC Application Form</h2>

      {/* Your form fields here */}
      <input
        value={lcData.importer_info?.applicant_name || ""}
        onChange={(e) => setLcData({
          ...lcData,
          importer_info: { ...lcData.importer_info, applicant_name: e.target.value }
        })}
        placeholder="Applicant Name"
      />

      {/* Voice call buttons */}
      <div>
        {!isCallActive ? (
          <button onClick={handleCallAgent}>
            🎤 Call Agent to Fill Form
          </button>
        ) : (
          <button onClick={handleEndCall}>
            ❌ End Call
          </button>
        )}
      </div>

      {isCallActive && <p>🔴 Voice call active...</p>}
    </div>
  );
}

export default LCFormWithVoice;
```

### 3. Simpler Approach (without React Hooks)

```javascript
import Vapi from "@vapi-ai/web";

const vapi = new Vapi("YOUR_VAPI_PUBLIC_KEY");

async function startLCVoiceCall(lcData) {
  // Get assistant config
  const response = await fetch("/vapi/lc/create-assistant", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      provided_lc_data: lcData
    })
  });

  const { assistant_config } = await response.json();

  // Start call
  vapi.start(assistant_config);

  // Listen for call end
  vapi.on("call-end", async (callData) => {
    const callId = callData.id;

    // Get complete data
    const completeResponse = await fetch(`/vapi/lc/get-complete-data/${callId}`);
    const { complete_lc_data } = await completeResponse.json();

    // Update your form
    updateLCForm(complete_lc_data);
  });
}
```

## How the AI Assistant Works

The assistant is configured to:

1. **Know what's already filled** - It won't ask for information you already provided
2. **Ask for missing fields only** - Based on the LC schema (20 fields total)
3. **Handle natural conversation** - Not robotic, friendly and professional
4. **Validate enum fields** - Ensures values like "Sight LC", "Port", etc. are correct
5. **Confirm critical info** - Reads back amounts, dates, names for confirmation
6. **Extract structured data** - Uses Gemini to convert conversation to JSON

## Data Extraction Process

When the call ends:

1. Backend gets the call transcript from VAPI
2. Uses Gemini AI to extract structured data from the conversation
3. Maps natural language to LC form schema fields
4. Validates extracted data
5. Merges with originally provided data
6. Returns complete LC form data

## Architecture

```
Frontend (React)
    ↓
    ↓ POST /vapi/lc/create-assistant (with partial LC data)
    ↓
Backend (FastAPI)
    ↓
    ↓ Returns assistant config
    ↓
Frontend
    ↓
    ↓ Starts voice call using VAPI SDK
    ↓
User ←→ VAPI Voice AI (in browser)
    ↓
    ↓ Call ends
    ↓
Frontend
    ↓
    ↓ GET /vapi/lc/get-complete-data/{call_id}
    ↓
Backend
    ↓
    ↓ 1. Gets transcript from VAPI
    ↓ 2. Extracts data using Gemini
    ↓ 3. Merges with provided data
    ↓ 4. Returns complete LC data
    ↓
Frontend (updates form with complete data)
```

## Key Files

- **Controller**: `app/controllers/vapi_controller.py` - API endpoints
- **Agent**: `app/agents/vapi_agent.py` - Business logic, data extraction
- **Service**: `app/utils/vapi_service.py` - VAPI API client
- **Assistant Config**: `app/utils/vapi_lc_assistant.py` - Assistant configuration generator
- **Schema**: `app/utils/lc_schema.py` - LC form schema and extraction prompts

## Testing

### 1. Check Health
```bash
curl http://localhost:8000/vapi/health
```

### 2. Create Assistant (test endpoint)
```bash
curl -X POST http://localhost:8000/vapi/lc/create-assistant \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "provided_lc_data": {
      "importer_info": {
        "applicant_name": "Ali Osaid"
      }
    }
  }'
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

All VAPI endpoints are documented there with examples.

## Security

- All endpoints require API key authentication (except /health and /docs)
- VAPI webhooks are validated using signature verification
- User data is only stored temporarily during call processing
- Transcripts can be optionally recorded (configure in assistant)

## Customization

### Change Voice
In `app/utils/vapi_lc_assistant.py`, modify:
```python
"voice": {
    "provider": "11labs",
    "voiceId": "rachel"  # Change to other ElevenLabs voices
}
```

### Change AI Model
```python
"model": {
    "provider": "openai",
    "model": "gpt-4",  # or "gpt-3.5-turbo" for faster/cheaper
    "temperature": 0.7
}
```

### Modify Conversation Style
Edit the system prompt in `get_lc_completion_assistant_config()` function.

## Troubleshooting

### "VAPI_API_KEY not configured"
- Make sure `.env` file exists and has `VAPI_API_KEY`
- Restart the FastAPI server after adding the key

### "Call transcript not available"
- Wait a few seconds after call ends for VAPI to process transcript
- Check call status first: GET `/vapi/lc/call-status/{call_id}`

### Voice call not starting in frontend
- Verify VAPI public key is correct
- Check browser console for errors
- Ensure microphone permissions are granted

### Data extraction returns empty fields
- Check if Gemini API key is configured
- Review the transcript to see if information was actually discussed
- May need to adjust extraction prompts

## Next Steps

1. **Add your VAPI API key** to `.env`
2. **Test the backend** using Swagger UI at /docs
3. **Integrate with frontend** using the React example above
4. **Customize the assistant** voice, personality, conversation flow
5. **Monitor calls** in VAPI dashboard: https://dashboard.vapi.ai

## Support

- VAPI Documentation: https://docs.vapi.ai
- VAPI Discord: https://discord.gg/vapi
- Backend Issues: Check logs in FastAPI console
