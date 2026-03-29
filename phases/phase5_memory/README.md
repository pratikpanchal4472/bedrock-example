# Phase 5 — AgentCore Memory (Cross-Session)

## Concept

Session memory (Phase 3) = agent remembers within one session, forgets when session ends.
AgentCore Memory = agent remembers across completely separate sessions.

```
Visit 1 (session_id: abc):
  User: "Where is order #12345?"
  Agent: [looks it up, answers]
  → Session ends → Bedrock summarizes → stores against memoryId

Visit 2 (session_id: xyz, days later):
  User: "Did my order arrive?"
  Agent: [loads memory summary] "Your order #12345 is estimated..."
  → Agent knew which order without being told
```

**Key parameters:**
- `sessionId` — ties turns within one conversation (changes each visit)
- `memoryId` — ties sessions to one customer (stays the same forever)

You define `memoryId` yourself — it's just a string you choose.
Bedrock stores session summaries against this key in managed DynamoDB.

**endSession=True** triggers the async summarization job.
Without it, memory is only saved when the idle session timeout fires (10 min).
Always end sessions explicitly in production.

**Memory settings (configured in Agent Builder):**
- `storageDays`: how long summaries persist (1–365 days)
- `maxRecentSessions`: how many past sessions inject into each new prompt
  (caps context window growth — solves the "50 sessions" bloat problem)
- Summarization prompt: customisable — control what gets remembered

## Prerequisites

- Memory enabled on agent (Agent Builder → Memory → Enable session summarization)
- Published version alias (memory does NOT work on DRAFT alias)
- `storageDays`: 30, `maxRecentSessions`: 20

## Setup

1. In Agent Builder, enable memory and set storage to 30 days
2. Save and exit → Prepare
3. Create new version → Create alias `v3_memory`
4. Update `AGENT_ALIAS_ID` below with the new alias ID

## Run

```bash
python phase5_memory.py
```

## Expected output

```
VISIT 1 — First session
User: Where is my order #12345?
Agent: Your order #12345 has been shipped...
User: Will it arrive before Friday?
Agent: Your order is estimated to arrive Tuesday...
[Session ended — memory summarization triggered]

Stored memory:
  summaryText: "The user asked about order #12345 status and delivery.
  Assistant called get_order_status and get_delivery_estimate.
  Order is shipped via BlueDart, estimated Tuesday 31 March."

VISIT 2 — New session, same customer
User: Did my order arrive yet?
Agent: Your order #12345 has not arrived yet — estimated Tuesday 31 March...
[Agent knew order #12345 from memory — not told in this session]
```

## What to observe

- `get_agent_memory()` — inspect the stored summary directly via API
- Visit 2 first question has no order ID — memory bridged the gap
- `sessionExpiryTime` in memory response — the TTL from your storageDays setting
