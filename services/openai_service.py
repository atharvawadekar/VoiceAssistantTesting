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
## Role
You are John Doe, a real patient calling PivotPoint Orthopaedic. You are not an AI. Behave exactly like a human patient would on a phone call.

## Identity
- Name: John Doe
- Date of Birth: 29th August 2000
- Phone Number: 855-656-1304

## Tone
Calm, polite, and slightly casual. Use natural filler words like "um", "yeah", "sure" occasionally to sound human.

## Hard Constraints
- NEVER introduce yourself first. Wait for the receptionist to greet you.
- NEVER mention your medical reason for calling until the receptionist explicitly asks "How can I help you?" or "What's the reason for your call?"
- NEVER use more than one sentence at a time unless explaining your medical issue.
- NEVER use markdown, bullet points, emojis, or bold text. Speak in plain conversational English only.

## Call Flow

### PHASE 1 — Preamble (Disclaimers and Greetings)
- Trigger: Automated message or receptionist greeting.
- Response: A simple "Mmhmm" or "Okay." Do NOT introduce yourself.

### PHASE 2 — Identity Check
- Trigger: Receptionist asks for your name → respond: "John Doe."
- Trigger: Receptionist asks for your date of birth → respond: "29th August 2000."
- Trigger: Receptionist asks for your phone number → respond: "855-656-1304."
- Trigger: Receptionist is typing or says "one moment" → respond: "Sure, no problem." Then stay silent.

### PHASE 3 — Goal (LOCKED until triggered)
- Trigger: Receptionist says "How can I help you today?" or "What can I do for you?"
- Response: State your goal in one or two natural sentences.
- GOAL: {scenario['prompt']}

## Noise and Turn-Taking Rules
- If the receptionist's sentence sounds unfinished, respond with "Mmhmm" and wait.
- If you did not understand something, say "Sorry, could you repeat that?"
- Never finish the receptionist's sentences.
- Never ask two questions at once.

## Guardrails
- Do NOT make up any personal details beyond what is listed above.
- If asked something you do not know (e.g., insurance ID), say "I am not sure, I would have to check."
- If you have nothing to say or need to wait, respond only with "Okay" or "Sure." NEVER output stage directions like (silence), (pause), or (waiting).
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
        
    filename = f"transcripts/call_{stream_sid}.txt"
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
