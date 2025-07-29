"""
This Python script defines a workflow for sending emails, incorporating a review 
and approval process when the recipient is the production manager. It leverages Azure 
services, language models, and custom toolkits to manage email sending, state management, 
and workflow execution.

Purpose: Automate the process of sending emails, ensuring that any email intended 
for the production manager is reviewed before sending.

Key Components:

+ Recipient Verification: Checks if the email recipient is the production manager.
+ Review Request: If the recipient is the production manager and no reviewer response is 
present, the workflow sends a review request to the reviewer and pauses execution.
+ Language Model Decision: Upon receiving a reviewer response, an Azure OpenAI language 
model evaluates whether to proceed or end the workflow.
+ Email Sending: Sends the email to the intended recipient after passing the review 
process or if no review is needed.
+ Workflow Execution Management: Handles workflow execution, pausing, resumption, and 
state management using Azure services and PostgreSQL.
"""

import json
import logging
import os

from azure.identity import UsernamePasswordCredential
from azure.storage.queue.aio import QueueClient
from langchain_openai import AzureChatOpenAI
from langgraph.errors import NodeInterrupt
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langsmith import traceable
from typing_extensions import TypedDict

from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from recall_space_agents.utils.workflow_execution_management import \
    WorkflowExecutionManagement

# Should be the same that endpoint on the azure function app
workflow_flow_name = "send an email"

class SendEmailWorkflow(TypedDict):
    subject: str = ""
    body_html: str = ""
    to_recipient_by_name: str = ""
    thread_id: str = ""
    reviewer_response: str = ""
    production_manager: str = ""
    reviewers_email: str = ""


credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD"),
)
llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
    temperature=0,  # Deterministic output.
)

email_toolkit = MSEmailToolKit(credentials=credentials)

# Azure Storage connection string and queue name
AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
QUEUE_NAME = "pending-workflows-dev"

# Workaround retry cause by node interrupt.
flag_verification_email = False

async def verify_recipient(state):
    if state["production_manager"].lower() in state["to_recipient_by_name"].lower():
        if state["reviewer_response"] == "":
            review_message = f"""
            <div class="container">
                <div class="header">
                    <h1>Review Request</h1>
                </div>
                <div class="content">
                    <p>Dear Reviewer,</p>
                    <p>I am about to send the following message to the
                    production manager <b>{state["production_manager"]}</b> 
                    and would appreciate your feedback.</p>
                    <h2>Email Subject: {state["subject"]}</h2>
                    <h2>Email Content: </h2>
                        <hr>
                        {state["body_html"]}
                        <hr>
                    <p>Best regards,<br><strong>Lisa AI</strong></p>
                </div>
                <div class="footer">
                    Request review for workflow run: {state["thread_id"]}
                </div>
            </div>
            """

            enqueu_message_dict = {
                "thread_id":state["thread_id"],
                "workflow_flow_name": workflow_flow_name,
                "editable_state":{
                    "subject":state["subject"],
                    "body_html":state["body_html"],
                    "to_recipient_by_name":state["to_recipient_by_name"],
                    "reviewer_response": state["reviewer_response"]
                }
            }
            enqueu_message= json.dumps(enqueu_message_dict)


            global flag_verification_email
            if flag_verification_email is False:
                async with QueueClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING, QUEUE_NAME) as queue_client:
                    logging.info(f"enqueue message: {enqueu_message}")
                    await queue_client.send_message(enqueu_message, time_to_live=300)
                await email_toolkit.asend_email(
                    subject="Please review this email.",
                    body_html=review_message,
                    to_recipient=state["reviewers_email"])
            flag_verification_email = True
            raise NodeInterrupt(
                "Emails to the Production Manager must be reviewed."
            )
        else:
            response = await llm.ainvoke(f"""
            please review the following statement:
            ```
            {state["reviewer_response"]}
            ```

            Respond with "END" if it appears that the process in question 
            should not continue. Otherwise, reply with "CONTINUE".
            """)
            if "END" in response.content:
                return Command(goto=END) 
    return Command(goto="Send email") 

async def send_email(state): 
    await email_toolkit.asend_email_by_name(
            subject=state["subject"],
            body_html=state["body_html"],
            to_recipient_by_name=state["to_recipient_by_name"])
    return Command(goto=END)


builder = StateGraph(SendEmailWorkflow)

builder.add_node(
    "Verify recipient", verify_recipient
)
builder.add_node(
    "Send email", send_email
)

builder.add_edge(START, "Verify recipient")
builder.add_edge("Verify recipient", END)
builder.add_edge("Verify recipient", "Send email")
builder.add_edge("Send email", END)


workflow_graph = builder.compile()


@traceable(name="Send an Email", project_name="Send an Email")
async def main(data: dict):
    input_state ={
        "subject": data.get("subject", ""),
        "body_html": data.get("body_html"),
        "to_recipient_by_name": data.get("to_recipient_by_name", ""),
        "thread_id":data.get("thread_id", ""),
        "reviewer_response":data.get("reviewer_response", ""),
        "production_manager":data.get("production_manager", "Titus Lottig"),
        "reviewers_email": data.get("reviewers_email", "info@recall.space"),
    }
    
    # Utility from recall space agents.
    # Handles the run and resume of workflows with dynamic theread_id generation
    # checkpointer management with postgresql and 
    workflow_execution_management = WorkflowExecutionManagement(
        db_connection_string=os.getenv("CHAT_DB_URL"))
    
    # Normal execution
    if input_state["thread_id"] == "":
        run_response= await workflow_execution_management.run_workflow(
            graph_builder=builder,
            state=input_state,
            llm=llm,
            workflow_name=workflow_flow_name)

    # Resume execution, thread_id is required.
    if input_state["thread_id"] != "":
        run_response= await workflow_execution_management.resume_workflow(
            thread_id=input_state["thread_id"],
            graph_builder=builder,
            resume_state=input_state
        )

    # Return the response for logging or further processing.
    return run_response