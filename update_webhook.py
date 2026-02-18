import os
import sys
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Configuration
if len(sys.argv) > 1:
    NGROK_URL = sys.argv[1].rstrip("/")
else:
    # Default fallback
    NGROK_URL = "https://your-url.ngrok-free.dev"

VOICE_URL = f"{NGROK_URL}/voice"
PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

print(f"🔍 Looking for phone number: {PHONE_NUMBER}")

# Find the specific phone number SID
incoming_phone_numbers = client.incoming_phone_numbers.list(phone_number=PHONE_NUMBER)

if incoming_phone_numbers:
    phone_number_sid = incoming_phone_numbers[0].sid
    print(f"✅ Found SID: {phone_number_sid}")
    
    # Update the Voice URL
    print(f"🔄 Updating Voice Webhook to: {VOICE_URL}")
    client.incoming_phone_numbers(phone_number_sid).update(
        voice_url=VOICE_URL,
        voice_method="POST"
    )
    print("✨ Success! Twilio is now connected to your local server.")
else:
    print(f"❌ Could not find the phone number {PHONE_NUMBER} in your Twilio account.")
    print("Please check .env matches your purchased number exactly.")
