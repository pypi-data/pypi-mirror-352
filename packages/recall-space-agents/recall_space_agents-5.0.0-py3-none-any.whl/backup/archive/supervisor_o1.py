"""
Supervisor module that orchestrates tasks among workers to fulfill user requests.

This module defines the Supervisor class, which is responsible for coordinating
a team of workers to complete a user's job. It can generate a plan, distribute
tasks to workers, and ensure the completion of the job.
"""

from textwrap import dedent
from typing import List, TypedDict

from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import AzureChatOpenAI
from langgraph.graph import END, MessagesState
from langgraph.types import Command

from recall_space_agents.hierarchical_agents.worker import Worker
import os


class Router(TypedDict):
    """Represents the next worker and the task to assign.

    Attributes:
        next (str): The name of the next worker to execute the task.
                    If no more workers are needed, this should be 'FINISH'.
        task (str): The specific task or instruction to give to the worker.
    """

    next: str
    task: str


class Supervisor:
    """Supervisor class that manages workers to fulfill a user's request.

    The Supervisor coordinates a group of workers to complete a job.
    It can generate a plan to divide the job into tasks, assign tasks to
    individual workers, and manage the workflow until completion.

    Attributes:
        agent_name (str): The name of the supervisor agent.
        llm (AzureChatOpenAI): The language model used for processing.
        workers (dict): A dictionary mapping worker names to Worker instances.
        workers_names (List[str]): A list of worker agent names.
        workers_info (str): Information about the workers and their skills.
        plan (str): The plan to fulfill the user's job.
        system_prompt (str): The system prompt used for generating responses.
        require_plan (bool): Indicates whether a plan is required.
    """

    def __init__(
        self, llm: AzureChatOpenAI, workers: List[Worker], require_plan: bool = False
    ):
        """Initialize the Supervisor.

        Args:
            llm (AzureChatOpenAI): The language model for processing messages.
            workers (List[Worker]): A list of Worker instances.
            require_plan (bool, optional): Whether to generate a plan. Defaults to False.
        """
        self.agent_name = "Supervisor"
        self.llm = llm
        self.llm_o1 = AzureChatOpenAI(
            base_url=os.getenv("AZURE_GPT4O_BASE_URL").replace("gpt-4o","o1-preview"),
            api_key=os.getenv("AZURE_GPT4O_KEY"),
            api_version="2024-08-01-preview",
            temperature=1,
            streaming=False,
        )
        self.workers = {worker.agent_name: worker for worker in workers}
        self.workers_names = [worker.agent_name for worker in workers]
        self.workers_info = ""
        for each_worker in workers:
            self.workers_info += dedent(
                f"""
            ```
            worker's name:
                {each_worker.agent_name}
            worker's skills:
                {each_worker.extracted_tool_description}
            ```
            """
            )

        self.plan = ""
        self.system_prompt = ""
        self.require_plan = require_plan

    async def generate_plan(self, state: MessagesState):
        """Generate a plan to fulfill the user's job.

        The plan divides the job into tasks that can be executed by individual workers.

        Args:
            state (MessagesState): The current state of messages.

        Returns:
            str: The generated plan content.
        """
        plan_prompt = dedent(
            f"""
        Create a plan to fulfill the user's job. It is recommended to
        divide the job into tasks that can be executed by individual workers.
        {self.workers_info}
        """
        )
        temp_plan_messages = [
            {"role": "system", "content": plan_prompt},
        ] + state["messages"]
        plan = await self.llm.ainvoke(temp_plan_messages)
        self.plan = plan.content
        return self.plan

    async def generate_system_prompt(self, state: MessagesState):
        """Generate the system prompt based on the plan and workers.

        Args:
            state (MessagesState): The current state of messages.

        Returns:
            str: The generated system prompt.
        """
        #if self.require_plan is True and self.plan == "":
        if False:
            plan = await self.generate_plan(state)
            self.system_prompt = dedent(
                f"""
            Your task is to ensure that the workers complete the user's
            request according to the assigned plan.

            # Plan
            ```
            {plan}
            ```

            # Workers
            ```
            {self.workers_names}
            ```
            Specify which worker should act next, and provide specific
            instructions to them. Keep in mind that each worker only
            knows what you tell them in each command; they are not aware
            of the conversation history.
            When all tasks are completed, respond with FINISH.
            """
            )

        #if self.require_plan is False and self.system_prompt == "":
        else:
            self.system_prompt = dedent(
                f"""
            Your task is to ensure that the workers complete the user's
            request.
            {self.workers_info}

            Specify which worker should act next and provide them with specific tasks, 
            one step at a time, sequentially. As the worker completes each task, the 
            conversation will progress. Only when the initial request 
            (the first message in the conversation) is fully addressed should you say 'Finish'.

            Keep in mind that each worker only knows the information provided in 
            each individual command; they are not aware of the conversation history.

            When all tasks are completed, respond with 'FINISH'.
            """
            )
        return self.system_prompt

    async def supervisor_node(self, state: MessagesState) -> Command[str]:
        """Process the supervisor node in the conversation graph.

        Determines the next worker to act and the task to assign.

        Args:
            state (MessagesState): The current state of messages.

        Returns:
            Command[str]: The command indicating the next worker and updates.
        """
        if self.system_prompt == "":
            await self.generate_system_prompt(state)
        messages = [
            {"role": "assistant", "content": self.system_prompt},
        ] + state["messages"]
        o1_prompt = f"""
        ```
        {self.system_prompt}
        ```

        + This is the conversation so far:
        {state["messages"]}


        """
        response_o1 = self.llm_o1.invoke(messages).content
        print("o1:", response_o1)
        if "FINISH" in response_o1:
            goto = "FINISH"
            task = ""
        else:
            message_temp =  dedent(f"""
            Your job is to extract worker's name who his task out the content.
            ## These are the possible workers:
            ```
            {self.workers_names}
            ```

            ## This is the content:
            ```
            {response_o1}
            ```
            """)
            response = self.llm.with_structured_output(Router).invoke(message_temp)
            goto = response["next"]
            task = response["task"]
            print("4o supervisor:", response)

        if goto == "FINISH":
            goto = END
        elif goto not in self.workers_names:
            # Handle invalid worker name
            raise ValueError(f"Unknown worker: {goto}")
        return Command(
            goto=goto,
            update={"messages": [HumanMessage(content=task, name=self.agent_name)]},
        )