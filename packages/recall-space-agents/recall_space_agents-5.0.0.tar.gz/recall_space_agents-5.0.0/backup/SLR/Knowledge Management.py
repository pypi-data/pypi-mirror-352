from langsmith import traceable
from recall_space_agents.hierarchical_agents.realized_workers.ai_search_manager import AiSearchManager
from recall_space_agents.toolkits.ms_ai_search.ms_ai_search_toolkit import MSAISearchToolKit
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
import os
from langchain_openai import AzureChatOpenAI
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler
from recall_space_agents.utils.workflow_execution_management import (
    WorkflowExecutionManagement,
)
import logging
from textwrap import dedent
from dotenv import load_dotenv
from datetime import datetime, timezone
import json

load_dotenv()

workflow_flow_name = "Knowledge Management"

llm = AzureChatOpenAI(
    base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
    api_key=os.getenv("AZURE_GPT4O_KEY"),
    api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
)
azure_functions_enqueuer = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="azure-functions-queue",
)

workflows_log = AzureQueueHandler(
    storage_connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING"),
    queue_name="workflows-log-coq3pmfjgoh74",
)

ai_search_manager=AiSearchManager(
    llm=llm, 
    ai_search_base_url=os.getenv("AZURE_AI_SEARCH_BASE_URL"), 
    ai_search_api_key= os.getenv("AZURE_AI_SEARCH_API_KEY"), 
    index_name =  os.getenv("LISA_INDEX_NAME"),
    embeddings_url=os.getenv("EMBEDDINGS_BASE_URL"),
    embeddings_api_key=os.getenv("EMBEDDINGS_KEY")
    )

ms_ai_search_tool_kit =MSAISearchToolKit(
    ai_search_base_url=os.getenv("AZURE_AI_SEARCH_BASE_URL"), 
    ai_search_api_key= os.getenv("AZURE_AI_SEARCH_API_KEY"), 
    index_name =  os.getenv("LISA_INDEX_NAME"),
    embeddings_url=os.getenv("EMBEDDINGS_BASE_URL"),
    embeddings_api_key=os.getenv("EMBEDDINGS_KEY")
)

# Workers
workers = [ai_search_manager]

# Supervisor
supervisor = Supervisor(llm=llm, workers=workers, require_plan=False)

# Application graph
workflow_graph = ApplicationGraph(supervisor).get_compiled_graph()

memories_classification="""
# Memories can be categorized as follows:

1. Semantic Memory (use "Semantic" as the type):
   - Concepts (metadata: "Concept"): 
       Abstract ideas or general notions (e.g., "Democracy," "Gravity").
   - Facts (metadata: "Facts"): 
       Objectively verifiable information (e.g., "Water freezes at 0°C").
   - Principles (metadata: "Principles"): 
       Fundamental truths or rules (e.g., "Newton's Laws").

2. Episodic Memory (use "Episodic" as the type):
   - Events (metadata: "Events"): 
       Specific occurrences at particular times/places (e.g., "Attended AI Conference 2023").
   - Episodes (metadata: "Episodes"): 
       Sequences of events forming a narrative (e.g., "A week-long vacation in Japan").

3. Procedural Memory (use "Procedural" as the type):
   - Procedures (metadata: "Procedures"): 
       Step-by-step instructions to achieve results (e.g., "Steps to install software").
   - Strategy (metadata: "Strategy"): 
       Plans of action toward long-term goals (e.g., "Marketing strategy to increase brand awareness").
"""

@traceable(
    name="Knowledge Management",
    project_name="Knowledge Management",
)
async def main(data: dict):
    if len(data["content"].split(" "))>300:
        store_instruction = dedent(f"""
        # Store multiple memories from the following content:

        ## Content to analize
        ```
        {data["content"]}
        ```

        {memories_classification}
        """)
    else:
        store_instruction = dedent(f"""
        # Analize and store as a memory:

        ## Content to analize
        ```
        {data["content"]}
        ```

        {memories_classification}
        """)

    input_state = {
        "messages": [
            ("user", store_instruction)],
    }
    # 10 minutes the message will be on the logs queue.
    workflow_log_msg = {"workflow_name":workflow_flow_name, "input_state":input_state, "timestamp": datetime.now(timezone.utc).isoformat()}
    await workflows_log.enqueue_message(json.dumps(workflow_log_msg), time_to_live=600, delay=0)



    logging.error(f"input_state: {input_state}")
    response = await WorkflowExecutionManagement.astream_with_queue_workflow(
        message_enqueuer=azure_functions_enqueuer,
        compile_graph=workflow_graph,
        state=input_state,
        stream_mode="values",
    )

    try:
        # Update Type 'Core' memory, used to inject a summary
        # of the memories on lisa's prompt
        summary= await ms_ai_search_tool_kit.summarize_recent_memories(llm=llm)
        logging.error(f"updated memory summary: {summary}") 
    except Exception as error:
        logging.error(f"could not update core memory {str(error)}") 


    user_response = response[-1]["messages"][-1].content

    return user_response