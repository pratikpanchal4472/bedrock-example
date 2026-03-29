"""
Phase 3 — Lambda handler for Bedrock Agent Action Groups
Deploy this to AWS Lambda (Python 3.12).
"""

import json
from datetime import datetime, timedelta

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


def get_order_status(order_id: str) -> dict:
    order = MOCK_ORDERS.get(order_id)
    if not order:
        return {"error": f"Order {order_id} not found"}
    return order


def get_delivery_estimate(tracking_id: str) -> dict:
    delivery = MOCK_DELIVERIES.get(tracking_id)
    if not delivery:
        return {"error": f"Tracking ID {tracking_id} not found"}
    return delivery


def lambda_handler(event, context):
    """
    Bedrock Agents invokes this Lambda with a specific event structure.
    Parameters come as a list of {name, type, value} dicts.
    Response must follow the exact Bedrock Agents format below.
    """
    print(f"Event: {json.dumps(event, indent=2)}")

    action_group = event.get("actionGroup")
    function     = event.get("function")
    parameters   = event.get("parameters", [])

    # Convert parameter list to simple dict
    params = {p["name"]: p["value"] for p in parameters}

    if function == "get_order_status":
        result = get_order_status(params.get("order_id", ""))
    elif function == "get_delivery_estimate":
        result = get_delivery_estimate(params.get("tracking_id", ""))
    else:
        result = {"error": f"Unknown function: {function}"}

    # Bedrock Agents requires this exact response structure
    return {
        "response": {
            "actionGroup": action_group,
            "function": function,
            "functionResponse": {
                "responseBody": {
                    "TEXT": {
                        "body": json.dumps(result)
                    }
                }
            }
        }
    }
