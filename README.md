# 🩺 Voice Bot - Patient Simulation Suite

An automated voice bot built for the Pretty Good AI Engineering Challenge. It acts as a "patient" to test, stress-test, and find bugs in medical AI agents.

## 🚀 Quick Start (One Command To Rule Them All)

1. **Install Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Setup SSL (Mac Only)**:
   ```bash
   /Applications/Python\ 3.13/Install\ Certificates.command
   ```

3. **Configure Environment**:
   Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   # Add your TWILIO and DEEPGRAM keys
   ```

4. **Start the Tunnels**:
   ```bash
   ngrok http 6000
   ```

5. **Run the Bot**:
   In separate terminals:
   * **Server**: `python main.py`
   * **Sync Webhook**: `python update_webhook.py [YOUR_NGROK_URL]`
   * **Trigger Call**: `python trigger_call.py +18054398008 --scenario scheduling_conflict`

## 🎭 Scenarios
You can trigger different patient types by passing the `--scenario` flag:
- `scheduling`: Inflexible patient — only available Fridays after 3 PM. Tests scheduling flexibility.
- `rescheduling`: Frustrated patient — needs to move an appointment for the second time. Tests empathy.
- `refill`: Confused and urgent patient — needs a medication refill but is unsure of the dosage. Tests accuracy.
- `info`: Curious patient — asks about holiday hours and insurance coverage. Tests knowledge and policy handling.

## 📄 Transcripts
All conversations are saved to the `transcripts/` folder. Review these files to identify and document bugs.

## 🏗 Architecture & Design

The system relies on a real-time **WebSocket** connection to stream audio between the phone call and your local computer.

```mermaid
sequenceDiagram
    participant User as You (on Phone)
    participant Twilio as Twilio Cloud
    participant Ngrok as Ngrok Tunnel
    participant Server as Local Python Server
    
    User->>Twilio: Speaks into phone
    Twilio->>Ngrok: Streams Audio (WebSocket)
    Ngrok->>Server: Forwards Audio
    Server->>Server: 1. Transcribe (Deepgram Nova-2)
    Server->>Server: 2. Think (Ollama Llama 3.1 8B)
    Server->>Server: 3. Speak (Deepgram Aura)
    Server->>Ngrok: Sends Audio Response
    Ngrok->>Twilio: Forwards Audio
    Twilio->>User: Plays Audio on Phone
```

### Why we need these pieces:
1.  **Local Python Server (`main.py`)**: This is the "brain". It runs on your laptop. Twilio cannot see your laptop directly.
2.  **Ngrok**: This is a "tunnel". It gives your laptop a public address so Twilio *can* see it.
3.  **Twilio**: Connects the traditional phone network to the internet. It takes the audio from the phone and streams it to our URL.
4.  **WebSockets**: A special type of internet connection that stays open, allowing audio to flow back and forth instantly.

---

## 📂 Component Breakdown

### Core Logic
- **`main.py`**: The FastAPI entry point. Exposes a `/voice` webhook for Twilio and a `/ws` websocket endpoint for the media stream.
- **`services/deepgram_service.py`**: Handles both Speech-to-Text (STT) and Text-to-Speech (TTS) using Deepgram's low-latency API.
- **`services/openai_service.py`**: Handles the "Brain" logic using **Llama 3.1 (via Ollama)**. Code-compatible with OpenAI but runs locally and for free.

### Scripts & Data
- **`trigger_call.py`**: A CLI script to initiate calls and select specific scenarios.
- **`update_webhook.py`**: A helper script to update Twilio's webhook URL when ngrok restarts.
- **`scenarios.json`**: A library of patient personas and medical goals.
- **`transcripts/`**: Automated storage for every call interaction for later analysis.

---

## 🛠 Features
- **Ollama Integration**: Runs locally on Llama 3.1 for free, private, and unlimited testing.
- **Dynamic Personas**: Easy to extend via `scenarios.json`.
- **Low Latency**: Sub-second response times using Deepgram's streaming STT/TTS.

---

## 🎬 Explanation (3-Minute Video Script)

### What is this project? *(~30 seconds)*
This is a **Voice Bot Patient Simulator** — an automated AI that calls a medical AI agent and pretends to be a real patient. The goal is to stress-test the AI agent by simulating realistic, tricky conversations: scheduling conflicts, medication refills, insurance questions, and more.

### Why does it exist? *(~30 seconds)*
Testing a voice AI agent manually is slow and expensive. You'd need a human to call in every time. This bot replaces that human — it can call the agent automatically, hold a realistic conversation, and save a full transcript for review. It runs entirely for free on your local machine using Ollama.

### How does it work? *(~60 seconds)*
1. You run `trigger_call.py` and choose a patient scenario (e.g., "scheduling").
2. Twilio places an outbound call to the target AI agent.
3. The agent's speech is streamed in real-time to your local Python server via a WebSocket tunnel (Ngrok).
4. **Deepgram Nova-2** transcribes the speech to text in under 300ms.
5. **Llama 3.1 8B (via Ollama)** reads the transcript and generates a realistic patient response, guided by a carefully engineered system prompt.
6. **Deepgram Aura** converts that response back to natural-sounding speech.
7. The audio is sent back to Twilio, and the agent hears the patient speak.
8. Every call is saved automatically to the `transcripts/` folder.

### What makes it smart? *(~30 seconds)*
The bot uses a **Phase-Based Prompt System**:
- **Phase 1 (Check-In)**: It only gives its name and date of birth when asked — it doesn't volunteer information.
- **Phase 2 (Wait)**: It stays silent when the agent is typing or looking up records.
- **Phase 3 (Goal)**: Only after the agent says "How can I help you?" does it reveal the reason for the call.

This makes it behave like a real, patient human caller — not a chatbot.

### What did we find? *(~30 seconds)*
By running multiple calls, we were able to identify real bugs in the target AI agent: hallucinated time slots, misheard names, and premature responses. All findings are documented in the transcripts for review.
