"""
This module defines the schema mappings for the Azure Queue Handler functionality,
including the input schemas for sending (enqueue) and receiving (dequeue) messages
from Azure Queue Storage. Transform function into tool.

"""

from pydantic import BaseModel, Field
from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.utils.azure_quere_handler import AzureQueueHandler

class EnqueueMessageInputSchema(BaseModel):
    """
    Schema for sending a message to Azure Queue.
    """
    message: str = Field(..., description="The message to enqueue.")
    time_to_live: int = Field(
        default=300,
        description="How long the message should remain in the queue (in seconds)."
    )
    delay: int = Field(
        default=1,
        description="Delay (in seconds) before the message becomes visible in the queue."
    )

class DequeueMessageInputSchema(BaseModel):
    """
    Schema for receiving and deleting a message from Azure Queue.
    """
    visibility_timeout: int = Field(
        default=2,
        description="The duration (in seconds) that the message is hidden from other clients."
    )
    delete_message: bool = Field(
        default=False,
        description="Indicates whether the message should be deleted from the queue after it is read. Set it to False unless the user explicitly requests its removal."
    )

schema_mappings = {
    "enqueue_message": {
        "description": "Send a message to Azure Queue Storage asynchronously.",
        "input_schema": EnqueueMessageInputSchema,
    },
    "dequeue_message": {
        "description": "Receive a message from Azure Queue Storage asynchronously.",
        "input_schema": DequeueMessageInputSchema,
    },
}



def get_azure_queue_handler_tool(storage_connection_string, queue_name):
    azure_queue_handler = AzureQueueHandler(
        storage_connection_string=storage_connection_string, 
        queue_name=queue_name)
    tools = []
    for each_method_key, each_method_value in schema_mappings.items():
        tool_builder = ToolBuilder()
        tool_builder.set_name(name=each_method_key)
        tool_builder.set_function(eval(f"azure_queue_handler.{each_method_key}"))
        tool_builder.set_coroutine(eval(f"azure_queue_handler.{each_method_key}"))
        tool_builder.set_description(description=each_method_value["description"])
        tool_builder.set_schema(schema=each_method_value["input_schema"])
        tool_builder = tool_builder.build()
        tools.append(tool_builder)
    return tools

