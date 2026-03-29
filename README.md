# AWS Bedrock Agents POC — ShopEasy Order Assistant

A hands-on, phase-by-phase POC that explores every major AWS Bedrock concept by building a real e-commerce order assistant.

> **"Where is my order #12345, and will it arrive before my birthday on Friday?"**
> One question. Three reasoning loops. Real data. No hallucination.

---

## What you will build

A production-grade AI agent for **ShopEasy** — an Indian e-commerce platform — that:

- Tracks orders and delivery estimates via real tool calls
- Answers policy questions from a Knowledge Base (RAG)
- Remembers customers across sessions (cross-session memory)
- Blocks harmful inputs, PII, and prompt injection (Guardrails)

---

## Concepts covered

| Phase | Concept |
|-------|---------|
| 1 | Foundation Models — Bedrock Converse API |
| 2 | ReAct loop manually — tool chaining, message history |
| 3 | Bedrock Agents — managed orchestration, Lambda action groups |
| 4 | Knowledge Bases — RAG, vector search, S3 embeddings |
| 5 | AgentCore Memory — cross-session memory, session summarization |
| 6 | Guardrails — PII masking, denied topics, prompt injection defense |

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Guardrails                           │
│  ┌──────────────────────────────────────────────────┐  │
│  │           Bedrock Agent (orchestrator)           │  │
│  │         Runs ReAct loop · routes tools           │  │
│  └───────────┬─────────────┬──────────────┬─────────┘  │
│              │             │              │             │
│  ┌───────────▼──┐  ┌───────▼──────┐  ┌───▼──────────┐ │
│  │  Foundation  │  │    Action    │  │  Knowledge   │ │
│  │    Model     │  │    Groups    │  │    Base      │ │
│  │    (LLM)     │  │   (Lambda)   │  │  (S3+RAG)    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│              │                                          │
│  ┌───────────▼──────────┐  ┌───────────────────────┐  │
│  │   AgentCore Memory   │  │     Observability      │  │
│  │  Cross-session store │  │   CloudWatch traces    │  │
│  └──────────────────────┘  └───────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- AWS account with Bedrock access
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) or pip
- AWS CLI configured (`aws configure`)
- Node.js 18+ (for CDK)

---

## Quick start

```bash
# Clone the repo
git clone https://github.com/pratikpanchal4472/bedrock-example
cd bedrock-example

# Install Python dependencies
uv venv --python python3.12
source .venv/bin/activate
uv pip install -r requirements.txt

# Deploy infrastructure (Lambda + IAM)
cd infrastructure/sam
sam build && sam deploy --guided

# Run Phase 1
cd ../../phases/phase1_foundation
python phase1_foundation.py
```

---

## Phase-by-phase guide

Each phase has its own README with:
- Concept explanation
- Step-by-step console setup
- Working Python code
- Expected output

| Phase | Directory | README |
|-------|-----------|--------|
| 1 | `phases/phase1_foundation/` | [Phase 1 README](phases/phase1_foundation/README.md) |
| 2 | `phases/phase2_tools/` | [Phase 2 README](phases/phase2_tools/README.md) |
| 3 | `phases/phase3_bedrock_agent/` | [Phase 3 README](phases/phase3_bedrock_agent/README.md) |
| 4 | `phases/phase4_knowledge_base/` | [Phase 4 README](phases/phase4_knowledge_base/README.md) |
| 5 | `phases/phase5_memory/` | [Phase 5 README](phases/phase5_memory/README.md) |
| 6 | `phases/phase6_guardrails/` | [Phase 6 README](phases/phase6_guardrails/README.md) |

---

## Infrastructure

| Template | Purpose |
|----------|---------|
| `infrastructure/sam/template.yaml` | Lambda function + IAM roles |
| `infrastructure/cdk/` | Bedrock Agent + KB + Guardrail CDK stack |

---

## Cost estimate

Running all 6 phases end-to-end costs approximately **$0.50–$2.00** depending on model and number of test runs.
