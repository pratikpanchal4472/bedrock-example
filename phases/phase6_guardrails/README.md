# Phase 6 — Guardrails

## Concept

**System prompt = training manual** → relies on model judgment → can fail.
**Guardrails = interceptor layer** → enforces rules on every response → cannot fail.

```
Without Guardrails:
User → Agent → LLM → Response → User

With Guardrails:
User → Guardrails → Agent → LLM → Response → Guardrails → User
         ↑                                          ↑
    blocks bad input                         blocks bad output
```

Guardrails sits on BOTH sides — it does not matter how well the model reasoned.
If the output violates a rule, it is blocked and replaced before the customer sees it.

**Five types of protection:**

| Type | What it does | Our config |
|------|-------------|------------|
| Content filters | Blocks hate, violence, sexual content | High on all |
| Denied topics | Blocks specific subjects | Competitor comparison |
| Word filters | Blocks specific phrases | "guaranteed refund" |
| PII detection | Masks sensitive data | Credit cards, phones |
| Grounding check | Detects hallucination | 0.7 threshold |

The grounding check is the most powerful for our use case.
It compares the agent's response against the actual tool results and KB chunks.
If the answer isn't grounded in real data, it gets blocked.
This would have caught the invented "automatic refund" sentence in Phase 4.

## Setup

### Step 1: Create Guardrail

1. **Bedrock → Guardrails → Create Guardrail**
2. Name: `shopease-guardrail`

**Content filters page:**
Set all categories to High for both input and output.

**Denied topics page — add two topics:**

Topic 1:
- Name: `competitor-comparison`
- Definition: `Any comparison of ShopEasy to competitor platforms like Amazon, Flipkart, or Meesho`
- Type: DENY

Topic 2:
- Name: `unverified-refund-promises`
- Definition: `Any claim that ShopEasy will automatically issue refunds or guarantees not stated in policy`
- Type: DENY

**Word filters page — add:**
```
guaranteed refund
automatic refund
we will compensate
```

**PII page:**
Enable: Email, Phone, Credit card — Action: ANONYMIZE

**Grounding check page:**
- Grounding threshold: 0.7
- Relevance threshold: 0.7

3. Click **Create Guardrail** → note the Guardrail ID

### Step 2: Attach to agent

1. **Agent Builder → Additional settings → Guardrails**
2. Select `shopease-guardrail`
3. **Save and exit → Prepare**

## Run

```bash
python phase6_guardrails.py
```

## Expected output

```
Test 1: Normal order — PASS
Agent: Your order #12345 has been shipped...

Test 2: Policy question — PASS (grounded in KB)
Agent: ShopEasy allows returns for electronics within 7 days...

Test 3: Competitor — BLOCKED
[GUARDRAIL INTERVENED]
Agent: Sorry, the model cannot answer this question.

Test 4: Credit card — BLOCKED (PII)
[GUARDRAIL INTERVENED]
Agent: Sorry, the model cannot answer this question.

Test 5: Prompt injection — BLOCKED
[GUARDRAIL INTERVENED]
Agent: Sorry, the model cannot answer this question.
```

## What to observe in the trace

The `guardrailTrace` event shows:
- `action`: PASS or INTERVENED
- `topicPolicy.topics`: which denied topic triggered
- `wordPolicy`: which word filter matched
- `sensitiveInformationPolicy`: which PII type was detected
