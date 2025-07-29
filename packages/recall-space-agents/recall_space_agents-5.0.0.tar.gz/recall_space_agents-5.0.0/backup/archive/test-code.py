from typing import TypedDict
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from psycopg import AsyncConnection

class State(TypedDict):
   """The graph state."""
   some_text: str

def human_node(state: State):
   value = interrupt(
      # Any JSON serializable value to surface to the human.
      # For example, a question or a piece of text or a set of keys in the state
      {
         "text_to_revise": state["some_text"]
      }
   )
   return {
      # Update the state with the human's input
      "some_text": value
   }


# Build the graph
graph_builder = StateGraph(State)
# Add the human-node to the graph
graph_builder.add_node("human_node", human_node)
graph_builder.add_edge(START, "human_node")


connection_kwargs = {
    "autocommit": True,
    "prepare_threshold": 0,
}

conn_string = "postgresql://recall-space:pleaseletmein@localhost:5432/demo-db"


async def main():
    async with await AsyncConnection.connect(conn_string, **connection_kwargs) as conn:
        checkpointer = AsyncPostgresSaver(conn)
        # checkpointer = AsyncPostgresSaver(pool)
        graph = graph_builder.compile(
        checkpointer=checkpointer
        )

        # Pass a thread ID to the graph to run it.
        thread_config = {"configurable": {"thread_id": '4'}}

        res = await graph.ainvoke({"some_text": "Original text"}, config=thread_config)
    return res

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())