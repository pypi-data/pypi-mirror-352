"""
This Python script defines a workflow for sending Teams messages, incorporating a review 
and approval process when the recipient is the production manager. It leverages Azure 
services, language models, and custom toolkits to manage Teams message sending, state management, 
and workflow execution.

Purpose: Automate the process of sending Teams messages, ensuring that any message intended 
for the production manager is reviewed before sending.

Key Components:

+ Recipient Verification: Checks if the message recipient is the production manager.
+ Review Request: If the recipient is the production manager and no reviewer response is 
present, the workflow sends a review request to the reviewer and pauses execution.
+ Language Model Decision: Upon receiving a reviewer response, an Azure OpenAI language 
model evaluates whether to proceed or end the workflow.
+ Teams Message Sending: Sends the message to the intended recipient after passing the review 
process or if no review is needed.
+ Workflow Execution Management: Handles workflow execution, pausing, resumption, and 
state management using Azure services and PostgreSQL.
"""

import json
import logging
import os

from azure.identity import UsernamePasswordCredential
from langchain_openai import AzureChatOpenAI
from langgraph.errors import NodeInterrupt
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command
from langsmith import traceable
from typing_extensions import TypedDict

from recall_space_agents.toolkits.ms_bot.ms_bot import MSBotToolKit
from recall_space_agents.toolkits.ms_email.ms_email import MSEmailToolKit
from recall_space_agents.utils.azure_quere_handler import MessageEnqueuer
from recall_space_agents.utils.workflow_execution_management import \
    WorkflowExecutionManagement

# Should be the same as the endpoint on the Azure Function App
workflow_flow_name = "Send a teams message"

class SendTeamsMessageWorkflow(TypedDict):
    message: str
    to_recipient_by_name: str
    thread_id: str
    reviewer_response: str
    production_manager: str
    reviewers_email: str

# Handles the run and resume of workflows with dynamic thread_id generation
# Checkpointer management with PostgreSQL and message enqueueing

# Enqueuer for human-in-the-loop pending workflows
pending_workflows_enqueuer = MessageEnqueuer(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name=os.getenv("PENDING_WORKFLOWS_QUEUE")
)

# Enqueuer for node step execution messages to Azure Functions queue
azure_functions_enqueuer = MessageEnqueuer(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="azure-functions-queue"
)

# Workflow execution management with message enqueuer
workflow_execution_management = WorkflowExecutionManagement(
    db_connection_string=os.getenv("CHECKPOINTERS_DB_URL"),
    message_enqueuer=azure_functions_enqueuer
)

credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD")
)

llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
    temperature=0  # Deterministic output
)

email_toolkit = MSEmailToolKit(credentials=credentials)

# Initialize the MSBotToolkit
bot_toolkit = MSBotToolKit(
    credentials=credentials,
    bot_id=os.getenv("BOT_ID"),
    direct_line_secret=os.getenv("DIRECT_LINE_SECRET")
)

# Workaround retry caused by node interrupt
flag_verification_message = False

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
                    production manager <b>{state["production_manager"]}</b> via
                    MS Teams and would appreciate your feedback.</p>
                    <h2>Message: </h2>
                        <hr>
                        {state["message"]}
                        <hr>
                    <p>Best regards,<br><strong>Lisa AI</strong></p>
                </div>
                <div class="footer">
                    Request review for workflow run: {state["thread_id"]}
                </div>
            </div>
            """

            enqueu_message_dict = {
                "thread_id": state["thread_id"],
                "workflow_flow_name": workflow_flow_name,
                "editable_state": {
                    "message": state["message"],
                    "to_recipient_by_name": state["to_recipient_by_name"],
                    "reviewer_response": state["reviewer_response"]
                }
            }
            enqueu_message = json.dumps(enqueu_message_dict)

            global flag_verification_message
            if flag_verification_message is False:
                logging.info(f"Enqueue message: {enqueu_message}")
                await pending_workflows_enqueuer.enqueue_message(
                    enqueu_message, time_to_live=600, delay=0
                )

                await email_toolkit.asend_email(
                    subject="Please review this email.",
                    body_html=review_message,
                    to_recipient=state["reviewers_email"])

                flag_verification_message = True

            raise NodeInterrupt(
                "Messages to the Production Manager must be reviewed."
            )
        else:
            response = await llm.ainvoke(f"""
            Please review the following statement:
            ```
            {state["reviewer_response"]}
            ```

            Respond with "END" if it appears that the process in question 
            should not continue. Otherwise, reply with "CONTINUE".
            """)
            if "END" in response.content:
                return Command(goto=END)
    return Command(goto="Send Teams message")

async def send_teams_message(state):
    result = await bot_toolkit.asend_team_message_by_name(
        message=state["message"],
        to_recipient_by_name=state["to_recipient_by_name"]
    )
    logging.info(f"Teams message send result: {result}")
    return Command(goto=END)

builder = StateGraph(SendTeamsMessageWorkflow)

builder.add_node(
    "Verify recipient", verify_recipient
)
builder.add_node(
    "Send Teams message", send_teams_message
)

builder.add_edge(START, "Verify recipient")
builder.add_edge("Verify recipient", END)
builder.add_edge("Verify recipient", "Send Teams message")
builder.add_edge("Send Teams message", END)

workflow_graph = builder.compile()

@traceable(name="Send a Teams Message", project_name="Send a Teams Message")
async def main(data: dict):
    input_state = {
        "message": data.get("message", ""),
        "to_recipient_by_name": data.get("to_recipient_by_name", ""),
        "thread_id": data.get("thread_id", ""),
        "reviewer_response": data.get("reviewer_response", ""),
        "production_manager":data.get("production_manager") or "Titus Lottig",
        "reviewers_email": data.get("reviewers_email") or "info@recall.space",
    }

    # Normal execution
    if input_state["thread_id"] == "":
        run_response = await workflow_execution_management.run_workflow(
            graph_builder=builder,
            state=input_state,
            llm=llm,
            workflow_name=workflow_flow_name
        )

    # Resume execution; thread_id is required
    if input_state["thread_id"] != "":
        run_response = await workflow_execution_management.resume_workflow(
            thread_id=input_state["thread_id"],
            graph_builder=builder,
            resume_state=input_state
        )

    # Return the response for logging or further processing
    return run_response