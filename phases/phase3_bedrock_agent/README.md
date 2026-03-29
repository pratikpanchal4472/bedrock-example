# Phase 3 — Bedrock Agents (Managed Orchestration)

## Concept

Phase 2 required ~80 lines of orchestration code. Phase 3 replaces all of it with
**one API call** — and adds things you didn't even have to think about yet.

| Your manual code (Phase 2) | Bedrock Agents gives you |
|---|---|
| `while True` loop | Managed orchestration engine |
| `messages = []` reset | Session memory per user |
| `if/elif` tool dispatch | Auto tool routing via Lambda |
| Growing message list | Managed conversation history |
| No retry logic | Built-in retry + timeout |
| No multi-user support | Isolated sessions per sessionId |

**The alias → version pattern** is key for production:
- Draft: your working copy under development
- Version: a published snapshot
- Alias: a pointer to a version (e.g. `v1test → Version 1`)

This means you can update your agent safely while production traffic
keeps pointing to the stable alias. Instant rollback = change the alias pointer.

## Console setup (required before running Python)

### Step 1: Create Lambda function

1. Go to **AWS Console → Lambda → Create function**
2. Name: `shopease-order-tools`
3. Runtime: Python 3.12
4. Paste code from `lambda_handler.py`
5. Click **Deploy**

### Step 2: Create Bedrock Agent

1. Go to **Bedrock → Agents → Create Agent**
2. Name: `shopease-order-assistant`
3. Model: `Amazon Nova Lite v1:0` (or any supported model)
4. Instructions:
```
You are a helpful order assistant for ShopEasy, an Indian e-commerce platform.
Always use tools to look up real order data before answering.
Never guess or make up order statuses or delivery dates.
After receiving tool results, provide a complete and friendly answer.
If an order is not found, tell the customer clearly and ask them to verify.
```

### Step 3: Add Action Group

1. Scroll to **Action groups → Add**
2. Name: `order-actions`
3. Lambda: select `shopease-order-tools`
4. Add function `get_order_status` with parameter `order_id` (string, required)
5. Add function `get_delivery_estimate` with parameter `tracking_id` (string, required)

### Step 4: Lambda resource policy

Go to **Lambda → shopease-order-tools → Configuration → Permissions → Add**:
- Principal: `bedrock.amazonaws.com`
- Action: `lambda:InvokeFunction`

### Step 5: Prepare and publish

1. Click **Prepare** → wait for green banner
2. Test in console: "Where is my order #12345?"
3. Create alias: **Aliases → Create** → name `v1test` → point to Version 1
4. Note your Agent ID and Alias ID

## Configuration

Edit `phase3_bedrock_agent.py`:

```python
AGENT_ID       = "YOUR_AGENT_ID"       # e.g. VG2HLELRPO
AGENT_ALIAS_ID = "YOUR_ALIAS_ID"       # e.g. LJSNJASNL1
```

## Run

```bash
python phase3_bedrock_agent.py
```

## Expected output

```
Starting session: b5d91857-...
User: Where is my order #12345?
Agent: Your order #12345 has been shipped and is currently at the
Ahmedabad sorting facility with BlueDart...

User: Will it arrive before Friday?
Agent: Your order is estimated to arrive on Tuesday, 31 March 2026,
which is before Friday...

Starting NEW session: 5a9b1d38-...
User: Will it arrive before Friday?
Agent: Could you please provide your order ID so I can check the status?
```

## What to observe

- Turn 2 works without repeating the order ID — session memory in action
- New session (Turn 3) has zero context — correctly asks for order ID
- Your code is now 20 lines vs 80 lines in Phase 2
