"""
This module defines the schema mappings for the MSBotToolKit functionality,
including the input schemas for finding a user by name and starting a Teams chat with a user.

Classes:
    FindUserIdByNameInputSchema: Schema for finding a user ID by their display name.
    SendTeamMessageByNameInputSchema: Schema for Send a message to user in MS Teams using user's name.

Variables:
    schema_mappings: A dictionary mapping method names to their descriptions and input schemas.
"""

from typing import Optional
from pydantic import BaseModel, Field

class FindUserIdByNameInputSchema(BaseModel):
    user_name: str = Field(..., description="The display name of the user to search for.")


class SendTeamMessageByNameInputSchema(BaseModel):
    to_recipient_by_name: str = Field(..., description="The display name of the user.")
    message: str = Field(..., description="The message content to send to the user.")

schema_mappings = {
    "afind_user_id_by_name": {
        "description": "Find a user's Activate Directory ID by their display name.",
        "input_schema": FindUserIdByNameInputSchema,
    },
    "asend_team_message_by_name": {
        "description": "Send a message to user in MS Teams using user's name.",
        "input_schema": SendTeamMessageByNameInputSchema,
    },
}