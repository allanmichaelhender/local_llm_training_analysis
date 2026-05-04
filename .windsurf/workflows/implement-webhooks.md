---
description: Replace polling with Twilio webhooks using FastAPI + Uvicorn
---

# Implement Twilio Webhooks with FastAPI

Replace the current polling-based WhatsApp message fetching with real-time Twilio webhooks using FastAPI and Uvicorn.

## Architecture Changes

**Current (Polling):**
- Orchestrator polls Twilio every 120 seconds
- Delay: up to 120 seconds before seeing new message
- Inefficient: makes API calls even when no new messages

**New (Webhooks):**
- Twilio sends HTTP POST to FastAPI endpoint when new message arrives
- Instant: no polling delay
- Efficient: only triggered when needed

## Implementation Steps

### 1. Create FastAPI Application

Create `webhook_server.py`:

```python
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

from services.database import (
    get_pending_feedback_activity,
    update_user_feedback,
    update_llm_summary,
)
from services.llm_service import LLMService

load_dotenv()

app = FastAPI()

# Store prompt times for timestamp filtering
prompt_times = {}

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """Receive WhatsApp messages from Twilio webhook"""
    try:
        # Parse form data from Twilio
        form_data = await request.form()
        
        message_sid = form_data.get("MessageSid")
        message_body = form_data.get("Body", "").strip()
        message_from = form_data.get("From")
        message_time = datetime.now(timezone.utc)
        
        # Check if there's a pending activity waiting for feedback
        pending_id, pending_data = get_pending_feedback_activity()
        
        if not pending_id:
            return JSONResponse({"status": "no pending activity"})
        
        # Check if this activity has a recent prompt
        last_prompt_time = prompt_times.get(pending_id)
        if not last_prompt_time:
            return JSONResponse({"status": "no recent prompt"})
        
        # Only accept messages sent after the prompt (with 5 second buffer)
        if message_time <= last_prompt_time:
            return JSONResponse({"status": "message too old"})
        
        # Store feedback
        if message_body:
            update_user_feedback(pending_id, message_body)
            print(f"   [WEBHOOK] Feedback received: {message_body[:50]}...")
            
            # Generate LLM summary
            hr_series = pending_data.get("hr_time_series", [])
            llm = LLMService()
            summary = llm.generate_summary(pending_data, message_body, hr_series)
            update_llm_summary(pending_id, summary)
            print(f"   [WEBHOOK] Summary generated")
            
            # Reset prompt time
            prompt_times.pop(pending_id, None)
            
            return JSONResponse({"status": "success"})
        
        return JSONResponse({"status": "empty message"})
    
    except Exception as e:
        print(f"   [WEBHOOK] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/prompt-sent")
async def prompt_sent_webhook(request: Request):
    """Called when WhatsApp prompt is sent to track prompt time"""
    try:
        form_data = await request.form()
        activity_id = form_data.get("activity_id")
        
        if activity_id:
            prompt_times[activity_id] = datetime.now(timezone.utc)
            print(f"   [WEBHOOK] Prompt time recorded for {activity_id}")
        
        return JSONResponse({"status": "success"})
    
    except Exception as e:
        print(f"   [WEBHOOK] Error recording prompt time: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
```

### 2. Update Orchestrator to Call Webhook

Modify `orchestrator.py` to call webhook when prompt is sent:

```python
import requests

# After sending WhatsApp prompt
whatsapp.send_activity_prompt(activity)
last_prompt_time = datetime.now(timezone.utc)
print("   WhatsApp prompt sent")

# Notify webhook server of prompt time
try:
    requests.post("http://localhost:8000/webhook/prompt-sent", 
                  data={"activity_id": activity["id"]})
except Exception as e:
    print(f"   Warning: Could not notify webhook server: {e}")
```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn
```

### 4. Run Webhook Server

**Development (local):**
```bash
uvicorn webhook_server:app --reload --host 0.0.0.0 --port 8000
```

**Production (with Nginx):**
```bash
uvicorn webhook_server:app --host 127.0.0.1 --port 8000
```

### 5. Configure Twilio Webhook

1. Go to Twilio Console → Messaging → Settings → WhatsApp sandbox settings
2. Set "When a message comes in" to: `https://your-domain.com/webhook/whatsapp`
3. For local development, use ngrok:
   ```bash
   ngrok http 8000
   ```
   Then set webhook URL to: `https://your-ngrok-url.ngrok.io/webhook/whatsapp`

### 6. Nginx Configuration (Production)

Create `/etc/nginx/sites-available/garmin-coach`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /webhook/ {
        proxy_pass http://127.0.0.1:8000/webhook/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/garmin-coach /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Add Webhook Signature Verification (Security)

Update webhook endpoint to verify Twilio signatures:

```python
from fastapi import Header, HTTPException
from twilio.request_validator import RequestValidator

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    x_twilio_signature: str = Header(None)
):
    # Verify Twilio signature
    validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))
    url = str(request.url)
    form_data = await request.form()
    
    if not validator.validate(url, form_data, x_twilio_signature):
        raise HTTPException(status_code=403, detail="Invalid signature")
    
    # Process webhook...
```

### 8. Remove Polling from Orchestrator

Remove the polling loop from `orchestrator.py` and replace with:
- Activity fetching only (every 120 seconds)
- No WhatsApp message polling
- Webhook handles feedback in real-time

## Testing

1. Start webhook server: `uvicorn webhook_server:app --reload --port 8000`
2. Start ngrok: `ngrok http 8000`
3. Configure Twilio webhook with ngrok URL
4. Send test WhatsApp message
5. Check webhook server logs for incoming requests

## Benefits

- **Real-time**: No polling delay
- **Efficient**: Only processes when messages arrive
- **Scalable**: Can handle high volume without polling overhead
- **Cleaner**: Separates concerns (webhook server vs orchestrator)
