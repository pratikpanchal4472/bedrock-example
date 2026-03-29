"""
Phase 2 — ReAct Loop + Tools (Manual)
The ReAct loop implemented manually — this is what Bedrock Agents does for you in Phase 3.
"""

import boto3
import json
import re
from datetime import datetime, timedelta

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "amazon.nova-lite-v1:0"

# ─────────────────────────────────────────────
# MOCK DATABASE
# In production this would be a real DB call
# ─────────────────────────────────────────────

MOCK_ORDERS = {
    "12345": {
        "order_id": "12345",
        "status": "shipped",
        "tracking_id": "ABC99",
        "carrier": "BlueDart",
        "last_location": "Ahmedabad sorting facility",
        "items": ["Nike Air Max", "Cotton T-Shirt x2"]
    },
    "99999": {
        "order_id": "99999",
        "status": "processing",
        "tracking_id": None,
        "carrier": None,
        "last_location": None,
        "items": ["iPhone Case"]
    }
}

MOCK_DELIVERIES = {
    "ABC99": {
        "tracking_id": "ABC99",
        "estimated_delivery": (datetime.now() + timedelta(days=2)).strftime("%A, %d %B %Y"),
        "current_city": "Ahmedabad",
        "destination_city": "Mumbai"
    }
}


# ─────────────────────────────────────────────
# TOOL FUNCTIONS
# ─────────────────────────────────────────────

def get_order_status(order_id: str) -> dict:
    """Look up real order data from mock DB."""
    order = MOCK_ORDERS.get(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    return order


def get_delivery_estimate(tracking_id: str) -> dict:
    """Get delivery estimate for a tracking ID."""
    delivery = MOCK_DELIVERIES.get(tracking_id)
    if not delivery:
        return {"error": f"Tracking ID {tracking_id} not found"}
    return delivery


# ─────────────────────────────────────────────
# TOOL DEFINITIONS
# These descriptions are injected into the LLM prompt as text.
# Nova Lite reads them and decides when and how to call each tool.
# ─────────────────────────────────────────────

TOOLS = [
    {
        "toolSpec": {
            "name": "get_order_status",
            "description": """Use this tool when the customer asks about
            the status, location, or details of a specific order.
            Requires an order ID. Always call this before answering
            any order-specific question — never guess order status.""",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "The order ID to look up e.g. 12345"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        }
    },
    {
        "toolSpec": {
            "name": "get_delivery_estimate",
            "description": """Use this tool when the customer asks about
            delivery date or whether an order will arrive by a specific day.
            Requires a tracking ID — get this from get_order_status first.""",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "tracking_id": {
                            "type": "string",
                            "description": "The tracking ID e.g. ABC99"
                        }
                    },
                    "required": ["tracking_id"]
                }
            }
        }
    }
]


# ─────────────────────────────────────────────
# TOOL DISPATCHER
# Routes tool call requests from Nova Lite to the right function.
# Notice: every new tool needs a new elif — this is the scaling problem
# that Bedrock Agents solves in Phase 3.
# ─────────────────────────────────────────────

def dispatch_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name == "get_order_status":
        result = get_order_status(tool_input["order_id"])
    elif tool_name == "get_delivery_estimate":
        result = get_delivery_estimate(tool_input["tracking_id"])
    else:
        result = {"error": f"Unknown tool: {tool_name}"}
    return json.dumps(result)


def strip_thinking(text: str) -> str:
    """Remove <thinking>...</thinking> blocks from Nova Lite output."""
    return re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL).strip()


# ─────────────────────────────────────────────
# REACT LOOP
# This is the core loop you are writing manually.
# In Phase 3, Bedrock Agents manages this entirely.
# ─────────────────────────────────────────────

def run_agent(user_message: str) -> str:
    print(f"\n{'='*50}")
    print(f"User: {user_message}")
    print(f"{'='*50}")

    messages = [
        {
            "role": "user",
            "content": [{"text": user_message}]
        }
    ]

    system = [
        {
            "text": """You are a helpful order assistant for ShopEasy.
            Always use tools to look up real order data.
            Never guess or make up order statuses or delivery dates.
            After receiving tool results, always provide a complete
            helpful answer to the customer."""
        }
    ]

    loop_count = 0
    while True:
        loop_count += 1
        print(f"\n--- Loop {loop_count}: Calling Nova Lite ---")

        response = bedrock.converse(
            modelId=MODEL_ID,
            system=system,
            messages=messages,
            toolConfig={"tools": TOOLS}
        )

        response_message = response["output"]["message"]
        stop_reason = response["stopReason"]
        print(f"Stop reason: {stop_reason}")

        messages.append(response_message)

        # ── CASE 1: Nova Lite wants to call a tool ──
        if stop_reason == "tool_use":
            tool_results = []

            for block in response_message["content"]:
                if "toolUse" in block:
                    tool_name   = block["toolUse"]["name"]
                    tool_input  = block["toolUse"]["input"]
                    tool_use_id = block["toolUse"]["toolUseId"]

                    print(f"Tool called: {tool_name}")
                    print(f"Tool input:  {json.dumps(tool_input, indent=2)}")

                    tool_result = dispatch_tool(tool_name, tool_input)
                    print(f"Tool result: {tool_result}")

                    tool_results.append({
                        "toolResult": {
                            "toolUseId": tool_use_id,
                            "content": [{"text": tool_result}],
                            "status": "success"
                        }
                    })

            # Send ALL tool results back in ONE user message
            messages.append({
                "role": "user",
                "content": tool_results
            })

        # ── CASE 2: Nova Lite has a final answer ──
        elif stop_reason == "end_turn":
            for block in response_message["content"]:
                if "text" in block and block["text"].strip():
                    final_answer = strip_thinking(block["text"])
                    print(f"\nFinal answer: {final_answer}")
                    return final_answer

        else:
            print(f"Unexpected stop reason: {stop_reason}")
            break


if __name__ == "__main__":
    # Test 1: Simple order lookup — 2 loops (status + delivery)
    run_agent("Where is my order #12345?")

    # Test 2: Multi-step — needs tool chaining to answer Friday question
    run_agent("Will my order #12345 arrive before Friday?")

    # Test 3: Order not in DB — graceful error handling
    run_agent("What's the status of order #00000?")
