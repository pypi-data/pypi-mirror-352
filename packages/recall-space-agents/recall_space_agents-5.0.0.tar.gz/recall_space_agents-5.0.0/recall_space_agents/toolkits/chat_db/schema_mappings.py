"""
This module defines the schema mappings for the ChatDbToolKit,
including the input schemas for various chat operations.

Classes:
    SaveChatInputSchema: Schema for saving a new chat.
    SaveMessageInputSchema: Schema for saving a message to a chat.
    DeleteChatByIdInputSchema: Schema for deleting a chat by ID.
    GetChatsByUserIdInputSchema: Schema for retrieving chats by user ID.
    GetChatByIdInputSchema: Schema for retrieving a chat by ID.
    GetMessagesByChatIdInputSchema: Schema for retrieving messages by chat ID.
    DeleteMessagesAfterTimestampInputSchema: Schema for deleting messages after a timestamp.

Variables:
    schema_mappings: A dictionary mapping method names to their descriptions and input schemas.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field
from textwrap import dedent

class SaveChatInputSchema(BaseModel):
    user_id: int = Field(..., description="The ID of the user creating the chat.")
    title: str = Field(..., description="The title of the chat.")
    chat_id: Optional[str] = Field(None, description="The ID of the chat. If not provided, a new UUID will be generated.")

class SaveMessageInputSchema(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat.")
    role: str = Field(..., description="The role of the message sender (e.g., 'user', 'assistant').")
    content: dict = Field(..., description="The content of the message.")

class DeleteChatByIdInputSchema(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat to delete.")

class GetChatsByUserIdInputSchema(BaseModel):
    user_id: int = Field(..., description="The ID of the user.")

class GetChatByIdInputSchema(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat.")

class GetMessagesByChatIdInputSchema(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat.")

class DeleteMessagesAfterTimestampInputSchema(BaseModel):
    chat_id: str = Field(..., description="The ID of the chat.")
    timestamp: datetime = Field(..., description="The cutoff timestamp in ISO format.")

schema_mappings = {
    "asave_chat": {
        "description": "Save a new chat to the database.",
        "input_schema": SaveChatInputSchema,
    },
    "asave_message": {
        "description": "Save a message to a chat.",
        "input_schema": SaveMessageInputSchema,
    },
    "adelete_chat_by_id": {
        "description": "Delete a chat and all its associated messages by chat ID.",
        "input_schema": DeleteChatByIdInputSchema,
    },
    "aget_chats_by_user_id": {
        "description": "Retrieve chats for a specific user.",
        "input_schema": GetChatsByUserIdInputSchema,
    },
    "aget_chat_by_id": {
        "description": "Retrieve a chat by its ID.",
        "input_schema": GetChatByIdInputSchema,
    },
    "aget_messages_by_chat_id": {
        "description": "Retrieve messages for a specific chat.",
        "input_schema": GetMessagesByChatIdInputSchema,
    },
    "adelete_messages_after_timestamp": {
        "description": "Delete messages after a certain timestamp in a chat.",
        "input_schema": DeleteMessagesAfterTimestampInputSchema,
    },
}