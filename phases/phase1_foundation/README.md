# Phase 1 — Foundation Models

## Concept

Before agents, tools, or any orchestration — you need to understand the raw foundation:
**just you, Python, and an LLM talking through Bedrock.**

A plain LLM is like a very smart person locked in a room with no phone and no internet.
They can only think and write from their training knowledge.

```
User question → LLM thinks → Response (from training only)
```

This phase teaches you the Bedrock Converse API — AWS's unified interface that works
across Claude, Nova, Llama, Titan, and Mistral with the same code. Swap one string
(the model ID) and everything else stays the same.

## Key insight

When you ask "Where is my order #12345?" — the LLM will either:
- Say it cannot look up orders (correct behavior)
- Make up a status (hallucination — this is what Phase 2 fixes)

Both outcomes are intentional teaching moments.

## Setup

No AWS console setup needed. Just configure your AWS credentials:

```bash
aws configure
# or set environment variables:
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

Make sure `amazon.nova-lite-v1:0` is enabled in:
**AWS Console → Bedrock → Model access → Manage model access**

## Run

```bash
python phase1_foundation.py
```

## Expected output

```
=== Test 1: Order lookup ===
{"inputTokens": 51, "outputTokens": 59, "totalTokens": 110}
Hi there! I'd be happy to help with order #12345...
[Notice: LLM either refuses or hallucinates — no real data]

=== Test 2: Return policy ===
{"inputTokens": 46, "outputTokens": 155, "totalTokens": 201}
Hello! Our return policy at ShopEasy allows you to return...
[Notice: LLM invents a policy — no real KB yet]
```

## What to observe

- `inputTokens` — your system prompt + user message consumed this many tokens
- `outputTokens` — the response used this many tokens
- Test 1 failure sets up WHY you need tools (Phase 2)
- Test 2 hallucination sets up WHY you need a Knowledge Base (Phase 4)
