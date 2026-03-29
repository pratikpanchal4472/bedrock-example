# Phase 4 — Knowledge Base (RAG)

## Concept

RAG = Retrieval Augmented Generation.
Instead of stuffing entire policy documents into every prompt (context bloat),
RAG converts documents into vectors and retrieves only the relevant chunks.

```
Ingestion (once):
PDF → Chunked → Embedding model → Vectors stored in S3/OpenSearch

Query (every request):
Customer question → Embedding model → Vector search → Top 3 chunks → LLM answer
```

**Same embedding model used twice** — this is the key insight:
- During ingestion: converts document chunks to vectors (stored)
- During query: converts customer question to vector (compared against stored vectors)

Vector similarity finds meaning matches, not just keyword matches.
"Return electronics" matches "Refund rules for gadgets" even with no common words.

The Knowledge Base is treated as a **tool** by the agent — it appears in the
orchestration trace the same way a Lambda tool call does.

## Setup

### Step 1: Upload policy document to S3

1. Create S3 bucket: `shopease-knowledge-base-YOUR_ACCOUNT_ID`
2. Upload `../../knowledge_base_docs/shopease_policy.txt`

### Step 2: Create Knowledge Base

1. **Bedrock → Knowledge Bases → Create**
2. Name: `shopease-policy-kb`
3. Data source: your S3 bucket
4. Embedding model: `Titan Text Embeddings V2`
5. Vector store: Quick create (OpenSearch Serverless) or S3 vectors
6. Click **Create** → wait 2-3 minutes

### Step 3: Sync data source

1. Click into your KB → **Data sources → Sync**
2. Wait for `Sync complete`

### Step 4: Test KB standalone

In KB console → **Test Knowledge Base**:
```
What is the return policy for electronics?
```
You should see the relevant chunk retrieved with a relevance score.

### Step 5: Attach KB to agent

1. **Agent Builder → Knowledge Bases → Add**
2. Select `shopease-policy-kb`
3. Instruction:
```
Use this knowledge base to answer questions about ShopEasy's
return policy, shipping policy, cancellation policy, and warranty.
Always search this knowledge base before answering any policy question.
```
4. **Save and exit → Prepare**

## Run

```bash
python phase4_knowledge_base.py
```

## Expected output

```
User: What is the return policy for electronics?
Agent: ShopEasy allows returns for electronics within 7 days of delivery,
provided the item is unopened...
[Answer grounded in your actual document — not invented]

User: What about for clothing?
Agent: For clothing, ShopEasy allows returns within 30 days...
[Same session — agent remembers this is a follow-up]
```

## What to observe in the trace

Look for `invocationType: KNOWLEDGE_BASE` in the console trace.
You will see:
- The search query the agent generated
- The chunks retrieved with relevance scores
- The S3 source URI the chunks came from

This is RAG made visible.
