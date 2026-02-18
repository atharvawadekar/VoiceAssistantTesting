import os
import io
from openai import AsyncOpenAI

client = AsyncOpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # Placeholder key for Ollama
)

import json

# Global conversation history
conversation_history = []

def load_scenario(scenario_id="scheduling"):
    """
    Loads a specific prompt from scenarios.json.
    """
    global conversation_history, current_scenario_id
    current_scenario_id = scenario_id
    try:
        with open("scenarios.json", "r") as f:
            scenarios = json.load(f)
            
        scenario = next((s for s in scenarios if s["id"] == scenario_id), scenarios[0])
        
        # Identity and Flow Context
        identity_context = f"""
You are John Doe, a patient calling the front desk receptionist at PivotPoint Orthopaedic. You are not an AI.

Your details (only share when asked):
- Name: John Doe
- Date of Birth: 29th August 2000
- Phone Number: 716-658-1112

Your reason for calling: {scenario['prompt']}

Rules:
- Be brief and natural. One short sentence at a time.
- Answer whatever the receptionist asks (name, DOB, phone number) when they ask for it.
- Do NOT mention your reason for calling until the receptionist asks "How can I help you?" or "What's the reason for your call?"
- If the receptionist is mid-sentence or pauses, just say "Mmhmm" and wait.
- Never make up information. If you don't know something, say "I'm not sure."
- Never output stage directions or actions in parentheses.
"""
        
        # Reset history
        conversation_history = [
            {"role": "system", "content": identity_context}
        ]
        print(f"🎭 Scenario Loaded: {scenario['name']} (Identity: John Doe)")
    except Exception as e:
        print(f"❌ Error loading scenario: {e}")
        conversation_history = [{"role": "system", "content": "You are a patient calling a medical office."}]

def save_transcript(stream_sid):
    """
    Save the current conversation history to a file.
    """
    if not os.path.exists("transcripts"):
        os.makedirs("transcripts")
        
    filename = f"transcripts/call_{current_scenario_id}_{stream_sid}.txt"
    try:
        with open(filename, "w") as f:
            for msg in conversation_history:
                role = msg["role"].upper()
                content = msg["content"]
                f.write(f"[{role}]: {content}\n")
        print(f"📄 Transcript saved: {filename}")
    except Exception as e:
        print(f"❌ Error saving transcript: {e}")

# Initialize with default
load_scenario()

async def get_chat_response(text_input):
    """
    Get response from local Ollama (Llama 3.1)
    """
    try:
        conversation_history.append({"role": "user", "content": text_input})
        
        response = await client.chat.completions.create(
            model="llama3.1:8b",
            messages=conversation_history
        )
        
        reply = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print(f"❌ OpenAI Chat Error: {e}")
        return f"Error: {e}"

async def transcribe_audio(audio_bytes):
    """
    Transcribe audio using OpenAI Whisper.
    Input: Audio bytes (wav/pcm)
    Output: Text string
    """
    try:
        # OpenAI requires a file-like object with a name
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav" 
        
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
        return transcript.text
    except Exception as e:
        print(f"Transcription Error: {e}")
        return None

async def text_to_speech(text):
    """
    Convert text to speech using OpenAI TTS.
    Returns raw audio bytes (pcm).
    """
    try:
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format="pcm" 
        )
        return response.content
    except Exception as e:
        print(f"TTS Error: {e}")
        return None
