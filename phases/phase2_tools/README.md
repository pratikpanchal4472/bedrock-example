# Phase 2 — ReAct Loop + Tools (Manual)

## Concept

This phase implements the **ReAct loop** (Reason + Act) manually in Python.
You will see exactly what every agent framework — LangChain, CrewAI, Bedrock Agents —
is doing under the hood.

```
User question
    ↓
1. Reason: Do I have the answer? Or do I need a tool?
    ↓ needs tool
2. Act: Call the right tool with correct parameters
    ↓
3. Observe: Read what the tool returned. Enough to answer?
    ↓ not enough → loop back to Reason
Final answer: Composed from all observations
```

## Key insights from this phase

**Tool descriptions are just text in the prompt.**
When Nova Lite decides to call `get_order_status("12345")` — it knows that function
exists because you injected its description into the system prompt as text. There is
no magic. Claude reads the description, reasons about it, and decides when to call it.

**Tool chaining happens automatically.**
For "Will it arrive before Friday?" — the agent makes THREE loops:
1. `get_order_status("12345")` → gets tracking ID ABC99
2. `get_delivery_estimate("ABC99")` → gets estimated delivery date
3. Composes final answer comparing date to Friday

The agent decided to chain tools on its own. You didn't hardcode this logic.

**Why you need Bedrock Agents (Phase 3).**
By the end of this phase you will have written ~80 lines of orchestration code:
- `while True` loop with no timeout or retry
- Manual `messages.append()` for every turn
- `if/elif` dispatcher for every tool
- Growing message list with no memory management

Phase 3 replaces all of that with one API call.

## Setup

No AWS console setup needed — tools run locally.

## Run

```bash
python phase2_tools.py
```

## Expected output

```
==================================================
User: Where is my order #12345?
==================================================
--- Loop 1: Calling Nova Lite ---
Stop reason: tool_use
Tool called: get_order_status
Tool input: {"order_id": "12345"}
Tool result: {"order_id": "12345", "status": "shipped", ...}
--- Loop 2: Calling Nova Lite ---
Stop reason: tool_use
Tool called: get_delivery_estimate
...
--- Loop 3: Calling Nova Lite ---
Stop reason: end_turn
Final answer: Your order #12345 has been shipped...
```

## What to observe

- Loop count — one user question triggers 3 separate LLM calls
- Tool chaining — tracking ID from loop 1 feeds into loop 2 automatically
- `stop_reason` — this is what drives the while loop logic
- Test 3 (order #00000) — watch whether the agent calls the tool or skips it
