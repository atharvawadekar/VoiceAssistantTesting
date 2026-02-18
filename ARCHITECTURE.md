# Architecture: Voice Bot Challenge

## Overview
This system is an automated voice-based "patient" designed to test medical AI agents by simulating realistic conversation scenarios. It uses a real-time, low-latency audio loop to interact over traditional phone lines.

## Technical Stack
- **Telephony**: [Twilio](https://www.twilio.com/) (Handles PSTN to WebSocket streaming).
- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous Python server).
- **STT (Speech-to-Text)**: [Deepgram Nova-2](https://www.deepgram.com/) (Chosen for <300ms latency and high accuracy with medical terminology).
- **LLM (The Brain)**: [Ollama / Llama 3.1:8b](https://ollama.com/) (Local execution to ensure zero cost and high privacy during extensive testing).
- **TTS (Text-to-Speech)**: [Deepgram Aura](https://www.deepgram.com/) (Optimized for human-like conversational speed).

## Key Design Choices

### 1. Unified Deepgram Integration
Instead of mixing providers (e.g., Whisper + Google TTS), we use Deepgram for both STT and TTS. This reduces the number of network hops and ensures audio formats (MuLaw 8khz) are consistent with Twilio’s requirements, minimizing latency.

### 2. Local LLM via Ollama
To satisfy the "stress-testing" requirement (Minimum 10 calls), we use Ollama. This allows for unlimited iterations without hitting OpenAI API quotas or incurring variable costs, making the testing suite significantly more robust.

### 3. State-Managed Scenarios
Patient personas are externalized in `scenarios.json`. This decoupling allows for adding new test cases without touching core logic. The persona is pushed into the model's system context at the start of each call to ensure consistent behavior.

### 4. Automated Transcription
Every call is automatically recorded to the `transcripts/` directory. This creates an audit trail for bug reporting and quality evaluation, as required by the challenge.

## Communication Flow
1. **Twilio** streams MuLaw 8000Hz audio to our **WebSocket**.
2. **Deepgram STT** transcribes the stream in real-time.
3. **Llama 3.1** processes the "is_final" transcript and generates a response.
4. **Deepgram TTS** converts the response to MuLaw bytes.
5. **FastAPI** sends the audio bytes back to Twilio via JSON WebSocket messages.
