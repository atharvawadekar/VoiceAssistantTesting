import os
import ssl
import websockets
import websockets.legacy.client

# Capture original before patching
original_legacy_connect = websockets.legacy.client.connect

def patched_connect(*args, **kwargs):
    if 'ssl' not in kwargs:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl'] = ctx
    return original_legacy_connect(*args, **kwargs)

# Patch
websockets.legacy.client.connect = patched_connect
websockets.connect = patched_connect

from dotenv import load_dotenv
load_dotenv()

from deepgram import AsyncDeepgramClient

api_key = os.getenv("DEEPGRAM_API_KEY")
client = AsyncDeepgramClient(api_key=api_key)

print(f"Client type: {type(client)}")
print(f"Listen type: {type(client.listen)}")
print(f"V1 type: {type(client.listen.v1)}")
print(f"Connect type: {type(client.listen.v1.connect)}")

import contextlib
try:
    with client.listen.v1.connect(model="nova-2"):
        print("Successfully used sync 'with'")
except TypeError as e:
    print(f"Sync 'with' failed: {e}")

async def check_async():
    try:
        async with client.listen.v1.connect(model="nova-2"):
            print("Successfully used 'async with'")
    except TypeError as e:
        print(f"Async 'with' failed: {e}")

import asyncio
if __name__ == "__main__":
    asyncio.run(check_async())
