"""
Phase 4 — Knowledge Base (RAG)
Policy questions now answered from real documents, not invented by the LLM.
Same invoke_agent call — KB is wired up in the console.
"""

import boto3
import uuid

bedrock_agent = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1"
)

AGENT_ID       = "YOUR_AGENT_ID"
AGENT_ALIAS_ID = "YOUR_ALIAS_ID"


def ask_agent(user_message: str, session_id: str) -> str:
    print(f"\nUser: {user_message}")

    response = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=user_message
    )

    full_response = ""
    for event in response["completion"]:
        if "chunk" in event:
            full_response += event["chunk"]["bytes"].decode("utf-8")

    print(f"Agent: {full_response}")
    return full_response


if __name__ == "__main__":
    # ── Session 1: order tool chaining (same as Phase 3) ──
    order_session = str(uuid.uuid4())
    ask_agent("Where is my order #12345?", order_session)
    ask_agent("Will it arrive before Friday?", order_session)

    # ── Session 2: KB questions — grounded in real document ──
    policy_session = str(uuid.uuid4())
    ask_agent("What is the return policy for electronics?", policy_session)

    # Follow-up in same session — agent remembers we are discussing policy
    ask_agent("What about for clothing?", policy_session)
