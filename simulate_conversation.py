"""
Simulates a conversation with the bot using the current system prompt.
Feed in the old transcript's USER lines and see how the new bot responds.
"""
import asyncio
from services.openai_service import load_scenario, get_chat_response

# The FIRST bad call transcript USER lines
OLD_TRANSCRIPT_LINES = [
    "Call may be recorded for quality and training purposes.",
    "Thanks for calling PivotPoint Orthopaedics.",
    "Orthopedics, part of Pretty Good AI. Am I speaking with John?",
    "Got it, John.",
    "Can you please tell me your date of birth?",
    "Just to confirm, I have your name as",
    "John Doe and your date of birth as August 2000. Is that correct?",
    "Would you like me to look up your record using your phone number?",
    "If so, please tell me the number you have on file with us. If you're not sure,",
    "I can confirm your",
]

async def simulate():
    load_scenario("scheduling")
    print("=" * 60)
    print("SIMULATION: New System Prompt vs Old Transcript")
    print("=" * 60)
    
    for line in OLD_TRANSCRIPT_LINES:
        print(f"\n[RECEPTIONIST]: {line}")
        reply = await get_chat_response(line)
        print(f"[BOT]:          {reply}")

if __name__ == "__main__":
    asyncio.run(simulate())
