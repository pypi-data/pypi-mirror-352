"""
Toolkit for managing Microsoft Graph tokens using Azure Entra ID and Key Vault.
"""
from azure.identity.aio import AzureCliCredential, ManagedIdentityCredential
from azure.keyvault.secrets.aio import SecretClient
from recall_space_agents.toolkits.ms_graph_token.schema_mappings import schema_mappings
from agent_builder.builders.tool_builder import ToolBuilder
import aiohttp
import urllib.parse
import hashlib
import os

class MsGraphTokenToolkit:
    def __init__(self, keyvault_url, client_id, tenant_id, client_secret, redirect_uri, scope=None):
        """
        Initialize the Microsoft Graph Token Toolkit.
        
        Args:
            keyvault_url (str): Azure Key Vault URL for storing tokens
            client_id (str): Azure Entra ID application client ID
            tenant_id (str): Azure Entra ID tenant ID
            client_secret (str): Azure Entra ID application client secret
            redirect_uri (str): OAuth2 redirect URI
            scope (list, optional): List of Microsoft Graph API scopes. Defaults to ["User.Read"]
        """
        self.keyvault_url = keyvault_url
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.scope = scope if scope is not None else ["User.Read"]
        self.schema_mappings = schema_mappings

        # Initialize Azure credentials based on environment
        if os.environ.get("AZURE_LOCAL_DEBUG") == "1":
            print("using AzureCliCredential")
            self.credential = AzureCliCredential()
        else:
            print("using ManagedIdentityCredential")
            self.credential = ManagedIdentityCredential()
        
        # Initialize async Key Vault client
        self.key_vault_client = SecretClient(vault_url=keyvault_url, credential=self.credential)

    async def _get_refresh_token(self, email):
        """
        Get the refresh token from KeyVault asynchronously.
        
        Args:
            email (str): Email address of the user
        """
        refresh_token_name = hashlib.sha256(f"{email}-refresh-token".encode('utf-8')).hexdigest()
        secret = await self.key_vault_client.get_secret(refresh_token_name)
        return secret.value

    def get_scope(self):
        """
        Get the current scope configuration.
        
        Returns:
            list: List of configured Microsoft Graph API scopes
        """
        return self.scope

    async def avalidate_if_email_token_exist(self, email):
        """
        Validate if a refresh token exists in Key Vault for the given email.
        
        Args:
            email (str): Email address to validate token existence for
            
        Returns:
            dict: A dictionary containing:
                - exists (bool): Whether the token exists
                - email (str): The email address checked
        """
        try:
            refresh_token_name = hashlib.sha256(f"{email}-refresh-token".encode('utf-8')).hexdigest()
            await self.key_vault_client.get_secret(refresh_token_name)
            return {"exists": True, "email": email, "scope": self.scope}
        except Exception as e:
            # If the secret is not found or any other error occurs
            return {"exists": False, "email": email}

    async def _generate_new_access_token_from_refresh(self, email):
        """
        Generate a new access token using the stored refresh token asynchronously.
        
        Args:
            email (str): Email address of the user
        """
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": await self._get_refresh_token(email),
            "scope": " ".join(self.scope),
            "redirect_uri": self.redirect_uri,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(token_url, data=data) as resp:
                resp.raise_for_status()
                return await resp.json()

    async def _generate_consent_link(self, email):
        """
        Generate the initial consent link for user authorization asynchronously.
        
        Args:
            email (str): Email address of the user
        """
        base_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        query_params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": self.redirect_uri,
            "response_mode": "query",
            "scope": " ".join(self.scope),
            "state": email,
            "prompt": "consent"
        }
        return f"{base_url}?{urllib.parse.urlencode(query_params)}"

    async def aget_refresh_token(self, email):
        """
        Get the refresh token from KeyVault asynchronously.
        
        Args:
            email (str): Email address of the user
        """
        value = await self._get_refresh_token(email)
        return {"refresh_token": value}

    async def agenerate_new_access_token(self, email):
        """
        Generate a new access token using the stored refresh token asynchronously.
        
        Args:
            email (str): Email address of the user
            
        Returns:
            dict: Either the token response from Microsoft Graph API or an error dictionary
                 containing the error message and a hint to generate a new consent link
        """
        try:
            value = await self._generate_new_access_token_from_refresh(email)
            return value
        except Exception as e:
            error_message = str(e)
            return {
                "error": error_message,
                "hint": f"consider generating a new consent link for email: {email}"
            }

    async def agenerate_link_for_consent(self, email):
        """
        Generate a consent link for user authorization asynchronously.
        
        Args:
            email (str): Email address of the user
        """
        value = await self._generate_consent_link(email)
        return {"consent_link": value}

    def get_tools(self):
        """
        Retrieve a list of tools mapped to the methods in the toolkit.
        Use it to bind tools to agents.

        Returns:
            list: A list of ToolBuilder objects, each representing a
            method in the toolkit.
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