"""
This module provides a toolkit for interacting with a PostgreSQL database to manage chats and messages.
It includes functionalities to create chats, save messages, delete chats, and retrieve chats and messages.

Classes:
    ChatDbToolKit: A toolkit class for managing chats using psycopg client.
"""

import uuid
from datetime import datetime
from typing import Optional, List
from agent_builder.builders.tool_builder import ToolBuilder
import psycopg
from psycopg_pool import AsyncConnectionPool

from recall_space_agents.toolkits.chat_db.schema_mappings import schema_mappings  # Adjust the import path accordingly


class ChatDbToolKit:
    """
    A toolkit class for managing chats using psycopg client.

    This class uses the AsyncConnectionPool context manager in each method, as per your request.

    Methods:
        asave_chat: Asynchronously save a chat record to the database.
        asave_message: Asynchronously save a message to a chat in the database.
        adelete_chat_by_id: Asynchronously delete a chat and its messages by chat ID.
        aget_chats_by_user_id: Asynchronously retrieve chats for a specific user.
        aget_chat_by_id: Asynchronously retrieve a chat by its ID.
        aget_messages_by_chat_id: Asynchronously retrieve messages for a specific chat.
        adelete_messages_after_timestamp: Asynchronously delete messages after a certain timestamp in a chat.
        get_tools: Retrieve a list of tools mapped to the methods in the toolkit.
    """

    def __init__(self, connecion_string : str):
        """
        Initialize the ChatDbToolKit with a PostgreSQL connection string.

        Args:
            connecion_string  (str): The Data Source Name containing the connection parameters.
        """
        self.connecion_string  = connecion_string 
        self.schema_mappings = schema_mappings

    async def asave_chat(self, user_id: int, title: str, chat_id: Optional[str] = None) -> str:
        """
        Asynchronously save a new chat to the database.

        Args:
            user_id (int): The ID of the user creating the chat.
            title (str): The title of the chat.
            chat_id (Optional[str]): The chat ID. If not provided, a new UUID will be generated.

        Returns:
            str: The ID of the saved chat.
        """
        if not chat_id:
            chat_id = str(uuid.uuid4())
        query = """
            INSERT INTO chat (id, created_at, user_id, title)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
        """
        params = (chat_id, datetime.utcnow(), user_id, title)
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    result = await cur.fetchone()
                    return result[0]

    async def asave_message(self, chat_id: str, role: str, content: dict) -> str:
        """
        Asynchronously save a message to a chat.

        Args:
            chat_id (str): The ID of the chat.
            role (str): The role of the message sender (e.g., 'user', 'assistant').
            content (dict): The content of the message.

        Returns:
            str: The ID of the saved message.
        """
        message_id = str(uuid.uuid4())
        query = """
            INSERT INTO message (id, chat_id, role, content, created_at)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        params = (message_id, chat_id, role, psycopg.types.json.Json(content), datetime.utcnow())
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    result = await cur.fetchone()
                    return result[0]

    async def adelete_chat_by_id(self, chat_id: str) -> dict:
        """
        Asynchronously delete a chat and all its associated messages by chat ID.

        Args:
            chat_id (str): The ID of the chat to delete.

        Returns:
            dict: A status message indicating the result of the operation.
        """
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.transaction():
                    async with conn.cursor() as cur:
                        # Delete messages first
                        delete_messages_query = "DELETE FROM message WHERE chat_id = %s;"
                        await cur.execute(delete_messages_query, (chat_id,))
                        # Delete the chat
                        delete_chat_query = "DELETE FROM chat WHERE id = %s;"
                        await cur.execute(delete_chat_query, (chat_id,))
        return {"status": f"Chat {chat_id} and its messages have been deleted."}

    async def aget_chats_by_user_id(self, user_id: int) -> List[dict]:
        """
        Asynchronously retrieve chats for a specific user.

        Args:
            user_id (int): The ID of the user.

        Returns:
            List[dict]: A list of chats belonging to the user.
        """
        query = """
            SELECT id, created_at, title FROM chat
            WHERE user_id = %s
            ORDER BY created_at DESC;
        """
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (user_id,))
                    rows = await cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in rows]

    async def aget_chat_by_id(self, chat_id: str) -> Optional[dict]:
        """
        Asynchronously retrieve a chat by its ID.

        Args:
            chat_id (str): The ID of the chat.

        Returns:
            Optional[dict]: The chat details if found, else None.
        """
        query = "SELECT * FROM chat WHERE id = %s LIMIT 1;"
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (chat_id,))
                    row = await cur.fetchone()
                    if row:
                        columns = [desc[0] for desc in cur.description]
                        return dict(zip(columns, row))
                    else:
                        return None

    async def aget_messages_by_chat_id(self, chat_id: str) -> List[dict]:
        """
        Asynchronously retrieve messages for a specific chat.

        Args:
            chat_id (str): The ID of the chat.

        Returns:
            List[dict]: A list of messages in the chat.
        """
        query = """
            SELECT id, chat_id, role, content, created_at FROM message
            WHERE chat_id = %s
            ORDER BY created_at ASC;
        """
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (chat_id,))
                    rows = await cur.fetchall()
                    columns = [desc[0] for desc in cur.description]
                    messages = [dict(zip(columns, row)) for row in rows]
                    return messages

    async def adelete_messages_after_timestamp(self, chat_id: str, timestamp: datetime) -> dict:
        """
        Asynchronously delete messages after a certain timestamp in a chat.

        Args:
            chat_id (str): The ID of the chat.
            timestamp (datetime): The cutoff timestamp.

        Returns:
            dict: A status message indicating the number of messages deleted.
        """
        query = """
            DELETE FROM message
            WHERE chat_id = %s AND created_at >= %s
            RETURNING id;
        """
        async with AsyncConnectionPool(conninfo=self.connecion_string ) as pool:
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, (chat_id, timestamp))
                    deleted_ids = await cur.fetchall()
                    return {"status": f"Deleted {len(deleted_ids)} messages after {timestamp}."}

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list: A list of ToolBuilder objects, each representing a method in the toolkit.
        """
        tools = []
        for method_name, method_info in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=method_name)
            method = getattr(self, method_name)
            tool_builder.set_function(method)
            tool_builder.set_coroutine(method)
            tool_builder.set_description(description=method_info["description"])
            tool_builder.set_schema(schema=method_info["input_schema"])
            tools.append(tool_builder.build())
        return tools