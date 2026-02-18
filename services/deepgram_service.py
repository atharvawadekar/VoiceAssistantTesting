import os
import asyncio
import httpx
import ssl
from deepgram import AsyncDeepgramClient

# Initialize Deepgram Client
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

class DeepgramService:
    def __init__(self):
        self.api_key = DEEPGRAM_API_KEY
        if not self.api_key:
            print("❌ Error: DEEPGRAM_API_KEY is missing")
        
        # Custom HTTP client for Deepgram
        self.httpx_client = httpx.AsyncClient()
        self.client = AsyncDeepgramClient(api_key=self.api_key, httpx_client=self.httpx_client)

    async def create_stt_connection(self):
        """
        Returns the async context manager for the Deepgram connection.
        """
        options = {
            "model": "nova-2",
            "language": "en-US",
            "smart_format": "true",
            "encoding": "mulaw",
            "sample_rate": "8000",
            "endpointing": "5000",
            "interim_results": "true" 
        }
        
        # Calling connect() on the async client returns an _AsyncGeneratorContextManager
        return self.client.listen.v1.connect(**options)

    async def text_to_speech(self, text):
        """
        REST execution for TTS using httpx for simplicity/speed.
        Returns raw audio bytes (mulaw/8000).
        """
        url = "https://api.deepgram.com/v1/speak?model=aura-asteria-en&encoding=mulaw&sample_rate=8000&container=none"
        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json"
        }
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(url, json={"text": text}, headers=headers)
                resp.raise_for_status()
                return resp.content
            except Exception as e:
                print(f"TTS Error: {e}")
                return None

# Singleton instance
deepgram_service = DeepgramService()
