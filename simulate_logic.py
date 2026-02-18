import asyncio
import os
import sys
from dotenv import load_dotenv
load_dotenv()

from services.openai_service import get_chat_response
from services.deepgram_service import deepgram_service

# Mock object to simulate Deepgram message
class MockAlternative:
    def __init__(self, transcript):
        self.transcript = transcript

class MockChannel:
    def __init__(self, transcript):
        self.alternatives = [MockAlternative(transcript)]

class MockMessage:
    def __init__(self, transcript, is_final=True):
        self.channel = MockChannel(transcript)
        self.is_final = is_final

async def simulate_handler():
    # This is EXACTLY the logic from main.py
    async def on_deepgram_message(message):
        try:
            print(f"DEBUG: Handler started for {message.channel.alternatives[0].transcript}")
            if hasattr(message, 'channel'):
                transcript = message.channel.alternatives[0].transcript
                if transcript and len(transcript.strip()) > 0:
                    if message.is_final:
                        print(f"🗣️ User: {transcript}")
                        sys.stdout.flush()
                        
                        # Get AI Reply
                        print(f"🧠 Asking AI: {transcript}")
                        sys.stdout.flush()
                        
                        reply = await get_chat_response(transcript)
                        print(f"🤖 Bot: {reply}")
                        sys.stdout.flush()
                        
                        # TTS
                        print(f"🔊 Generating TTS for: {reply}")
                        sys.stdout.flush()
                        audio_data = await deepgram_service.text_to_speech(reply)
                        if audio_data:
                            print(f"✅ TTS Generated ({len(audio_data)} bytes)")
                        else:
                            print("❌ TTS Failed")
                        sys.stdout.flush()
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

    print("--- Starting Simulation 1: 'Hello?' ---")
    msg1 = MockMessage("Hello?")
    await on_deepgram_message(msg1)
    
    print("\n--- Starting Simulation 2: 'My name is John' ---")
    msg2 = MockMessage("My name is John")
    await on_deepgram_message(msg2)

if __name__ == "__main__":
    asyncio.run(simulate_handler())
