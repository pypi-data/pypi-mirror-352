import asyncio
import os

from azure.identity import UsernamePasswordCredential
from langchain_openai import AzureChatOpenAI

from recall_space_agents.hierarchical_agents.application_graph import \
    ApplicationGraph
from recall_space_agents.hierarchical_agents.realized_workers.todo_manager import \
    TodoManager
from recall_space_agents.hierarchical_agents.supervisor import Supervisor
import dotenv
dotenv.load_dotenv()

credentials = UsernamePasswordCredential(
    client_id=os.getenv("CLIENT_ID"), 
    authority="https://login.microsoftonline.com/", 
    tenant_id=os.getenv("TENANT_ID"),
    username=os.getenv("LISA_USER_NAME"),
    password=os.getenv("LISA_PASSWORD")
    )

llm = AzureChatOpenAI(
        base_url=os.getenv("AZURE_GPT4O_BASE_URL"),
        api_key=os.getenv("AZURE_GPT4O_KEY"),
        api_version=os.getenv("AZURE_GPT4O_API_VERSION"),
        temperature=0
    )
todo_manager = TodoManager(llm=llm, credentials=credentials)
workers = [todo_manager]
supervisor = Supervisor(llm=llm, workers=workers, require_plan=False)
demo_todo_app = ApplicationGraph(supervisor).get_compiled_graph()

# Step 6: Define the main async function.
async def main(data):
    # Define the initial state with instructions.
    state = {
        "messages": [
            """Create a TODO Item named 'a nice joke' and add to the body 
            a nice joke about any topic.
            Do it on the TODO list named 'General Tasks' 
            """,
        ],
    }

    # Execute the workflow graph asynchronously.
    response = await demo_todo_app.ainvoke(state)
    # Optional: process the response as needed.
    return response

# if __name__ == "__main__":
#     # Retrieve data if necessary, for now using an empty dictionary
#     data = {}
#     # Run the main async function
#     response = asyncio.run(main(data))
#     # Print the response
#     print(response)