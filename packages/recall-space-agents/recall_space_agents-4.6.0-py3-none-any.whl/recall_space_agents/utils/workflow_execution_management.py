"""
Module for managing workflow execution with asynchronous PostgreSQL checkpoints.
"""

from textwrap import dedent
from typing import TypedDict

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler
import logging
import json


class WorkflowExecutionManagement:
    """Class to manage workflows with asynchronous PostgreSQL checkpoints."""

    class WorkflowRunName(TypedDict):
        """TypedDict representing the workflow run name."""

        run_name: str

    def __init__(
        self,
        db_connection_string: str,
        message_enqueuer: AzureQueueHandler = None
    ):
        """Initialize the WorkflowExecutionManagement.

        Args:
            db_connection_string (str): Database connection string.
            message_enqueuer (AzureQueueHandler, optional): Message enqueuer instance. Defaults to None.
        """
        self.db_connection_string = db_connection_string
        self.message_enqueuer = message_enqueuer
        self.connection_kwargs = {
            "autocommit": True,
            "prepare_threshold": 0,
        }

    async def run_workflow(
        self,
        graph_builder,
        state: dict,
        llm,
        workflow_name: str,
        thread_id: str = None
    ):
        """Run a workflow and return the response.

        Args:
            graph_builder: The graph builder object.
            state (dict): The initial state.
            llm: The language model to use.
            workflow_name (str): The name of the workflow.
            thread_id (str): Thread of the run. If it is not provided
            it will be generated for you.

        Returns:
            The response from invoking the compiled graph.
        """
        async with AsyncConnectionPool(
            conninfo=self.db_connection_string,
            max_size=5,
            kwargs=self.connection_kwargs,
        ) as pool:
            checkpointer = AsyncPostgresSaver(pool)
            # Uncomment the line below if running for the first time to setup the checkpointer.
            await checkpointer.setup()

            compile_graph = graph_builder.compile(checkpointer=checkpointer)

            if thread_id is None:
                thread_generation_prompt = dedent(f"""
                Please create a meaningful, human readable name for the run of
                the following workflow:
                workflow name:
                ```
                {workflow_name}
                ```

                workflow inputs:
                ```
                {state}
                ```
                """)
                response = await llm.with_structured_output(
                    self.WorkflowRunName
                ).ainvoke(thread_generation_prompt)
                thread_id = response.get("run_name")

            config = {"configurable": {"thread_id": thread_id}}
            state["thread_id"] = thread_id
            if self.message_enqueuer is not None:
                response = await self.astream_with_queue_workflow(
                    self.message_enqueuer,
                    compile_graph=compile_graph,
                    state=state,
                    config=config
                )
            else:
                response = await compile_graph.ainvoke(input=state, config=config)
            return response

    async def resume_workflow(
        self,
        thread_id: str,
        graph_builder,
        resume_state: dict,
    ):
        """Resume a workflow and return the response.

        Args:
            thread_id (str): The ID of the thread to resume.
            graph_builder: The graph builder object.
            resume_state (dict): The state to resume with.

        Returns:
            The response from invoking the compiled graph.
        """
        async with AsyncConnectionPool(
            conninfo=self.db_connection_string,
            max_size=5,
            kwargs=self.connection_kwargs,
        ) as pool:
            checkpointer = AsyncPostgresSaver(pool)
            compile_graph = graph_builder.compile(checkpointer=checkpointer)
            config = {"configurable": {"thread_id": thread_id}}
            await compile_graph.aupdate_state(config=config, values=resume_state)

            response = await compile_graph.ainvoke(None, config=config)
            try:
                # After workflow execution, remove data from the checkpoint tables
                async with pool.connection() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute(
                            "DELETE FROM checkpoint_blobs WHERE thread_id = %s;",
                            (thread_id,)
                        )
                        await cur.execute(
                            "DELETE FROM checkpoint_writes WHERE thread_id = %s;",
                            (thread_id,)
                        )
                        await cur.execute(
                            "DELETE FROM checkpoints WHERE thread_id = %s;",
                            (thread_id,)
                        )
            except:
                logging.error("Failed to remove threads from database.")
            return response

    @staticmethod
    async def astream_with_queue_workflow(
        message_enqueuer,
        compile_graph,
        state,
        config=None,
        stream_mode="updates",
        subgraphs=True
    ):
        """Enqueue workflow execution and process responses.

        Args:
            message_enqueuer: The message enqueuer to use for sending messages.
            compile_graph: The compiled graph to execute.
            state: The initial state for the workflow.
            config: Configuration parameters for the workflow execution.
            stream_mode (str, optional): The stream mode to use. Defaults to "updates".
            subgraphs (bool, optional): Flag indicating whether to process subgraphs. Defaults to True.

        Returns:
            The final response from the workflow execution.
        """
        logging.info("Enqueuing workflow...")
        async for response in compile_graph.astream(
            state,
            stream_mode=stream_mode,
            subgraphs=subgraphs,
            config=config
        ):
            logging.info(str(response))

            node_name = None

            if isinstance(response, tuple) and len(response) == 2:
                first_part, second_part = response

                if isinstance(first_part, dict):
                    node_name = list(first_part.keys())[0]
                elif isinstance(second_part, dict):
                    node_name = list(second_part.keys())[0]
            elif isinstance(response, dict):
                node_name = list(response.keys())[0]

            if node_name:
                message_data = json.dumps({"status": "completed", "node": node_name})
                await message_enqueuer.enqueue_message(message_data)
        return response