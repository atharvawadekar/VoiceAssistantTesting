import httpx
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_ssl():
    print("🔍 Testing secure connections...")
    
    # Test Deepgram connectivity
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("https://api.deepgram.com/v1/projects")
            if resp.status_code in [200, 401]: # 401 is fine, it means SSL handshake worked but auth failed
                print("✅ SSL Connection to Deepgram: SUCCESS")
            else:
                print(f"⚠️ SSL Connection to Deepgram: Unexpected status {resp.status_code}")
        except Exception as e:
            print(f"❌ SSL Connection to Deepgram: FAILED ({e})")

    # Test OpenAI/Ollama (though local, it might use HTTPS if configured)
    # But usually Ollama is HTTP. Let's check a standard HTTPS site.
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get("https://google.com")
            print("✅ SSL Connection to Google: SUCCESS")
        except Exception as e:
            print(f"❌ SSL Connection to Google: FAILED ({e})")

if __name__ == "__main__":
    asyncio.run(test_ssl())
