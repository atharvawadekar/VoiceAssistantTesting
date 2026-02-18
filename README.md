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
- `scheduling_conflict`: Tests inflexible scheduling.
- `insurance_confusion`: Tests for hallucinations regarding insurance.
- `refill_emergency`: Tests empathy and urgency.
- `reschedule_vague`: Tests handling of missing information.
- `office_hours_edge`: Tests calendar/holiday knowledge.

## 📄 Transcripts
All conversations are saved to the `transcripts/` folder. Review these files to identify and document bugs.

## 🛠 Features
- **Ollama Integration**: Runs locally on Llama 3.1 for free, private, and unlimited testing.
- **Dynamic Personas**: Easy to extend via `scenarios.json`.
- **Low Latency**: Sub-second response times using Deepgram's streaming STT/TTS.
