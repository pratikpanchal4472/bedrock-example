"""
Phase 1 — Foundation Models
Bedrock Converse API: the raw foundation before agents or tools.
"""

import boto3
import json

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

MODEL_ID = "amazon.nova-lite-v1:0"


def ask_nova(user_message: str) -> str:
    """
    Call Nova Lite using the Converse API.
    Converse is Bedrock's unified interface — same code works for
    Claude, Llama, Titan, Mistral. Just swap MODEL_ID.
    """
    response = bedrock.converse(
        modelId=MODEL_ID,
        system=[
            {
                "text": """You are a helpful order assistant for ShopEasy,
                an Indian e-commerce platform. You help customers track orders,
                understand delivery timelines, and resolve issues.
                Always be concise and friendly."""
            }
        ],
        messages=[
            {
                "role": "user",
                "content": [{"text": user_message}]
            }
        ]
    )

    # Log token usage — watch this grow as you add tools and KB in later phases
    print(json.dumps(response["usage"], indent=2))

    return response["output"]["message"]["content"][0]["text"]


if __name__ == "__main__":
    # Test 1: order lookup — LLM has no tools, will hallucinate or refuse
    print("=== Test 1: Order lookup ===")
    print(ask_nova("Where is my order #12345?"))

    print()

    # Test 2: policy question — LLM invents policy, no KB yet
    print("=== Test 2: Return policy ===")
    print(ask_nova("What is your return policy?"))
