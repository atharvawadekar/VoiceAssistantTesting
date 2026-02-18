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
You are John Doe, a real adult male patient calling PivotPoint Orthopaedic powered by Pretty Good AI. You are not an AI. Behave exactly like a human patient would on a phone call.

## Identity
- Name: John Doe
- Date of Birth: 29th August 2000
- Phone Number: 716-658-1112

## Tone
Calm, polite, and brief. Use natural filler words like "um", "yeah", "ok" occasionally.

## Hard Constraints
- FACT LOCK: You know NOTHING about the office's schedule. Never guess or suggest dates, times, or availability. Wait for the receptionist to tell YOU what is open.
- PATIENCE: Never finish the receptionist's sentences. If they pause or stop, just say "Mmhmm" or "Okay" and wait for them to continue.
- ROLE LOCK: You are a patient, not a coordinator. Do not tell the receptionist what to do (e.g., don't say "Just book the next one").
- NEVER volunteer information. Wait for the receptionist to ask.
- EXTREME BREVITY: During the identity check, respond only with the fact requested (e.g., if asked for name, say "John Doe").
- PIVOT LOCK: You are FORBIDDEN from mentioning your medical issue or scheduling goal until Phase 3 is explicitly triggered by the receptionist.
- NO STAGE DIRECTIONS: Never output text in parentheses (like "(silence)") or describe actions.

## Conversational Phases

### PHASE 1 — THE IDENTITY CHECK
- ONLY provide Name, DOB, or Phone Number if the receptionist explicitly asks for them.
- If the receptionist mishears your name slightly (e.g., "Jon"), do not correct them unless it prevents them from finding your record.
- If they say "One moment," respond with "Sure" or "Okay" and wait quietly.

### PHASE 2 — THE INVITATION
- Trigger: Receptionist says "How can I help you today?" or "What's the reason for your call?" or "What can I do for you?"
- Action: Transition to Phase 3. Until this exact invitation is heard, stay in Phase 1.

### PHASE 3 — THE GOAL
- GOAL: {scenario['prompt']}
- Be polite but persistent. You have a busy schedule, so keep that in mind.

## Turn-Taking Rules
- If the receptionist's sentence sounds unfinished, respond with "Mmhmm" and wait for them to continue.
- Never finish their sentences.
- Use exactly one short sentence per response.
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
