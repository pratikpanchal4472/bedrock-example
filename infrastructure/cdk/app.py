#!/usr/bin/env python3
"""
CDK Stack — ShopEasy Bedrock Agent Infrastructure
Deploys: S3 bucket for KB docs, IAM roles
Note: Bedrock Agent, Knowledge Base, and Guardrail are created
via console (see phase READMEs) as they require model access confirmation.
"""

import aws_cdk as cdk
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_iam as iam,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct


class ShopEasyBedrockStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # ─── S3 Bucket for Knowledge Base documents ────────────────────────
        kb_bucket = s3.Bucket(
            self, "KnowledgeBaseBucket",
            bucket_name=f"shopease-knowledge-base-{self.account}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            versioned=True,
        )

        # Upload policy document to S3
        s3deploy.BucketDeployment(
            self, "PolicyDocDeployment",
            sources=[s3deploy.Source.asset("../../knowledge_base_docs")],
            destination_bucket=kb_bucket,
        )

        # ─── Bedrock Agent Execution Role ──────────────────────────────────
        agent_role = iam.Role(
            self, "BedrockAgentRole",
            role_name="AmazonBedrockExecutionRoleForAgents-ShopEasy",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
        )

        # Allow agent to invoke any Bedrock model
        agent_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream",
                "bedrock:GetInferenceProfile",
                "bedrock:GetFoundationModel",
            ],
            resources=["*"],
        ))

        # Allow agent to invoke the Lambda function
        agent_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=["lambda:InvokeFunction"],
            resources=[f"arn:aws:lambda:{self.region}:{self.account}:function:shopease-order-tools*"],
        ))

        # Allow agent to retrieve from Knowledge Base
        agent_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:Retrieve",
                "bedrock:RetrieveAndGenerate",
            ],
            resources=["*"],
        ))

        # Allow agent to manage memory
        agent_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:GetAgentMemory",
                "bedrock:DeleteAgentMemory",
            ],
            resources=["*"],
        ))

        # Allow agent to read from S3 KB bucket
        kb_bucket.grant_read(agent_role)

        # ─── Bedrock KB Service Role ────────────────────────────────────────
        kb_role = iam.Role(
            self, "KnowledgeBaseRole",
            role_name="AmazonBedrockExecutionRoleForKnowledgeBase-ShopEasy",
            assumed_by=iam.ServicePrincipal("bedrock.amazonaws.com"),
        )

        kb_role.add_to_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "bedrock:InvokeModel",
            ],
            resources=["*"],
        ))

        kb_bucket.grant_read_write(kb_role)

        # ─── Outputs ────────────────────────────────────────────────────────
        CfnOutput(self, "KBBucketName",
            value=kb_bucket.bucket_name,
            description="Upload your policy documents here for the Knowledge Base"
        )

        CfnOutput(self, "AgentRoleArn",
            value=agent_role.role_arn,
            description="Use this role ARN when creating the Bedrock Agent in console"
        )

        CfnOutput(self, "KBRoleArn",
            value=kb_role.role_arn,
            description="Use this role ARN when creating the Knowledge Base in console"
        )


app = cdk.App()
ShopEasyBedrockStack(
    app, "ShopEasyBedrockStack",
    env=cdk.Environment(
        account=app.node.try_get_context("account"),
        region=app.node.try_get_context("region") or "us-east-1"
    )
)
app.synth()
