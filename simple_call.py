import os
import time
from twilio.rest import Client
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

# Configuration
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
from_number = os.getenv('TWILIO_PHONE_NUMBER')
to_number = '+17166581112'  # Pretty Good AI Challenge Number

# Initialize Twilio Client
if not account_sid or not auth_token or not from_number:
    print("❌ Error: Missing credentials in .env file.")
    print("Please ensure TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER are set.")
    exit(1)

client = Client(account_sid, auth_token)

print(f"📞 Initiating call from {from_number} to {to_number}...")

try:
    # We use a demo URL for TwiML instructions. 
    # This URL simply tells Twilio to say "Thanks for the call. Configure your number's voice URL to change this message." 
    # This is just to keep the line open so we can verify the other side picked up.
    call = client.calls.create(
        url='http://demo.twilio.com/docs/voice.xml',
        to=to_number,
        from_=from_number
    )
    
    print(f"✅ Call initiated! SID: {call.sid}")
    print("Check your phone or Twilio console to see if it connected.")
    print("Polling for call status...")

    # Poll status for a few seconds
    for _ in range(10):
        updated_call = client.calls(call.sid).fetch()
        print(f"   Status: {updated_call.status}")
        if updated_call.status in ['completed', 'failed', 'busy', 'no-answer']:
            break
        time.sleep(2)

except Exception as e:
    print(f"❌ Failed to make call: {e}")
