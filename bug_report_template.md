# Bug Report - Pretty Good AI Agent

Use this document to track issues found during your 10 test calls.

## Summary Table

| Call ID | Scenario | Issue Type | Severity | Description |
|---------|----------|------------|----------|-------------|
| 1       | insurance_confusion | Hallucination | High | Agent confirmed it accepts "Global Health Plus" which doesn't exist. |
| 2       | scheduling_conflict | Business Logic | Med | Agent tried to schedule me at 6 PM on a Sunday. |
| ...     |          |            |          |             |

## Detailed Findings

### 1. Hallucination: Fake Insurance
- **Scenario**: `insurance_confusion`
- **Transcript Reference**: `transcripts/call_xxxx.txt`
- **Issue**: The agent confidently stated that the office accepts "Global Health Plus" insurance.
- **Recommended Fix**: Ensure the agent has a strictly grounded list of accepted insurance providers in its system prompt/knowledge base.

### 2. Lack of Empathy: Emergency Refill
- **Scenario**: `refill_emergency`
- **Issue**: When the patient expressed anxiety about being out of heart medication, the agent responded with a generic "I can help with that" without acknowledging the urgency or asking if the patient was currently in distress.
- **Recommended Fix**: Add a directive to prioritize empathy in high-anxiety medication scenarios.

### 3. Loop Failure: Vague Rescheduling
- **Scenario**: `reschedule_vague`
- **Issue**: When I said I didn't know my appointment date, the agent kept repeating "What date would you like to move it to?" instead of offering to look it up or asking for my name.
- **Recommended Fix**: Implement a fallback path for when a patient is missing key appointment details.
