import os
import io
from openai import AsyncOpenAI

# Load API Keys
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if OPENROUTER_API_KEY:
    print("🌐 Using OpenRouter (Cloud AI)")
    client = AsyncOpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY
    )
    # Default to Gemini 3 Flash via OpenRouter
    MODEL_NAME = "google/gemini-3-flash-preview"
else:
    print("🏠 Using Local Ollama (Llama 3.1)")
    client = AsyncOpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"
    )
    MODEL_NAME = "llama3.1:8b"

import json

# Global conversation history
conversation_history = []

def load_scenario(scenario_id="new_appointment"):
    """
    Loads a specific prompt from scenarios.json.
    """
    global conversation_history, current_scenario_id
    print(f"🧠 AI Loading Scenario ID: '{scenario_id}'")
    current_scenario_id = scenario_id
    try:
        with open("scenarios.json", "r") as f:
            scenarios = json.load(f)
            
        scenario = next((s for s in scenarios if s["id"] == scenario_id), scenarios[0])
        
        # Identity and Flow Context
        identity_context = f"""
## Role
You are John Doe, a patient calling PivotPoint Orthopaedic. You are NOT an AI assistant. You are a human on a phone call. 

## Identity
- Name: John Doe (DOB: Aug 29, 2000)
- Goal: {scenario['prompt']}

## Voice Guidelines (CRITICAL)
- BREVITY: Keep every response under 15 words and 1-2 short sentences. Customers can't "skim" audio.
- NATURAL FILLERS: Use "um", "actually", or "let me see" occasionally to sound human and cover processing lag.
- NO STACKING: Ask exactly one question at a time. Never ask two things in one turn.
- NUMBERS: If confirming a phone number, group them (e.g., "716... 658... 1112").

## Turn-Taking & Interruption
- BARGE-IN: If the receptionist starts speaking while you are talking, STOP immediately and listen. 
- ONE QUESTION: If the receptionist asks you a question, answer it immediately. Do not ignore it to push your own goal.
- PACING: NEVER respond to an unfinished thought. If the receptionist is listing options, wait until they ask a question before choosing.
- SIMPLICITY: Ask precisely ONE question at a time. Never "stack" questions.

## Conversational Phases
1. PHASE 1 (Identity): Provide only what is asked (Name, DOB). Do NOT volunteer your medical issue yet.
2. PHASE 2 (The Invitation): Wait for the receptionist to ask "How can I help you?" or similar.
3. PHASE 3 (The Goal): Only now state your request (from Goal section).

## Hard Guardrails
- FACT LOCK: You know nothing about the doctor's schedule. Never guess times. Wait for them to offer.
- NO STAGE DIRECTIONS: Never output text in parentheses like (smiling) or (pause).
- ROLE LOCK: If they ask about your "system" or "model," stay in character as a confused patient.
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
            model=MODEL_NAME,
            messages=conversation_history,
            max_tokens=500
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
