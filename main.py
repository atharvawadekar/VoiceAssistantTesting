import os
import uvicorn
import json
import base64
import asyncio
import ssl
import websockets
import websockets.legacy.client
from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse, Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
from dotenv import load_dotenv

# 1. Twilio Voice Configuration
original_legacy_connect = websockets.legacy.client.connect
def patched_connect(*args, **kwargs):
    if 'ssl' not in kwargs:
        kwargs['ssl'] = ssl.create_default_context()
    return original_legacy_connect(*args, **kwargs)
websockets.legacy.client.connect = patched_connect
websockets.connect = patched_connect

load_dotenv()

from services.deepgram_service import deepgram_service
from services.openai_service import get_chat_response

app = FastAPI()

print(f"🚀 Starting Voice Bot on port {os.getenv('PORT', 5000)}...")

PORT = int(os.getenv("PORT", 5000))

@app.get("/", response_class=HTMLResponse)
async def index():
    return "<h1>Voice Bot Server is Running!</h1>"

@app.api_route("/voice", methods=["GET", "POST"])
async def voice(request: Request):
    """
    Twilio hits this endpoint when the call connects.
    """
    host = request.headers.get("host")
    scenario = request.query_params.get("scenario", "new_appointment")
    print(f"📞 Incoming Call Webhook. Params: {request.query_params}, Resulting Scenario: {scenario}")
    
    response = VoiceResponse()
    connect = Connect()
    stream = Stream(url=f"wss://{host}/ws")
    stream.parameter(name="scenario", value=scenario)
    connect.append(stream)
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Scenario will be loaded from the 'start' message parameters
    print("🔌 WebSocket Connected. Waiting for start message...")
    
    from services.openai_service import load_scenario, save_transcript
    
    stream_sid = None
    
    # 1. Start Deepgram Connection
    try:
        # Get the context manager
        dg_cm = await deepgram_service.create_stt_connection()
        
        # Ensure we are using it as an async context manager
        async with dg_cm as dg_connection:
            print("🚀 Deepgram STT Connected")
            
            # 2. Define Event Handlers
            # We need to listen to messages from Deepgram
            # The SDK expects us to register handlers on the connection object?
            # Or does start_listening emit them? 
            # Looking at SDK code, it emits using EventEmitterMixin.
            
            # We can also just hook into the 'message' event if we use start_listening()
            # BUT start_listening() is blocking. So we run it in a task.
            
            async def on_deepgram_message(message, **kwargs):
                try:
                    if hasattr(message, 'channel'):
                        transcript = message.channel.alternatives[0].transcript
                        if transcript and len(transcript.strip()) > 0:
                            if message.is_final:
                                print(f"🗣️ User: {transcript}")
                                print(f"🧠 Asking AI: {transcript}")
                                reply = await get_chat_response(transcript)
                                print(f"🤖 Bot: {reply}")
                                
                                # TTS
                                print(f"🔊 Generating TTS for: {reply}")
                                audio_data = await deepgram_service.text_to_speech(reply)
                                if audio_data:
                                    print(f"✅ TTS Generated ({len(audio_data)} bytes)")
                                    # Send to Twilio
                                    payload = base64.b64encode(audio_data).decode("utf-8")
                                    await websocket.send_json({
                                        "event": "media",
                                        "streamSid": stream_sid,
                                        "media": {
                                            "payload": payload
                                        }
                                    })
                except Exception as e:
                    print(f"❌ Error in on_deepgram_message: {e}")

            # Register handler
            dg_connection.on("message", on_deepgram_message)
            
            # 3. Start Listener Task (Non-blocking)
            # The SDK's start_listening() is async and loops forever.
            listener_task = asyncio.create_task(dg_connection.start_listening())
            
            # 4. Loop Twilio Messages
            try:
                while True:
                    data = await websocket.receive_json()
                    
                    if data['event'] == 'start':
                        stream_sid = data['start']['streamSid']
                        print(f"📞 Stream started: {stream_sid}")
                        
                        # Extract scenario from custom parameters
                        custom_params = data['start'].get('customParameters', {})
                        scenario_id = custom_params.get('scenario', 'new_appointment')
                        print(f"🎭 Loading Scenario from Twilio Params: {scenario_id}")
                        load_scenario(scenario_id)
                        
                    elif data['event'] == 'media':
                        media_payload = base64.b64decode(data['media']['payload'])
                        # Send to Deepgram
                        await dg_connection.send_media(media_payload)
                        
                    elif data['event'] == 'stop':
                        print("🛑 Stream stopped")
                        break
                        
            except Exception as e:
                print(f"❌ WebSocket Error: {e}")
            finally:
                # Cancel listener task when Twilio hangs up
                listener_task.cancel()
                try:
                    await listener_task
                except asyncio.CancelledError:
                    pass

    except Exception as e:
        print(f"❌ Deepgram Connection Error: {e}")
    finally:
        if stream_sid:
            save_transcript(stream_sid)
        print("🔌 WebSocket Disconnected")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
