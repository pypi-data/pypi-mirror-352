import json
import aiohttp
from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from agent_builder.builders.tool_builder import ToolBuilder
from recall_space_agents.toolkits.ms_bot.schema_mappings import schema_mappings

class MSBotToolKit:
    def __init__(self, credentials, bot_id: str, direct_line_secret: str):
        """
        Initialize the MSBotToolKit.

        Args:
            credentials: The credentials for Microsoft Graph API.
            bot_id (str): The bot's application (client) ID.
            direct_line_secret (str): The Direct Line secret from Azure Bot Service.
        """
        self.credentials = credentials
        self.bot_id = bot_id
        self.direct_line_secret = direct_line_secret
        self.direct_line_url = "https://directline.botframework.com/v3/directline"
        self.required_scopes = ["User.Read.All"]
        self.ms_graph_client = GraphServiceClient(
            credentials, scopes=self.required_scopes
        )
        self.schema_mappings = schema_mappings

    async def afind_user_id_by_name(self, user_name: str) -> str:
        """
        Asynchronously find a user ID by their display name.

        Args:
            user_name (str): The display name of the user.

        Returns:
            str: The user ID if found, or an error message.
        """
        try:
            query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
                filter=f"displayName eq '{user_name}'",
                select=["id", "displayName"],
                top=1,
            )
            request_config = RequestConfiguration(
                query_parameters=query_params,
            )
            users = await self.ms_graph_client.users.get(
                request_configuration=request_config
            )

            if users and users.value and len(users.value) > 0:
                user = users.value[0]
                return user.id
            else:
                return f"User '{user_name}' not found."
        except Exception as e:
            return f"An error occurred while searching for user '{user_name}': {e}"

    async def send_message_to_bot(self, message_json: str) -> str:
        """
        Asynchronously send a message to the bot using the Direct Line channel.

        Args:
            message_json (str): A JSON string containing the message to send.

        Returns:
            str: Message indicating success or failure.
        """
        try:
            # Start a conversation
            headers = {
                "Authorization": f"Bearer {self.direct_line_secret}",
                "Content-Type": "application/json",
            }
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.direct_line_url}/conversations", headers=headers
                ) as response:
                    if response.status == 201:
                        conversation = await response.json()
                        conversation_id = conversation["conversationId"]
                    else:
                        return f"Failed to start conversation with bot. Status code: {response.status}"

                # Send the message
                data = {
                    "type": "message",
                    "from": {
                        "id": "MSBotToolKit_user",
                        "name": "MSBotToolKit",
                    },
                    "text": message_json,
                }
                async with session.post(
                    f"{self.direct_line_url}/conversations/{conversation_id}/activities",
                    headers=headers,
                    json=data,
                ) as response:
                    if response.status in (200, 201):
                        return "Message sent to bot successfully."
                    else:
                        return f"Failed to send message to bot. Status code: {response.status}"
        except Exception as e:
            return f"An error occurred while sending message to bot: {e}"

    async def asend_team_message_by_name(
        self,  to_recipient_by_name: str, message: str,
    ) -> str:
        """
        Asynchronously send a message to a Teams user identified by display name.

        Args:
            message (str): The message content to send.
            to_recipient_by_name (str): The display name of the recipient.

        Returns:
            str: Message indicating success or failure.
        """
        user_id = await self.afind_user_id_by_name(to_recipient_by_name)
        if user_id.startswith("An error occurred") or user_id.startswith("User '"):
            # Return the error message from 'find_user_id_by_name'
            return user_id

        # Build the JSON string
        message_payload = {
            "user_id": user_id,
            "message": message,
            "to_recipient_by_name":to_recipient_by_name,
            "target_channel":"msteams"
        }
        message_json = json.dumps(message_payload)

        # Send the message to the bot
        result = await self.send_message_to_bot(message_json)
        return result
    

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.

        Returns:
            list: A list of ToolBuilder objects, each representing a method in the toolkit.
        """
        tools = []
        for each_method_key, each_method_value in self.schema_mappings.items():
            tool_builder = ToolBuilder()
            tool_builder.set_name(name=each_method_key)
            tool_builder.set_function(eval(f"self.{each_method_key}"))
            tool_builder.set_coroutine(eval(f"self.{each_method_key}"))
            tool_builder.set_description(description=each_method_value["description"])
            tool_builder.set_schema(schema=each_method_value["input_schema"])
            tool_builder = tool_builder.build()
            tools.append(tool_builder)
        return tools