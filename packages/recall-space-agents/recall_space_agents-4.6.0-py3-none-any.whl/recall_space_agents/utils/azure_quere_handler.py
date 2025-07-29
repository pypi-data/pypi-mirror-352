"""
Azure Queue Storage Message Enqueuer Module

This module provides the `AzureQueueHandler` class, which allows for asynchronous
sending and receiving of messages to and from an Azure Queue Storage queue.
"""
import base64 
import json
import asyncio
import logging

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.queue.aio import QueueClient


class AzureQueueHandler:
    """
    Handler for Azure Queue Storage operations.
    """

    def __init__(self, storage_connection_string: str, queue_name: str):
        """
        Initialize the AzureQueueHandler with connection string and queue name.
        """
        self.storage_connection_string = storage_connection_string
        self.queue_name = queue_name

    async def enqueue_message(
        self,
        message: str,
        time_to_live: int = 300,
        delay: int = 1
    ) -> bool:
        """
        Send a message to Azure Queue Storage asynchronously.

        Args:
            message (str): The message to send.
            time_to_live (int, optional): How long the message will remain in
                the queue. Defaults to 300 seconds.
            delay (int, optional): Delay to prevent messages appearing
                instantly. Defaults to 1 second.

        Returns:
            bool: True if the message was sent successfully, False otherwise.
        """
        success = False
        try:
            if not self.storage_connection_string:
                logging.error(
                    "Storage connection string is not set. Cannot send message to queue."
                )
            else:
                logging.info(f"Connecting to queue: {self.queue_name}")
                async with QueueClient.from_connection_string(
                    self.storage_connection_string,
                    self.queue_name
                ) as queue_client:
                    try:
                        logging.info(f"Sending message: {message}")
                        await queue_client.send_message(
                            message,
                            time_to_live=time_to_live
                        )
                        logging.info("Message successfully sent to queue.")
                        await asyncio.sleep(delay)  # Delay to prevent messages appearing instantly
                        success = True
                    except ResourceNotFoundError:
                        # The queue does not exist. Create it and retry.
                        logging.info(
                            f"Queue '{self.queue_name}' does not exist. Creating queue."
                        )
                        await queue_client.create_queue()
                        logging.info(f"Queue '{self.queue_name}' created.")
                        # Retry sending the message
                        await queue_client.send_message(
                            message,
                            time_to_live=time_to_live
                        )
                        logging.info("Message successfully sent to queue after creation.")
                        await asyncio.sleep(delay)
                        success = True
        except Exception as e:
            logging.error(f"Failed to send message to queue: {e}", exc_info=True)
        return success

    async def dequeue_message(self, visibility_timeout: int = 30, delete_message: bool= True):
        """
        Receive and delete a message from Azure Queue Storage asynchronously.

        Args:
            visibility_timeout (int, optional): The visibility timeout for
                the message. Defaults to 30 seconds.
            delete_message (bool, optional): whether reads removes the message from queue.

        Returns:
            str or None: The content of the message if received, None otherwise.
        """
        message_content = None
        try:
            if not self.storage_connection_string:
                logging.error(
                    "Storage connection string is not set. Cannot receive messages from queue."
                )
            else:
                logging.info(f"Connecting to queue: {self.queue_name}")
                async with QueueClient.from_connection_string(
                    self.storage_connection_string,
                    self.queue_name
                ) as queue_client:
                    try:
                        message = await queue_client.receive_message(
                            visibility_timeout=visibility_timeout
                        )
                        if message:
                            try:
                                message_content = json.loads(base64.b64decode(message.content).decode("utf-8"))
                            except:
                                message_content = json.loads(message.content)
                            logging.info(f"Received message: {message_content}")
                            if delete_message is True:
                                await queue_client.delete_message(message)
                                logging.info("Message successfully deleted from queue.")
                        else:
                            logging.info("No messages in queue.")
                    except ResourceNotFoundError:
                        logging.error(
                            f"Queue '{self.queue_name}' does not exist. Cannot receive messages."
                        )
        except Exception as e:
            logging.error(f"Failed to receive message from queue: {e}", exc_info=True)
        return message_content