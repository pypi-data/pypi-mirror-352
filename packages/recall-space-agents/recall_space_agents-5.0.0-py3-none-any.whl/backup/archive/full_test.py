from azure.identity import UsernamePasswordCredential
from typing import Literal
from typing import TypedDict
from langgraph.types import Command, interrupt
from recall_space_agents.hierarchical_agents.realized_workers.email_manager import EmailManager
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import TodoManager
from recall_space_agents.hierarchical_agents.realized_workers.site_manager import SiteManager
import os
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, START, StateGraph, MessagesState
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
from recall_space_agents.hierarchical_agents.application_graph import ApplicationGraph
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

DB_URI = "postgresql://recall-space:pleaseletmein@localhost:5432/demo-db?sslmode=disable"

credentials = UsernamePasswordCredential(
    client_id="c302dbd2-79f1-4c14-8164-2f064c2bb80d", 
    authority="https://login.microsoftonline.com/", 
    tenant_id="83b9af06-3811-437a-b341-6f6545ba840d",
    username="lisa.ai@recall.space",
    password="n._qNYZu^Y3Zy%_")

# Initialize LLM (Large Language Model)
llm = AzureChatOpenAI(
        base_url="https://recallspaceopenai.openai.azure.com/openai/deployments/gpt-4o/",
        api_key="ba50533a6aa8479bafc414fa3854dacf",
        api_version="2024-08-01-preview",
        temperature=0
    )

######
## Application 1
# workers
email_manager = EmailManager(llm=llm, credentials=credentials)
todo_manager = TodoManager(llm=llm, credentials=credentials)
site_manager = SiteManager(llm=llm, credentials=credentials)

workers = [email_manager, todo_manager, site_manager]

# supervisor
supervisor = Supervisor(llm=llm, workers=workers)



######
## Application 2
# workers
workers = [email_manager]

# supervisor
supervisor = Supervisor(llm=llm, workers=workers)



class VIPUserAppState(MessagesState):
    request_human_input: bool
    user_name: str

def the_human_input(state)-> Command[Literal["paid_application", "free_application"]]:
    next_node = "free_application"
    messages = [("user", 
        f"""
        tell a joke about lawyers
        """)]
    is_routed_to_paied_app = interrupt(
        # Any JSON serializable value to surface to the human.
        # For example, a question or a piece of text or a set of keys in the state
       {
          "text_to_revise": "some staff"
       }
    )
    print("------")
    print(is_routed_to_paied_app)
    if 'paid' in is_routed_to_paied_app:
        next_node = "paid_application"
        messages = [("user",f"""
        tell a joke about doctors
        """)]
    return Command(
                goto=next_node,
                update={"messages": messages},
            )

# Application 2
free_application  = ApplicationGraph(supervisor)
# Application 1
paid_application  = ApplicationGraph(supervisor)
builder = StateGraph(VIPUserAppState)
builder.add_edge(START, "the_human_input")
builder.add_node("the_human_input", the_human_input)
builder.add_node("paid_application", paid_application.get_compiled_graph())
builder.add_node("free_application", free_application.get_compiled_graph())
builder.add_edge("paid_application", END)
builder.add_edge("free_application", END)

connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}


async def main():
    async with AsyncConnectionPool(
        # Example configuration
        conninfo=DB_URI,
        max_size=20,
        kwargs=connection_kwargs,
    ) as pool:
        checkpointer = AsyncPostgresSaver(pool)

        # NOTE: you need to call .setup() the first time you're using your checkpointer
        #await checkpointer.setup()

        demo_app = builder.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": "24"}}
        # first time:
        res = await demo_app.ainvoke(
            {"messages": [("human", "do your work")],
            "user_name": "Gari Ciodaro"}, config
        )
        # second time
        # Resume the graph with the human's input
        #res = await demo_app.ainvoke(Command(resume='it is paid'), config=config)

        #checkpoint = await checkpointer.aget(config)
    return res

if __name__ == '__main__':
    import asyncio
    import sys
    if sys.platform.startswith('win'):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r=asyncio.run(main())
    print(r)