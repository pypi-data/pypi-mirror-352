import os
from dotenv import load_dotenv
from azure.identity import UsernamePasswordCredential
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import (
    EmailManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import (
    TodoManager,
)
from recall_space_agents.hierarchical_agents.realized_workers.site_manager import SiteManager
from recall_space_agents.hierarchical_agents.realized_workers.site_workbook_manager import SiteWorkbookManager
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
from langchain_openai import AzureChatOpenAI
from zoneinfo import ZoneInfo
from datetime import datetime
from langsmith import traceable
from langgraph.graph import END, START, StateGraph, MessagesState
from langgraph.types import Command, interrupt
from typing import Literal
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
import uuid
from recall_space_agents.toolkits.chat_db.chat_db import ChatDbToolKit
import pytz


# ========================== CONSTANT CONFIGURATION ==========================
load_dotenv()


# Authenticate using Azure UsernamePasswordCredential. This provides credentials
# required for interacting with protected user configured resources (e.g., TODO list, emails).
# This allows the system to already interact with the user's system
credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"),
    authority=os.getenv("MS_AUTHORITY"),
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD"),
)

# Initialize the language model interface with specified parameters.
# This model is used by workers for NLP tasks like understanding instructions or generating text.
llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
    temperature=0,  # Deterministic output.
)


# ========================== WORKER SETUP ==========================
# Define workers here. Each worker encapsulates functionality for a specific task.
email_manager = EmailManager(llm=llm, credentials=credentials)
todo_manager = TodoManager(llm=llm, credentials=credentials)
site_manager = SiteManager(llm=llm, credentials=credentials)
site_workbook_manager = SiteWorkbookManager(llm=llm, credentials=credentials)

# Configure appropriate workers for the tasks
workers = [ email_manager, ]

# ========================== SUPERVISOR & APPLICATION GRAPH ==========================
# Supervisor orchestrates the workflow and plans tasks before execution.
supervisor = Supervisor(llm=llm, workers=workers, require_plan=False)

# ApplicationGraph defines the hierarchical execution logic for the workflow.
supervisor_app = ApplicationGraph(supervisor).get_compiled_graph()

# When using interrupt you need to connector to the chat database
chat_db_connection_string = os.getenv("CHAT_DB_ENTRA_ID_CONNECTION_STRING")
chat_db_tool_kit = ChatDbToolKit(chat_db_connection_string)

# extent MessagesState.
# MessagesState contains 'messages' keyword
class SampleAppState(MessagesState):
    request_human_input_flag: bool = False
    user_name: str = ""
    # This key is always required. When user input is needed, the user 
    # specified by this key will receive the request for input via chat session.
    thread_id: str = ""
    accountable_user_id: str = ""
    reviewer_response: str = ""


async def request_human_input(state)-> Command[Literal["delegate_to_supervisor_app", "delegate_to_email_manager_directly"]]:
    next_node = "delegate_to_email_manager_directly"
    messages = [("user", 
        f"""
        Check if there are unread emails from '{state['user_name']}'
        if there are:
            - Summarize it's content.
        else:
            - Do nothing.
        """)]
    if state["request_human_input_flag"] is True:        
        the_human_input = interrupt(
        # Any JSON serializable value to surface to the human.
        # For example, a question or a piece of text or a set of keys in the state
        {
            "reviewer_response": "who should perform the job?  supervisor or the email manager"
        }
        )
        if "supervisor" in the_human_input["reviewer_response"].lower():
            next_node = "delegate_to_supervisor_app"
    return Command(
                goto=next_node,
                update={"messages": messages},
            )

builder = StateGraph(SampleAppState)
builder.add_edge(START, "request_human_input")
builder.add_node("request_human_input", request_human_input)
builder.add_node("delegate_to_supervisor_app", supervisor_app)
builder.add_node("delegate_to_email_manager_directly", email_manager.agent)
builder.add_edge("delegate_to_supervisor_app", END)
builder.add_edge("delegate_to_email_manager_directly", END)


connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

workflow_graph =  builder.compile()

# ========================== WORKFLOW EXECUTION TEMPLATE ==========================
@traceable(name="human_in_the_loop_test", project_name="human_in_the_loop_test")
# NOTE: data is only included when the trigger is Http Type.
# The data would consist of input params defined by input_signature.
async def main(data: dict):
    """
    Main entry point for executing the workflow.

    Parameters:
        data (dict): Input parameters needed to drive the workflow.
    """
    # to keep track of human input
    request_human_input_flag= data.get("request_human_input_flag") or False
    user_name= data.get("user_name") or ""
    thread_id = data.get("thread_id") or ""
    accountable_user_id = data.get("accountable_user_id") or ""
    reviewer_response = data.get("reviewer_response") or ""
    
    # For this example, no messages are provided at init time.
    # They have the format [("user", "hi, start your work."),]
    messages =[]
    state = {
        "request_human_input_flag": request_human_input_flag,
        "user_name" : user_name,
        "thread_id": thread_id,
        "accountable_user_id": accountable_user_id,
        "reviewer_response": reviewer_response,
        "messages": messages
    }
    async with AsyncConnectionPool(
        # Example configuration
        conninfo=f"{os.getenv('CHAT_DB_ENTRA_ID_CONNECTION_STRING')}-checkpointers",
        max_size=5,
        kwargs=connection_kwargs,
        password=
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)
        # NOTE: you need to call .setup() the first time you're using your checkpointer
        await checkpointer.setup()
        workflow_graph = builder.compile(checkpointer=checkpointer)
        if thread_id=="" and state["request_human_input_flag"] is True:
            # new execution. Assigning thread_id
            thread_id = f"human_in_the_loop_test:{str(uuid.uuid4())}"
            config = {"configurable": {"thread_id": thread_id}}
            response = await workflow_graph.ainvoke(input=state, config=config)
            # Since user input is required, and we are the first execution,
            # let's emit a message to alert the accountable_user that
            # his input is required.
            german_timezone = pytz.timezone('Europe/Berlin')
            now_in_germany = datetime.now(german_timezone)
            now_in_germany_str = now_in_germany.strftime('%Y-%m-%d %H:%M:%S %Z%z')
            
            # create a chat for user to reply
            new_chat_id = await chat_db_tool_kit.asave_chat(
                user_id=state['accountable_user_id'], 
                title=f"Call to action {now_in_germany_str}"
                )
            await chat_db_tool_kit.asave_message(
                chat_id=new_chat_id, 
                role="assistant", 
                content=f"""
                Hi, who should continue the workflow—the Supervisor or the 
                email manager? Please note that the Supervisor can generate 
                an execution plan. To resume the execution use 
                thread_id: {thread_id}""")
        else:
            config = {"configurable": {"thread_id": thread_id}}
            response=await workflow_graph.ainvoke(
                Command(resume={"reviewer_response": reviewer_response}), 
                config=config
            )
            # clean execution
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(
                        "DELETE FROM public.checkpoint_blobs WHERE thread_id =  %s;",
                        (thread_id,)
                    )
                    await cur.execute(
                        "DELETE FROM public.checkpoint_writes WHERE thread_id = %s;",
                        (thread_id,)
                    )
                    await cur.execute(
                        "DELETE FROM public.checkpoints WHERE thread_id = %s;",
                        (thread_id,)
                    )
        # Return the response for logging or further processing.
        return response