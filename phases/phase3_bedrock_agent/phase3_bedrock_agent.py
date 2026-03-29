"""
Phase 3 — Invoke Bedrock Agent
Replace all 80 lines of Phase 2 orchestration with one API call.
"""

import boto3
import uuid

bedrock_agent = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1"
)

# Get these from the Bedrock console:
# Agent Details page → Agent ID
# Aliases tab → Alias ID
AGENT_ID       = "YOUR_AGENT_ID"        # e.g. VG2HLELRPO
AGENT_ALIAS_ID = "YOUR_ALIAS_ID"        # e.g. LJSNJASNL1


def ask_agent(user_message: str, session_id: str) -> str:
    """
    Invoke a Bedrock Agent.
    session_id ties messages together — agent remembers context within
    the same session. This is what you had to manage manually in Phase 2.
    """
    print(f"\n{'='*50}")
    print(f"Session: {session_id[:8]}...")
    print(f"User: {user_message}")
    print(f"{'='*50}")

    response = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        inputText=user_message
    )

    # Response comes back as a streaming event — collect all chunks
    full_response = ""
    for event in response["completion"]:
        if "chunk" in event:
            full_response += event["chunk"]["bytes"].decode("utf-8")

    print(f"Agent: {full_response}")
    return full_response


if __name__ == "__main__":
    # ── Session 1: multi-turn conversation ──
    session_id = str(uuid.uuid4())
    print(f"Starting session: {session_id}")

    # Turn 1: agent looks up order, chains tools
    ask_agent("Where is my order #12345?", session_id)

    # Turn 2: agent remembers #12345 — no need to repeat it
    ask_agent("Will it arrive before Friday?", session_id)

    # ── Session 2: new session, memory resets ──
    new_session = str(uuid.uuid4())
    print(f"\nStarting NEW session: {new_session}")

    # Without session memory, agent must ask for order ID
    ask_agent("Will it arrive before Friday?", new_session)
