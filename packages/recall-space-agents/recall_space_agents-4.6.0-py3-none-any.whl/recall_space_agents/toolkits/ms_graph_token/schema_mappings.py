"""
Schema mappings for MsGraphTokenToolkit methods.
"""
from pydantic import BaseModel, Field

class EmailInputSchema(BaseModel):
    email: str = Field(..., description="Email address of the user")

schema_mappings = {
    # "aget_refresh_token": {
    #     "description": "Retrieve the refresh token from Key Vault for the specified email.",
    #     "input_schema": EmailInputSchema,
    # },
    # "agenerate_new_access_token": {
    #     "description": "Generate a new access token using the stored refresh token for the specified email.",
    #     "input_schema": EmailInputSchema,
    # },
    "agenerate_link_for_consent": {
        "description": "Generate a consent link for user authorization for the specified email.",
        "input_schema": EmailInputSchema,
    },
    "avalidate_if_email_token_exist": {
        "description": "Check if a refresh microsoft graph token exists in Key Vault for the specified email.",
        "input_schema": EmailInputSchema,
    }
}
