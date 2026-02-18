import os
import sys
import argparse
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

def trigger():
    parser = argparse.ArgumentParser(description="Trigger an outbound call for the Voice Bot.")
    parser.add_argument("to", help="The destination phone number (e.g., +15550000000).")
    parser.add_argument("--scenario", default="scheduling", help="The scenario ID from scenarios.json (default: scheduling).")
    parser.add_argument("--url", help="Override the base ngrok URL (otherwise uses current Twilio config).")
    
    args = parser.parse_args()

    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    from_number = os.getenv('TWILIO_PHONE_NUMBER')

    if not account_sid or not auth_token or not from_number:
        print("❌ Error: Missing credentials in .env file.")
        sys.exit(1)

    client = Client(account_sid, auth_token)

    # If no URL is provided, we assume Twilio is already configured via update_webhook.py
    # OR we try to find the current Voice URL for the number to append the scenario.
    to_number = args.to
    scenario = args.scenario
    
    voice_url = None
    if args.url:
        voice_url = f"{args.url.rstrip('/')}/voice?scenario={scenario}"
    else:
        # Fetch current config from Twilio to append scenario
        incoming_numbers = client.incoming_phone_numbers.list(phone_number=from_number)
        if incoming_numbers:
            current_url = incoming_numbers[0].voice_url
            if "?" in current_url:
                voice_url = f"{current_url.split('?')[0]}?scenario={scenario}"
            else:
                voice_url = f"{current_url}?scenario={scenario}"
        else:
            print("❌ Error: Could not find phone number in Twilio account to get Voice URL.")
            sys.exit(1)

    print(f"📞 Initiating call...")
    print(f"   From: {from_number}")
    print(f"   To:   {to_number}")
    print(f"   Scenario: {scenario}")
    print(f"   Url:  {voice_url}")

    try:
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url=voice_url
        )
        print(f"✅ Call Initiated! SID: {call.sid}")
        print("The phone should ring momentarily. When you answer, the bot will start.")

    except Exception as e:
        print(f"❌ Failed to initiate call: {e}")

if __name__ == "__main__":
    trigger()
