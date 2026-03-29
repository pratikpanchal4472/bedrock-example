"""
Phase 5 — AgentCore Memory (Cross-Session)
The agent remembers customers across completely separate sessions.
"""

import boto3
import uuid
import time

bedrock_agent = boto3.client(
    service_name="bedrock-agent-runtime",
    region_name="us-east-1"
)

# Must be a PUBLISHED VERSION alias — memory does not work on DRAFT
AGENT_ID       = "YOUR_AGENT_ID"
AGENT_ALIAS_ID = "YOUR_V3_MEMORY_ALIAS_ID"  # e.g. HCYP1UYNKB


def ask_agent(
    user_message: str,
    session_id: str,
    memory_id: str,
    end_session: bool = False
) -> str:
    """
    memory_id ties sessions to one customer.
    Different session_id = new conversation.
    Same memory_id = same customer — agent remembers across sessions.
    """
    print(f"\nUser: {user_message}")

    response = bedrock_agent.invoke_agent(
        agentId=AGENT_ID,
        agentAliasId=AGENT_ALIAS_ID,
        sessionId=session_id,
        memoryId=memory_id,
        inputText=user_message,
        endSession=end_session  # triggers async memory summarization
    )

    full_response = ""
    for event in response["completion"]:
        if "chunk" in event:
            full_response += event["chunk"]["bytes"].decode("utf-8")

    print(f"Agent: {full_response}")
    return full_response


def get_memory(memory_id: str) -> list:
    """Inspect what Bedrock stored for this customer."""
    try:
        response = bedrock_agent.get_agent_memory(
            agentId=AGENT_ID,
            agentAliasId=AGENT_ALIAS_ID,
            memoryId=memory_id,
            memoryType="SESSION_SUMMARY"
        )
        return response.get("memoryContents", [])
    except Exception as e:
        print(f"[Memory fetch error: {e}]")
        return []


if __name__ == "__main__":
    # memoryId — you define this per customer, any string 2-100 chars
    CUSTOMER_MEMORY_ID = "pratik001"

    # ── Visit 1: first conversation ──
    print("\n" + "█"*50)
    print("VISIT 1 — First session")
    print("█"*50)
    session_1 = str(uuid.uuid4())

    ask_agent("Where is my order #12345?", session_1, CUSTOMER_MEMORY_ID)
    ask_agent("Will it arrive before Friday?", session_1, CUSTOMER_MEMORY_ID)

    # endSession=True triggers memory summarization asynchronously
    print("\n[Ending session — triggering memory summarization...]")
    ask_agent("Thanks, goodbye!", session_1, CUSTOMER_MEMORY_ID, end_session=True)

    # Summarization is async — wait for it to complete
    print("[Waiting 30s for summarization...]")
    time.sleep(30)

    # Inspect what was stored
    print("\n[Stored memory:]")
    memories = get_memory(CUSTOMER_MEMORY_ID)
    for m in memories:
        print(f"  {m}")

    # ── Visit 2: new session, same customer ──
    print("\n" + "█"*50)
    print("VISIT 2 — New session, same customer")
    print("█"*50)
    session_2 = str(uuid.uuid4())

    # No order ID given — memory bridges the gap
    ask_agent("Did my order arrive yet?", session_2, CUSTOMER_MEMORY_ID)
    ask_agent("What is the return policy if it didn't?", session_2, CUSTOMER_MEMORY_ID)
